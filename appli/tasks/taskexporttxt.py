# -*- coding: utf-8 -*-
import csv
import datetime
import logging
import os
import re
import shutil
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import psycopg2.extras
from flask import render_template, g, flash

import appli.project.sharedfilter as sharedfilter
from appli import db, app, database, PrintInCharte, gvp, gvg, DecodeEqualList, XSSEscape
from appli.database import GetAll
from appli.tasks.taskmanager import AsyncTask

# noinspection RegExpRedundantEscape
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ObjectsApi, ObjectSetQueryRsp


def normalize_filename(filename):
    return re.sub(R"[^a-zA-Z0-9 \.\-\(\)]", "_", str(filename))


# noinspection PyPep8Naming
def get_DOI_imgfile_name(objid, imgrank, taxofolder, originalfilename):
    if not taxofolder:
        taxofolder = "NoCategory"
    FileName = "images/{0}/{1}_{2}{3}".format(normalize_filename(taxofolder), objid, imgrank,
                                              Path(originalfilename).suffix.lower())
    return FileName


# noinspection RegExpRedundantEscape,PyPep8Naming
class TaskExportTxt(AsyncTask):
    # noinspection SpellCheckingInspection
    class Params(AsyncTask.Params):
        # noinspection PyPep8Naming
        def __init__(self, InitStr=None):
            self.steperrors = []
            super().__init__(InitStr)
            if InitStr is None:  # Valeurs par defaut ou vide pour init
                self.ProjectId = None
                self.what = None  # TSV, XML, IMG , Summary
                self.Details = None
                self.OutFile = None
                self.filtres = {}
                self.samplelist = ""
                self.commentsdata = ''
                self.objectdata = ''
                self.sampledata = ''
                self.processdata = ''
                self.acqdata = ''
                self.histodata = ''
                self.splitcsvby = ''
                self.usecomasepa = ''
                self.sumsubtotal = ''
                self.internalids = ''
                self.typeline = ''
                self.putfileonftparea = ''
                self.use_internal_image_name = ''
                self.exportimagesbak = ''
                self.exportimagesdoi = ''

    def __init__(self, task=None):
        self.pgcur = None
        super().__init__(task)
        if task is None:
            self.param = self.Params()
        else:
            self.param = self.Params(task.inputparam)

    def SPCommon(self):
        """ Executed before each step, i.e. in subprocess """
        logging.info("Execute SPCommon for Txt Export")
        self.pgcur = db.engine.raw_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)

    def CreateTSV(self, ExportMode, start_progress, end_progress):
        self.UpdateProgress(start_progress, "Start TSV export")
        progress_range = end_progress - start_progress
        Prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        image_export = ''
        if ExportMode in ('BAK', 'DOI'):
            self.param.sampledata = self.param.objectdata = self.param.processdata = self.param.acqdata = '1'
            self.param.commentsdata = self.param.histodata = self.param.internalids = ''
        if ExportMode == 'BAK':
            image_export = self.param.exportimagesbak
        if ExportMode == 'DOI':
            image_export = self.param.exportimagesdoi

        # Get a fast count of the maximum of what to do
        sql_count = "select sum(nbr) as cnt from projects_taxo_stat where projid=%(projid)s"
        self.pgcur.execute(sql_count, {'projid': int(self.param.ProjectId)})
        obj_count = next(self.pgcur)[0]

        sql1 = """select o.orig_id as object_id, o.latitude as object_lat, o.longitude as object_lon,
                         to_char(objdate,'YYYYMMDD') as object_date,
                         to_char(objtime,'HH24MISS') as object_time,
                         object_link, depth_min as object_depth_min, depth_max as object_depth_max,
                         case o.classif_qual 
                            when 'V' then 'validated' 
                            when 'P' then 'predicted' 
                            when 'D' then 'dubious' 
                            else o.classif_qual 
                         end object_annotation_status,                
                         uo1.name object_annotation_person_name, uo1.email object_annotation_person_email,
                         to_char(o.classif_when,'YYYYMMDD') object_annotation_date,
                         to_char(o.classif_when,'HH24MISS') object_annotation_time,                
                         to1.display_name as object_annotation_category 
                    """
        if ExportMode == 'BAK':
            sql1 += ",to1.id as object_annotation_category_id"

        if ExportMode != 'BAK':
            sql1 += """
                ,(WITH RECURSIVE rq(id,name,parent_id) 
                   as (select id, name, parent_id, 1 rang 
                         from taxonomy 
                        where id = o.classif_id
                       union
                       select t.id, t.name, t.parent_id, rang+1 rang 
                         from rq 
                         join taxonomy t on t.id = rq.parent_id)
                    select string_agg(name,'>') 
                      from (select name 
                              from rq 
                              order by rang desc) q) object_annotation_hierarchy """
        sql2 = """ from objects o
                left join taxonomy to1 on o.classif_id = to1.id
                left join taxonomy to1p on to1.parent_id = to1p.id
                left join users uo1 on o.classif_who = uo1.id
                left join taxonomy to2 on o.classif_auto_id = to2.id
                     join samples s on o.sampleid = s.sampleid """
        sql3 = " where o.projid=%(projid)s "
        params = {'projid': int(self.param.ProjectId)}
        original_col_name = {}  # Nom de colonneSQL => Nom de colonne permet de traiter le cas de %area
        if image_export == '1':
            sql1 += "\n,img.orig_file_name as img_file_name,img.imgrank img_rank"
            sql2 += "\nleft join images img on o.objid = img.objid " \
                    "                      and img.imgrank = (SELECT MIN(img2.imgrank) " \
                    "                                           FROM images img2 WHERE img2.objid = o.objid) "
        if image_export == 'A':  # Toutes les images
            sql1 += "\n,img.orig_file_name as img_file_name,img.imgrank img_rank"
            sql2 += "\nleft join images img on o.objid = img.objid "

        if self.param.samplelist != "":
            sql3 += " and s.orig_id= any(%(samplelist)s) "
            params['samplelist'] = self.param.samplelist.split(",")

        if self.param.commentsdata == '1':
            sql1 += "\n,complement_info"
        if self.param.objectdata == '1':
            sql1 += "\n"
            mapping = DecodeEqualList(Prj.mappingobj)
            for k, v in mapping.items():
                alias_sql = 'object_%s' % re.sub(R"[^a-zA-Z0-9\.\-µ]", "_", v)
                original_col_name[alias_sql] = 'object_%s' % v
                sql1 += ',o.%s as "%s" ' % (k, alias_sql)
        if self.param.sampledata == '1':
            sql1 += "\n,s.orig_id sample_id,s.dataportal_descriptor as sample_dataportal_descriptor "
            mapping = DecodeEqualList(Prj.mappingsample)
            for k, v in mapping.items():
                sql1 += ',s.%s as "sample_%s" ' % (k, re.sub(R"[^a-zA-Z0-9\.\-µ]", "_", v))
        if self.param.processdata == '1':
            sql1 += "\n,p.orig_id process_id"
            mapping = DecodeEqualList(Prj.mappingprocess)
            for k, v in mapping.items():
                sql1 += ',p.%s as "process_%s" ' % (k, re.sub(R"[^a-zA-Z0-9\.\-µ]", "_", v))
            sql2 += "      join process p on o.acquisid = p.processid "
        if self.param.acqdata == '1':
            sql1 += "\n,a.orig_id acq_id,a.instrument as acq_instrument"
            mapping = DecodeEqualList(Prj.mappingacq)
            for k, v in mapping.items():
                sql1 += ',a.%s as "acq_%s" ' % (k, re.sub(R"[^a-zA-Z0-9\.\-µ]", "_", v))
            sql2 += " join acquisitions a on o.acquisid = a.acquisid "
        if ExportMode == 'DOI':
            sql1 += "\n,o.objid"
        if self.param.internalids == '1':
            sql1 += """\n,o.objid, o.acquisid as acq_id_internal, o.acquisid as processid_internal, 
                    o.sampleid as sample_id_internal, o.classif_id, o.classif_who,
                    o.classif_auto_id, to2.name classif_auto_name, classif_auto_score, classif_auto_when,
                    o.random_value object_random_value, o.sunpos object_sunpos """
            if self.param.sampledata == '1':
                sql1 += "\n, s.latitude sample_lat, s.longitude sample_long "

        if self.param.histodata == '1':
            if self.param.samplelist != "":  # injection du filtre sur les echantillons dans les historique
                samplefilter = " join samples s on o.sampleid = s.sampleid and s.orig_id = any(%(samplelist)s) "
            else:
                samplefilter = ""
            sql1 += " , oh.classif_date histoclassif_date, classif_type histoclassif_type, " \
                    "to3.name histoclassif_name, oh.classif_qual histoclassif_qual,uo3.name histoclassif_who, " \
                    "classif_score histoclassif_score"
            sql2 += """ left join (select o.objid, classif_date, classif_type, och.classif_id, 
                                          och.classif_qual, och.classif_who, classif_score
                                     from objectsclassifhisto och
                                     join objects o on o.objid=och.objid and o.projid=1 {0}
                                   union all
                                   select o.objid, o.classif_when classif_date, 'C' classif_type, classif_id, 
                                          classif_qual, classif_who, NULL
                                     from objects o {0} where o.projid=1
                                  ) oh on o.objid=oh.objid
                        left join taxonomy to3 on oh.classif_id=to3.id
                        left join users uo3 on oh.classif_who=uo3.id
                    """.format(samplefilter)

        # sql3 += sharedfilter.GetSQLFilter(self.param.filtres, params, self.task.owner_id)

        # Use the API entry point for filtering
        with ApiClient(ObjectsApi, self.cookie) as api:
            res: ObjectSetQueryRsp = api.get_object_set_object_set_project_id_query_post(self.param.ProjectId,
                                                                                         self.param.filtres)
            sql3 += "and o.objid = any (%(objids)s) "
            params["objids"] = sorted(res.object_ids)

        splitfield = "object_id"  # cette valeur permet d'éviter des erreurs plus loin dans r[splitfield]
        if ExportMode == 'BAK':
            self.param.splitcsvby = "sample"
        elif ExportMode == 'DOI':
            self.param.splitcsvby = ""
        if self.param.splitcsvby == "sample":
            sql3 += " order by s.orig_id, o.objid "
            splitfield = "sample_id"
        elif self.param.splitcsvby == "taxo":
            sql1 += "\n,concat(to1p.name,'_',to1.name) taxo_parent_child "
            sql3 += " order by taxo_parent_child, o.objid "
            splitfield = "taxo_parent_child"
        else:
            sql3 += " order by s.orig_id, o.objid "  # tri par defaut
        if image_export != '':
            sql3 += ",img_rank"
        sql = sql1 + " " + sql2 + " " + sql3
        logging.info("Execute SQL : %s" % (sql,))
        logging.info("Params : %s" % (params,))
        self.pgcur.execute(sql, params)
        splitcsv = (self.param.splitcsvby != "")
        self.param.OutFile = "export_{0:d}_{1:s}.{2}".format(
            Prj.projid, datetime.datetime.now().strftime("%Y%m%d_%H%M"), "zip")

        zfile = zipfile.ZipFile(os.path.join(self.GetWorkingDir(), self.param.OutFile),
                                'w', allowZip64=True, compression=zipfile.ZIP_DEFLATED)
        if splitcsv:
            csvfilename = 'temp.tsv'
            prevvalue = "NotAssigned"
        else:
            csvfilename = self.param.OutFile.replace('.zip', '.tsv')
            prevvalue = self.param.OutFile.replace('.zip', '')
        fichier = os.path.join(self.GetWorkingDir(), csvfilename)
        csvfile = None
        wtr = None
        colnames = [desc[0] for desc in self.pgcur.description]
        coltypes = [desc[1] for desc in self.pgcur.description]
        # on lit le type de la colonne 2 alias latitude pour determiner le code du type double
        db_float_type = coltypes[2]
        nb_rows = 0
        for r in self.pgcur:
            if (csvfile is None and (not splitcsv)) or ((prevvalue != r[splitfield]) and splitcsv):
                self.close_csv_if_needed(csvfile, fichier, zfile, prevvalue, ExportMode)
                if splitcsv:
                    prevvalue = r[splitfield]
                logging.info("Creating file %s" % (fichier,))
                csvfile = open(fichier, 'w', encoding='latin_1')
                wtr = csv.writer(csvfile, delimiter='\t', quotechar='"', lineterminator='\n',
                                 quoting=csv.QUOTE_NONNUMERIC)
                wtr.writerow([original_col_name.get(c, c) for c in colnames])
                if ExportMode == 'BAK':
                    wtr.writerow(['[f]' if x == db_float_type else '[t]' for x in coltypes])
            # on supprime les CR des commentaires.
            if r.get('img_file_name', '') and ExportMode == 'DOI':  # les images sont dans des dossiers par taxo
                r['img_file_name'] = get_DOI_imgfile_name(r['objid'], r['img_rank'], r['object_annotation_category'],
                                                          r['img_file_name'])
            if self.param.commentsdata == '1' and r['complement_info']:
                r['complement_info'] = ' '.join(r['complement_info'].splitlines())
            if self.param.usecomasepa == '1':  # sur les decimaux on remplace . par ,
                for i, t in zip(range(1000), coltypes):
                    if t == db_float_type and r[i] is not None:
                        r[i] = str(r[i]).replace('.', ',')
            wtr.writerow(r)
            nb_rows += 1
            if nb_rows % 10000 == 0:
                msg = "Row %d of max %d" % (nb_rows, obj_count)
                logging.info(msg)
                self.UpdateProgress(start_progress + progress_range / obj_count * nb_rows, msg)
        self.close_csv_if_needed(csvfile, fichier, zfile, prevvalue, ExportMode)
        logging.info("Extracted %d rows", self.pgcur.rowcount)

    @staticmethod
    def close_csv_if_needed(csvfile, fichier, zfile, prevvalue, ExportMode):
        if csvfile:
            csvfile.close()
            if zfile:
                if ExportMode == 'BAK':
                    zfile.write(fichier, os.path.join(str(prevvalue), "ecotaxa_" + str(prevvalue) + ".tsv"))
                else:
                    zfile.write(fichier, "ecotaxa_" + str(prevvalue) + ".tsv")

    def CreateIMG(self, SplitImageBy, start_progress, end_progress):
        # tsvfile=self.param.OutFile
        self.UpdateProgress(start_progress, "Start Image export")
        progress_range = end_progress - start_progress
        _Prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        # self.param.OutFile= "exportimg_{0:d}_{1:s}.zip".format(Prj.projid,
        #                                                      datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        # fichier=os.path.join(self.GetWorkingDir(),self.param.OutFile)
        logging.info("Opening for appending file %s" % (self.param.OutFile,))
        # zfile=zipfile.ZipFile(fichier, 'w',allowZip64 = True,compression= zipfile.ZIP_DEFLATED)
        # zfile.write(tsvfile)
        zfile = zipfile.ZipFile(self.param.OutFile, 'a', allowZip64=True, compression=zipfile.ZIP_DEFLATED)

        sql = """select i.objid, i.file_name, i.orig_file_name, t.name, 
                        replace(t.display_name,'<','_') taxo_parent_child, imgrank,
                        s.orig_id sample_orig_id
                   from objects o 
                        join samples s on o.sampleid = s.sampleid
                   join images i on o.objid = i.objid
                   left join taxonomy t on o.classif_id = t.id
                   left join taxonomy to1p on t.parent_id = to1p.id
                  where o.projid=%(projid)s """
        params = {'projid': int(self.param.ProjectId)}
        if self.param.samplelist != "":
            sql += " and s.orig_id= any(%(samplelist)s) "
            params['samplelist'] = self.param.samplelist.split(",")

        # sql += sharedfilter.GetSQLFilter(self.param.filtres, params, self.task.owner_id)

        # Use the API entry point for filtering
        with ApiClient(ObjectsApi, self.cookie) as api:
            res: ObjectSetQueryRsp = api.get_object_set_object_set_project_id_query_post(self.param.ProjectId,
                                                                                         self.param.filtres)
            sql += "and o.objid = any (%(objids)s) "
            params["objids"] = sorted(res.object_ids)

        logging.info("Execute SQL : %s" % (sql,))
        logging.info("Params : %s" % (params,))
        self.pgcur.execute(sql, params)
        temp_img_file = os.path.join(self.GetWorkingDir(), "images.csv")
        # Write the resultset to a file in order to free cursor data #542
        nb_files_to_add = self.write_cursor_to_csv(temp_img_file)
        nb_files_added = 0
        vaultroot = Path("../../vault")
        with open(temp_img_file, "r") as temp_images_csv_fd:
            for r in csv.DictReader(temp_images_csv_fd, delimiter='\t', quotechar='"', lineterminator='\n'):
                img_file_path = vaultroot.joinpath(r["file_name"]).as_posix()
                if SplitImageBy == 'taxo':
                    path_in_zip = get_DOI_imgfile_name(r['objid'], r['imgrank'], r['taxo_parent_child'], r['file_name'])
                else:
                    path_in_zip = "{0}/{1}".format(r['sample_orig_id'], r['orig_file_name'])
                try:
                    zfile.write(img_file_path, arcname=path_in_zip)
                except FileNotFoundError:
                    pass
                nb_files_added += 1
                if nb_files_added % 1000 == 0:
                    msg = "Added %d files" % nb_files_added
                    logging.info(msg)
                    self.UpdateProgress(start_progress + progress_range / nb_files_to_add * nb_files_added, msg)

    # TODO: Invalid URL
    XMLNS = "http://typo.oceanomics.abims.sbr.fr/ecotaxa-export"
    XSI_LOC = "platform:/resource/typo-shared/src/main/resources/ecotaxa-export-1.1.xsd"

    def create_XML(self):
        self.UpdateProgress(1, "Start XML export")
        Prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()

        self.param.OutFile = "export_{0:d}_{1:s}.xml".format(Prj.projid,
                                                             datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        fichier = os.path.join(self.GetWorkingDir(), self.param.OutFile)
        logging.info("Creating file %s" % (fichier,))
        root = ET.Element('projects', {"xmlns": self.XMLNS,
                                       "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                       "xsi:schemaLocation": self.XMLNS + " " + self.XSI_LOC
                                       })

        project_elem = ET.SubElement(root, 'project', {'id': "ecotaxa:%d" % Prj.projid})
        projectdescription = ET.SubElement(project_elem, 'projectdescription')
        projectdescriptionname = ET.SubElement(projectdescription, 'name')
        projectdescriptionname.text = Prj.title
        ET.SubElement(projectdescription, 'link', {"url": "%sprj/%d" % (app.config['SERVERURL'], Prj.projid)})
        projectdescriptionmanagers = ET.SubElement(projectdescription, 'managers')
        projectdescriptionanno = ET.SubElement(projectdescription, 'contributors')
        for pm in Prj.projmembers:
            if pm.privilege == "Manage":
                m = ET.SubElement(projectdescriptionmanagers, 'manager')
            elif pm.privilege == "Annotate":
                m = ET.SubElement(projectdescriptionanno, 'contributor')
            else:
                continue
            ET.SubElement(m, 'name').text = pm.memberrel.name
            ET.SubElement(m, 'email').text = pm.memberrel.email

        sql1 = """select s.sampleid, s.orig_id, s.dataportal_descriptor
                    from samples s
                   where projid = %(projid)s 
                     and dataportal_descriptor is not null """
        sql3 = " "
        params = {'projid': int(self.param.ProjectId)}
        if self.param.samplelist != "":
            sql3 += " and s.orig_id = any(%(samplelist)s) "
            params['samplelist'] = self.param.samplelist.split(",")

        sql = sql1 + " " + sql3
        logging.info("Execute SQL : %s" % (sql,))
        logging.info("Params : %s" % (params,))
        self.pgcur.execute(sql, params)

        samples = ET.SubElement(project_elem, 'samples')
        for r in self.pgcur:
            sel = ET.SubElement(samples, 'sample')
            dtpdesc = ET.fromstring(r['dataportal_descriptor'])
            sel.append(dtpdesc)
            ET.SubElement(sel, 'sampleregistryreference', barcode=r['orig_id'])

            sql = """select distinct to1.name
                       from objects o
                       join taxonomy to1 on o.classif_id=to1.id
                      where o.sampleid={0:d}
                """.format(r['sampleid'], )
            taxo = GetAll(sql)
            taxoel = ET.SubElement(sel, 'taxonomicassignments')
            # TODO: variable 'r' is same as enclosing???
            # noinspection PyAssignmentToLoopOrWithParameter
            for r in taxo:
                ET.SubElement(taxoel, 'taxonomicassignment', taxon=r[0])

        ET.ElementTree(root).write(fichier, encoding="UTF-8", xml_declaration=True)

    def create_sum(self):
        self.UpdateProgress(1, "Start Summary export")
        Prj = database.Projects.query.filter_by(projid=self.param.ProjectId).first()
        grp = "to1.display_name"
        if self.param.sumsubtotal == "A":
            grp = "a.orig_id," + grp
        if self.param.sumsubtotal == "S":
            grp = "s.orig_id,s.latitude,s.longitude," + grp
        sql1 = "SELECT " + grp
        if self.param.sumsubtotal == "S":
            # Il est demandé d'avoir la colonne agrégé date au milieu du groupe, donc réécriture de la requete.
            sql1 = "SELECT  s.orig_id, s.latitude, s.longitude, max(objdate) as date, to1.display_name"
        sql1 += ",count(*) Nbr"
        sql2 = """ FROM objects o
                left join taxonomy to1 on o.classif_id = to1.id
                     join samples s on o.sampleid = s.sampleid
                     join acquisitions a on o.acquisid = a.acquisid """
        sql3 = " where o.projid=%(projid)s "
        params = {'projid': int(self.param.ProjectId)}
        if self.param.samplelist != "":
            sql3 += " and s.orig_id= any(%(samplelist)s) "
            params['samplelist'] = self.param.samplelist.split(",")

        # sql3 += sharedfilter.GetSQLFilter(self.param.filtres, params, self.task.owner_id)

        # Use the API entry point for filtering
        with ApiClient(ObjectsApi, self.cookie) as api:
            res: ObjectSetQueryRsp = api.get_object_set_object_set_project_id_query_post(self.param.ProjectId,
                                                                                         self.param.filtres)
            sql3 += "and o.objid = any (%(objids)s) "
            params["objids"] = sorted(res.object_ids)

        sql3 += " group by " + grp
        sql3 += " order by " + grp
        sql = sql1 + " " + sql2 + " " + sql3
        logging.info("Execute SQL : %s" % (sql,))
        logging.info("Params : %s" % (params,))
        self.pgcur.execute(sql, params)

        self.param.OutFile = "export_summary_{0:d}_{1:s}.tsv".format(Prj.projid,
                                                                     datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        fichier = os.path.join(self.GetWorkingDir(), self.param.OutFile)
        msg = "Creating file %s" % fichier
        logging.info(msg)
        self.UpdateProgress(50, msg)
        nb_lines = self.write_cursor_to_csv(fichier)
        msg = "Extracted %d rows" % nb_lines
        logging.info(msg)
        self.UpdateProgress(90, msg)

    def write_cursor_to_csv(self, fichier):
        nb_lines = 0
        with open(fichier, 'w', encoding='latin_1') as csvfile:
            wtr = csv.writer(csvfile, delimiter='\t', quotechar='"', lineterminator='\n')
            colnames = [desc[0] for desc in self.pgcur.description]
            wtr.writerow(colnames)
            for r in self.pgcur:
                wtr.writerow(r)
                nb_lines += 1
        return nb_lines

    def SPStep1(self):
        """ In subprocess, task.taskstep = 1 """
        logging.info("Input Param = %s" % (self.param.__dict__,))
        # A bit of forward-thinking...
        progress_before_copy = 100
        if self.param.putfileonftparea == 'Y':
            progress_before_copy = 95
        # Bulk of the job
        params = self.param
        if params.what == "TSV":
            self.CreateTSV(params.what, 1, progress_before_copy)
        elif params.what == "BAK":
            self.CreateTSV(params.what, 1, 10 if params.exportimagesbak != '' else progress_before_copy)
            if params.exportimagesbak != '':
                self.CreateIMG('sample', 10, progress_before_copy)
        elif params.what == "DOI":
            self.CreateTSV(params.what, 1, 10 if params.exportimagesdoi != '' else progress_before_copy)
            if params.exportimagesdoi != '':
                self.CreateIMG('taxo', 10, progress_before_copy)
        elif params.what == "XML":
            self.create_XML()
        elif params.what == "SUM":
            self.create_sum()
        else:
            raise Exception("Unsupported exportation type : %s" % (params.what,))
        # Final copy
        if params.putfileonftparea == 'Y':
            self.UpdateProgress(progress_before_copy, "Copying file to FTP")
            fichier = Path(self.GetWorkingDir()) / params.OutFile
            fichierdest = Path(app.config['FTPEXPORTAREA'])
            if not fichierdest.exists():
                fichierdest.mkdir()
            NomFichier = "task_%d_%s" % (self.task.id, params.OutFile)
            fichierdest = fichierdest / NomFichier
            # fichier.rename(fichierdest) si ce sont des volumes sur des devices differents ça ne marche pas
            shutil.copyfile(fichier.as_posix(), fichierdest.as_posix())
            params.OutFile = ''
            final_message = "Export successful : File '%s' is available on the 'Exported_data' FTP folder" % NomFichier
        else:
            final_message = "Export successful"

        self.task.taskstate = "Done"
        self.UpdateProgress(100, final_message)

        # self.task.taskstate="Error"
        # self.UpdateProgress(10,"Test Error")

    def QuestionProcess(self):
        Prj = database.Projects.query.filter_by(projid=gvg("projid")).first()
        txt = "<a href='/prj/%d'>Back to project</a>" % Prj.projid
        if not Prj.CheckRight(1):
            return PrintInCharte("ACCESS DENIED for this project<br>" + txt)
        txt += "<h3>Text export Task creation</h3>"
        txt += "<h5>Exported Project : #%d - %s</h5>" % (Prj.projid, XSSEscape(Prj.title))
        errors = []
        self.param.filtres = {}
        for k in sharedfilter.FilterList:
            if gvg(k, "") != "":
                self.param.filtres[k] = gvg(k, "")
        if len(self.param.filtres) > 0:
            TxtFiltres = ",".join([k + "=" + v for k, v in self.param.filtres.items() if v != ""])
        else:
            TxtFiltres = ""

        if self.task.taskstep == 0:
            # Le projet de base est choisi second écran ou validation du second ecran
            if gvp('starttask') == "Y":
                # validation du second ecran
                self.param.ProjectId = gvg("projid")
                self.param.what = gvp("what")
                self.param.samplelist = gvp("samplelist")
                self.param.objectdata = gvp("objectdata")
                self.param.processdata = gvp("processdata")
                self.param.acqdata = gvp("acqdata")
                self.param.sampledata = gvp("sampledata")
                self.param.histodata = gvp("histodata")
                self.param.commentsdata = gvp("commentsdata")
                self.param.usecomasepa = gvp("usecomasepa")
                self.param.sumsubtotal = gvp("sumsubtotal")
                self.param.internalids = gvp("internalids")
                self.param.use_internal_image_name = gvp("use_internal_image_name")
                self.param.exportimagesbak = gvp("exportimagesbak")
                self.param.exportimagesdoi = gvp("exportimagesdoi")
                self.param.typeline = gvp("typeline")
                self.param.splitcsvby = gvp("splitcsvby")
                self.param.putfileonftparea = gvp("putfileonftparea")
                if self.param.splitcsvby == 'sample':  # si on splitte par sample, il faut les données du sample
                    self.param.sampledata = '1'
                # Verifier la coherence des données
                # errors.append("TEST ERROR")
                if self.param.what == '':
                    errors.append("You must select What you want to export")
                if len(errors) > 0:
                    for e in errors:
                        flash(e, "error")
                else:  # Pas d'erreur, on lance la tache
                    return self.StartTask(self.param)
            else:  # valeurs par default
                self.param.what = "TSV"
                self.param.objectdata = "1"
                self.param.processdata = "1"
                self.param.acqdata = "1"
                self.param.sampledata = "1"
                self.param.splitcsvby = ""
            # recupere les samples
            sql = """select sampleid,orig_id
                       from samples 
                      where projid =%(projid)s
                      order by orig_id"""
            g.SampleList = GetAll(sql, {"projid": gvg("projid")}, cursor_factory=None)
            g.headcenter = "<h4>Project : <a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid, XSSEscape(Prj.title))
            if TxtFiltres != "":
                g.headcenter = "<h4>Project : <a href='/prj/{0}?{2}'>{1}</a></h4>". \
                    format(Prj.projid, Prj.title, "&".join([k + "=" + v for k, v in self.param.filtres.items()
                                                            if v != ""]))
            lst_users = database.GetAll(
                """select distinct u.email,u.name,Lower(u.name)
                     from users_roles ur join users u on ur.user_id=u.id
                    where ur.role_id=2
                      and u.active = TRUE 
                      and email like '%@%'
                    order by Lower(u.name)""")
            g.LstUser = ",".join(["<a href='mailto:{0}'>{0}</a></li> ".format(*r) for r in lst_users])
            return render_template('task/textexport_create.html', header=txt, data=self.param, TxtFiltres=TxtFiltres)

    # noinspection PyPep8Naming
    def GetResultFile(self):
        return self.param.OutFile
