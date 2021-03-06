# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)

import os, sys, pathlib, urllib.parse

# Permet de traiter le probleme de l'execution dans un virtualenv sous windows de mathplotlib qui requiert TCL
if sys.platform.startswith('win32'):
    virtualprefix = sys.base_prefix
    if hasattr(sys, 'real_prefix'):
        sys.base_prefix = sys.real_prefix
    if float(sys.winver.replace('-32', '')) < 3.5:
        from tkinter import _fix

        if "TCL_LIBRARY" not in os.environ:
            # reload module, so that sys.real_prefix be used
            from imp import reload

            reload(_fix)
    sys.base_prefix = virtualprefix

VaultRootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "vault")
if not os.path.exists(VaultRootDir):
    os.mkdir(VaultRootDir)
TempTaskDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "temptask")
if not os.path.exists(TempTaskDir):
    os.mkdir(TempTaskDir)

from flask import Flask, render_template, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security
import inspect, html, math, threading, traceback
import appli.securitycachedstore
import matplotlib

matplotlib.use('Agg')

app = Flask("appli")
app.config.from_pyfile('config.cfg')
app.config['SECURITY_MSG_DISABLED_ACCOUNT'] = (
    'Your account is disabled. Email to the User manager (list on the left) to re-activate.', 'error')
app.logger.setLevel(10)

if 'PYTHONEXECUTABLE' in app.config:
    app.PythonExecutable = app.config['PYTHONEXECUTABLE']
else:
    app.PythonExecutable = "TBD"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={
    'expire_on_commit': True})  # expire_on_commit évite d'avoir des select quand on manipule les objets aprés un commit.


def XSSEscape(txt):
    return html.escape(txt)


import appli.database

# Setup Flask-Security
user_datastore = appli.securitycachedstore.SQLAlchemyUserDatastoreCACHED(db, database.users, database.roles)
security = Security(app, user_datastore)

app.MRUClassif = {}  # Dictionnaire des valeurs recement utilisé par les classifications
app.MRUClassif_lock = threading.Lock()


def ObjectToStr(o):
    #    return str([(n, v) for n, v in inspect.getmembers(o) if((not inspect.ismethod(v))and  (not inspect.isfunction(v))and  (n!='__module__')and  (n!='__doc__') and  (n!='__dict__') and  (n!='__dir__')and  (n!='__delattr__')and  (n!='__dir__')and  (n!='__dir__') )])
    return str([(n, v) for n, v in inspect.getmembers(o) if (
            ('method' not in str(v)) and (not inspect.isfunction(v)) and (n != '__module__') and (
            n != '__doc__') and (n != '__dict__') and (n != '__dir__') and (n != '__weakref__'))])


def PrintInCharte(txt, title=None):
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    AddTaskSummaryForTemplate()
    module = ''  # Par defaut c'est Ecotaxa
    if request.path.find('/part') >= 0:
        module = 'part'
    if not title:
        if module == 'part':
            title = 'EcoPart'
        else:
            title = 'EcoTaxa'
    return render_template('layout.html', bodycontent=txt, module=module, title=title)


def ErrorFormat(txt):
    return """
<div class='cell panel ' style='background-color: #f2dede; margin: 15px;'><div class='body' >
				<table style='background-color: #f2dede'><tr><td width='50px' style='color: red;font-size: larger'> <span class='glyphicon glyphicon-exclamation-sign'></span></td>
				<td style='color: red;font-size: larger;vertical-align: middle;'><B>%s</B></td>
				</tr></table></div></div>
    """ % (txt)


def AddTaskSummaryForTemplate():
    from flask_login import current_user
    if getattr(current_user, 'id', -1) > 0:
        g.tasksummary = appli.database.GetAssoc2Col(
            "SELECT taskstate,count(*) from temp_tasks WHERE owner_id=%(owner_id)s group by taskstate"
            , {'owner_id': current_user.id})
    g.google_analytics_id = app.config.get('GOOGLE_ANALYTICS_ID', '')


def gvg(varname, defvalue=''):
    """
    Permet de récuperer une variable dans la Chaine GET ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par default si elle n'existe pas
    """
    return request.args.get(varname, defvalue)


def gvp(varname, defvalue=''):
    """
    Permet de récuperer une variable dans la Chaine POST ou de retourner une valeur par defaut
    :param varname: Variable à récuperer
    :param defvalue: Valeur par default
    :return: Chaine de la variable ou valeur par default si elle n'existe pas
    """
    return request.form.get(varname, defvalue)


def ntcv(v):
    """
    Permet de récuperer une chaine que la source soit une chaine ou un None issue d'une DB
    :param v: Chaine potentiellement None
    :return: V ou chaine vide
    """
    if v is None:
        return ""
    return v


def nonetoformat(v, fmt: str):
    """
    Permet de faire un formatage qui n'aura lieu que si la donnée n'est pas nulle et permet récuperer une chaine que la source soit une données ou un None issue d'une DB
    :param v: Chaine potentiellement None
    :param fmt: clause de formatage qui va etre générée par {0:fmt}
    :return: V ou chaine vide
    """
    if v is None:
        return ""
    return ("{0:" + fmt + "}").format(v)


def DecodeEqualList(txt):
    res = {}
    for l in str(txt).splitlines():
        ls = l.split('=', 1)
        if len(ls) == 2:
            res[ls[0].strip().lower()] = ls[1].strip().lower()
    return res


def EncodeEqualList(map):
    l = ["%s=%s" % (k, v) for k, v in map.items()]
    l.sort()
    return "\n".join(l)


def ScaleForDisplay(v):
    """
    Permet de supprimer les decimales supplementaires des flottant en fonctions de la valeur et de ne rien faire au reste
    :param v: valeur à ajuste
    :return: Texte formaté
    """
    if isinstance(v, (float)):
        if (abs(v) < 100):
            return "%0.2f" % (v)
        else:
            return "%0.f" % (v)
    elif v is None:
        return ""
    else:
        return v


def XSSUnEscape(txt):
    return html.unescape(txt)


def TaxoNameAddSpaces(name):
    Parts = [XSSEscape(x) for x in ntcv(name).split('<')]
    return ' &lt;&nbsp;'.join(Parts)  # premier espace secable, second non


def FormatError(Msg, *args, DoNotEscape=False, **kwargs):
    caller_frameinfo = inspect.getframeinfo(sys._getframe(1))
    txt = Msg.format(*args, **kwargs)
    app.logger.error("FormatError from {} : {}".format(caller_frameinfo.function, txt))
    if not DoNotEscape:
        Msg = Msg.replace('\n', '__BR__')
    txt = Msg.format(*args, **kwargs)
    if not DoNotEscape:
        txt = XSSEscape(txt)
    txt = txt.replace('__BR__', '<br>')
    return "<div class='alert alert-danger' role='alert'>{}</div>".format(txt)


def FAIcon(classname, styleclass='fas'):
    return "<span class='{} fa-{}'></span> ".format(styleclass, classname)


def FormatSuccess(Msg, *args, DoNotEscape=False, **kwargs):
    txt = Msg.format(*args, **kwargs)
    if not DoNotEscape:
        txt = XSSEscape(txt)
    if not DoNotEscape:
        Msg = Msg.replace('\n', '__BR__')
    txt = Msg.format(*args, **kwargs)
    if not DoNotEscape:
        txt = XSSEscape(txt)
    txt = txt.replace('__BR__', '<br>')
    return "<div class='alert alert-success' role='alert'>{}</div>".format(txt)


def CreateDirConcurrentlyIfNeeded(DirPath: pathlib.Path):
    """
    Permets de créer le répertoire passé en paramètre s'il n'existe pas et le crée si nécessaire.
    Si la création échoue, il teste s'il n'a pas été créé par un autre processus, et dans ce cas ne remonte pas d'erreur.
    :param DirPath: répertoire à créer sous forme de path
    """
    try:
        if not DirPath.exists():
            DirPath.mkdir()
    except Exception as e:
        if not DirPath.exists():
            raise e


def ComputeLimitForImage(imgwidth, imgheight, LimitWidth, LimitHeight):
    width = imgwidth
    height = imgheight
    if width > LimitWidth:
        width = LimitWidth
        height = math.trunc(imgheight * width / imgwidth)
        if height == 0: height = 1
    if height > LimitHeight:
        height = LimitHeight
        width = math.trunc(imgwidth * height / imgheight)
        if width == 0: width = 1
    return width, height


def GetAppManagerMailto():
    # Left here for EcoPart
    if 'APPMANAGER_EMAIL' in app.config and 'APPMANAGER_NAME' in app.config:
        return "<a href='mailto:{APPMANAGER_EMAIL}'>{APPMANAGER_NAME} ({APPMANAGER_EMAIL})</a>".format(**app.config)
    return ""


def CalcAstralDayTime(Date, Time, Latitude, Longitude):
    """
    Calcule la position du soleil pour l'heure donnée.
    :param Date: Date UTC
    :param Time:  Heure UTC
    :param Latitude: Latitude
    :param Longitude: Longitude
    :return: D pour Day, U pour Dusk/crépuscule, N pour Night/Nuit, A pour Aube/Dawn
    """
    from astral import Location
    l = Location()
    l.solar_depression = 'nautical'
    l.latitude = Latitude
    l.longitude = Longitude
    s = l.sun(date=Date, local=False)
    # print(Date,Time,Latitude,Longitude,s,)
    Result = '?'
    Inter = ({'d': 'sunrise', 'f': 'sunset', 'r': 'D'}
             , {'d': 'sunset', 'f': 'dusk', 'r': 'U'}
             , {'d': 'dusk', 'f': 'dawn', 'r': 'N'}
             , {'d': 'dawn', 'f': 'sunrise', 'r': 'A'}
             )
    for I in Inter:
        if s[I['d']].time() < s[I['f']].time() and (Time >= s[I['d']].time() and Time <= s[I['f']].time()):
            Result = I['r']
        elif s[I['d']].time() > s[I['f']].time() and (Time >= s[I['d']].time() or Time <= s[I['f']].time()):
            Result = I['r']  # Changement de jour entre les 2 parties de l'intervalle
    return Result


_utf_warn = "HINT: Did you use utf-8 while transferring?"

import unicodedata


def _suspicious_str(path: str):
    if not isinstance(path, str):
        return False
    try:
        t = repr(path)
        for c in path:
            # Below throws an exception and that's all we need
            unicodedata.name(c)
            if 0xFFF0 <= ord(c) <= 0xFFFF:
                # Replacement chars
                return True
        return False
    except ValueError:
        return True


def UtfDiag(errors, path: str):
    if _suspicious_str(path):
        errors.append(_utf_warn)


def UtfDiag2(fn, path1: str, path2: str):
    if _suspicious_str(path1) or _suspicious_str(path2):
        fn(_utf_warn)


def UtfDiag3(path: str):
    if _suspicious_str(path):
        return ". " + _utf_warn
    return ""


# Ici les imports des modules qui definissent des routes
import appli.main
import appli.tasks.taskmanager
import appli.search.view
import appli.project.view
import appli.part.view
import appli.taxonomy.taxomain
import appli.usermgmnt
import appli.api_proxy
import appli.project.emodnet


@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.exception(e)
    return render_template("errors/500.html"), 500


@app.errorhandler(Exception)
def unhandled_exception(e):
    # Ceci est imperatif si on veut pouvoir avoir des messages d'erreurs à l'écran sous apache
    app.logger.exception(e)
    # Ajout des informations d'exception dans le template custom
    tb_list = traceback.format_tb(e.__traceback__)
    s = "<b>Error:</b> %s <br><b>Description: </b>%s \n<b>Traceback:</b>" % (
        html.escape(str(e.__class__)), html.escape(str(e)))
    for i in tb_list[::-1]:
        s += "\n" + html.escape(i)
    db.session.rollback()
    return render_template('errors/500.html', trace=s), 500


def JinjaFormatDateTime(d, format='%Y-%m-%d %H:%M:%S'):
    if d is None:
        return ""
    return d.strftime(format)


def JinjaNl2BR(t):
    return t.replace('\n', '<br>\n')


def JinjaGetManagerList(sujet=""):
    LstUsers = database.GetAll("""select distinct u.email,u.name,Lower(u.name)
FROM users_roles ur join users u on ur.user_id=u.id
where ur.role_id=2
and u.active=TRUE and email like '%@%'
order by Lower(u.name)""")
    if sujet:
        sujet = "?" + urllib.parse.urlencode({"subject": sujet}).replace('+', '%20')
    return " ".join(["<li><a href='mailto:{1}{0}'>{2} ({1})</a></li> ".format(sujet, *r) for r in LstUsers])


ecotaxa_version = "2.5.5"


def JinjaGetEcotaxaVersionText():
    return ecotaxa_version + " 2021-02-11"


app.jinja_env.filters['datetime'] = JinjaFormatDateTime
app.jinja_env.filters['nl2br'] = JinjaNl2BR
app.jinja_env.globals.update(GetManagerList=JinjaGetManagerList, GetEcotaxaVersionText=JinjaGetEcotaxaVersionText)

"""Changelog
2021-02-03 : V 2.5.5
    Feature #603: Export abundances / concentrations of 0 in DwCA export
    Bug #583 (starting): Set-up database storage of information about images on disk. Add an API
        entry point to store MD5 of present files. 
    Feature #579: Amend database to store users email validity information.
    Bug #602 (Api): PUT projects/{project_id} i.e. project update fails silently on some errors
    Feature #612: Relocate admin app in a dedicated sub-app. 
    Bug #587: "Visible for all visitors" checkbox cannot be changed in project settings". 
2021-02-03 : V 2.5.4
    Bug #548 (starting): Move object orig_id from obj_field DB table to obj_head. 
    Bug #523: Cosmetic fix (order of categories in project settings page).
    Feature #436 (continues): Use more entry points from backend, around Samples and Taxonomy. 
    Feature #411: Remove DB export and import. App. export is better even if slower.
2021-01-28 : V 2.5.3
    Feature #430: Move selection using CTRL-key + arrows in manual classification page
    Bug #371: Manual classification layout is broken (scrolls) with too long taxa names.
    Regression #574: Instrument list does not show in Other Filters when clicking ?
    Regression #576: When last page in manual classification does not match filtering criterion, it appears
        empty after a save. Used to jump automatically back to previous one.
    Feature #399: CTRL-SHIFT+left/right arrow to move b/w pages in manual classification page.
    Data consistency bug #544: It was possible to have several paths to reach an object.
2021-01-21 : V 2.5.2
    Feature #557: Rename some API endpoints for naming consistency
    Feature #511: Add a legal license per project.
    Feature #564: Add a second "Save" button in Project Settings page
    Feature #565: Add a Contact Person per project
    Feature #4: Add a "Recent projects" list (with last accesses projects)
    Bug #541: Ensure that the objects hierarchy is consistent
    Bug #567: Under some conditions, FastAPI framework leaks request resource (DB session) 
2021-01-14 : V 2.5.1
    Feature #529: Show a progress bar while loading in the manual classification window.
    Bug #549: Cryptic error when import update fails due to rights problem.
    Bug #556: Fields are not updated in object_set/update when mixing plain and free columns.
    Bug #538: Space in sample names made them unselectable in "Pick from other projects" child window.
    Regression due to #523 fix: Preset were erased from project after editing rights only. 
2020-12-08 : V 2.5.0
    Bug #542: During export with images, arrange that resultsets from DB are flushed to disk instead of remaining opened.
    Bug #537: There is now a decent progress bar during export.
    Bug #540: It's not possible anymore to have a NULL orig_id in Samples and Acquisitions.
    Bug #546 (partial fix): orig_id is now unique for Samples and Acquisitions. Process is not relevant anymore. Object remains.
    Feature #144: Check the hierarchy in data identifiers at import time.
    Feature #367: Merge acquisition and process into a single entity.
2020-11-25 : V 2.4.7
    Feature #389: Force presence of sample/acquisition/process for each object.
    Features #435, #523: More functions go thru API from flask app.
2020-11-10 : V 2.4.6
    Bug #503: Inconsistency in database schema on samples, acquisitions and process tables.
    Bug #523, #524: Project settings page layout is damaged and predefined taxonomy not saved.
    Bug #501: It was possible to delete objects outside current project.
    Bug #499: Last imported path was not recorded for 'import update'.
    Bug #68: Inconsistency in 'Import Database' UI.
    Bug #345: Users were told late that nothing has to be done during automatic classification.    
2020-10-29 : V 2.4.5
    Bug #516: No title for project in anonymous view mode.
    Feature #426: Minimal UI to export a project in DwC format. Menu is hidden.
    Feature #244: Add a license field for projects.
    Feature #435: Project edit now on back-end (excluding CNN list).
2020-10-14 : V 2.4.4
    Bug #500: Base view for queries should be simpler and faster.
    Feature #497: Sort tasks by more recents first.
    Feature #435: Object details is now implemented on back-end.
    Bug #414: Useless commit appears as a warning in PG logs.
    Feature #321: Proper message when a user who cannot create a taxon needs one.
    Bug #342: Taxon select box has no MRU or create link in object details window. 
    Bug #422: Update sun position when related metadata changes.
    Bug #341: Filter "NaN" and "NA" even in text columns.
    Feature #435: Move classification/validation to back-end.
    Bug #464: Last used taxa should not be random.
2020-09-30 : V 2.4.3
    Bug: Ecopart #451: Too long project title makes layout of EcoPart prjedit page ugly.
    Bug: Ecopart #437: Stack trace when displaying TIME.
    Bug: Ecopart #433: Single-line TIME_LPM files cannot be imported.
    Feature: Ecopart #288: Add date+time in map popup.
    Feature: Ecopart #438: View pressure in TIME mode.
    Feature: Ecopart #432: Improve UVP6 remote import (http* support).
    Documentation: Ecopart #442: Indicate polling frequency for UVP remote files.
    Documentation: Ecopart #378: Indicate data origin in import task.
    Feature #452: No more confusion matrix page.
    Feature #435: Edit / Erase annotation massively is now implemented on back-end.
    Feature #383: Mouse move + click in manual classification page sometimes fails to select.
    Feature: Ecopart #202: Choice between Zoo and LPM formats during export.
    Documentation: Ecopart #356: Indicate units in export page.
    Bug #475: Some user fields could start/end with blanks.
    Bug #477: Category assignment using ENTER did not work with same category.
    Bug #463: Re-fix. Behavior was different when typing into the input and outside, e.g. in vignettes pane.
    Bug #459: _One_ of the tens of missing user input controls is now implemented.
    Bug #458: SCN Network presence is checked before using it during prediction.
    Bug #344: Export summary crashed when current filter was on an object feature.
    Bug #368: Saving with opened autocompletion left an unused window in the page upper left corner.
    Bug #483: Cryptic error during import with too large image files.
    Bug #484: Right checking was wrong for READ action.
    Bug #466: Make optional a previously mandatory column during import update.    
2020-09-16 : V 2.4.2
    Feature #245: More API primitives implemented on back-end, namely mass update and reset to predicted.
    Bugfix #465: Right-click menu in category is cropped and moves with right pane.
    Feature #445: Remember, per project, the directory used during last import operation.
    Bugfix #463: Recent categories were not filtered as they should have.
2020-09-02 : V 2.4.1
    Feature #245: More API primitives implemented on back-end.
    Bugfix #350: Object mappings are now re-ordered during merge.
    Bugfix #352: Merge is now impossible when it would mean data loss.
    Bugfix #408: Subset operation now uses same bulk operations as import.
    Removal of some dead code.
2020-07-02 : V 2.3.4
    Bugfix #419: Add preset/add extra unusable due to HTML escape.
    Feature #282: Subset extraction page improvement.
    Feature: Ecopart #423: Allow a special value for last image.
2020-06-10 : V 2.3.3
    Bugfix #391, #418, #420: Rewrite of manual classification entry point for safer multi-session access.
    Feature #400: Move simple import to back-end.
2020-05-27 : V 2.3.2
    Bugfix #357: Outdated logos.
    Feature #401: Add a mailto: link to owner for each task in task list.
    Feature #222: Add a link to project for each task in task list.
    Bugfix #413: Daily Task (cron) fails.
    Feature #406: EcoPart: Share current filters by mail.
    Feature #400: Move import update to back-end.
    Bugfix #403: EcoPart: Last graph in series is damaged.
2020-05-18 : V 2.3.1
    Bugfix #402: Under server load or for big page sizes, vignettes could appear after a delay.
2020-05-13 : V 2.3
    Architecture #400: Move some code to back-end, potentially in a container.
    Bugfix #349: Time format wrongly hinted in Mass Update page.
    Bugfix #320: "Dust" instead of "Dusk" in parts of day display.
    Bugfix #322: Document limit of custom fields for each table in import page.
    Bugfix #395: Ensure preferences do not overflow the DB column.
    Feature #379: EcoPart: Allow negative values in particle import.
    Feature #380: EcoPart: Remove descent filter for UVP6 datasets.
    Bugfix #300: EcoPart: User cannot export restricted project when not annotator.
    Bugfix #363: In details page, tasks are always flagged as "with error" while running.
    Bugfix #361: "Ecotaxa Administration" is a dead link in admin home.
    Bugfix #328: No country in a freshly created DB.
2020-05-05 : V 2.2.7
    Bugfix #334: L'utilisateur reçoit un indice en cas de nom de fichier problématique lors de l'import.
    Bugfix #281: Correction des rechargements aléatoires pendant la classification manuelle.
    Début de nettoyage du code #381.
2020-04-27 : V 2.2.6
    Bugfix #364 #366: Import de fichiers encodés latin_1 sous Linux.
    Bugfix #351: Exception python lors de l'import si la 2eme ligne du TSV n'est pas conforme.
2020-04-23 : V 2.2.5
    Amélioration du texte d'information sur le serveur FTP lors des exports.
2020-04-20 : V 2.2.4
    Bugfix/Regression #340 les imports d'objets sont en notation degrée decimaux et non pas degree.minutes
    Réduction du nombre de décimales lors des conversions des latitudes et longitudes exprimées en minutes
    Suppression de warning de dépraciation sur WTForm validators.required 
2020-02-07 : V 2.2.3
    Ajout de normpath sur certaines resolution de chemin suite à problème avec des lien sympboliques
2020-01-29 : V 2.2.2
    Part : Modification comportement default_depthoffset now override
    Part import : uvp6 sample use Pressure_offset
    Part export : Divers bugfix 
    Part view : Ajustement groupe de classes 
2020-01-14 : V 2.2.1
    Generation vignette : Largeur minimale pour voir au moins l'echelle
    Gestion UVP6 Remote : Format LOV TSV
    Fix python 3.7
    Améliorations performances import
    Part : Gestion graphique temporel temps absolu
    Part : Gestion graphique 1 couleur par sample + legende si un seul projet
    Part export : gestion aggregation des TSV sur détaillé et réduit + nom projet dans les summary
    Part import : ajustement format LOV TSV
    Part import : ignore les samples sans depth si profil vertical sinon si depth invalide mise à 0
      
2019-08-18 : V 2.2.0
    Intégration of UVPApp Data Format
2019-04-18 : V 2.1.0
    Fix #304,#316,#317
2019-04-03 : V 2.1.0
    Fix #111,#277,#304,#305,#306,#307,#311,#312,#314
2019.02.01 : V 2.0.1
    Fix implementation minor bug
2019.01.25 : V 2.0.0
    Integration with EcotaxoServer
    Handling new display_name child<parent #87,#172
    Python Packages upgrade (flask, numpy, scikit, .... ), Bootstrap Upgrade
    fix/improve #216,#274,#284,#280 
2018.11.22 : V 1.6.1
    Minor fix
2018.11.14 : V 1.6
    RandomForestClassifier modified from balanced to auto
    Export redesigned
    Import #224,#243,#248: Robustified issues with Sun Position computation, lat/lon of sample always recomputed
    ReImport : Added sun position computation, lat/lon of sample always recomputed
    Subset #255 : Added duplication of CNN features
    Admin Project : Enhanced user management
    Manual classif #169,#164 : Refresh counter at each save, use separated badges
    Manual classif #163,#162,#260 : autoremove autoadded by sort displayed fields, Validation,ObjDate,Lat,Long date available on list and added on popup
    Manual classif #161,#159,#158 : autorefresh on top filter value change, added Ctrl+L for Validate selection, Keep vertical position on save
    Manual classif #211,#210,#209,#207,#205,#183 : Help for TaxoFilter,Improved validator filter, Added filter on validation date, added save dubious
    Manual classif #212,#217: duplicated saving status, Annotator can import
    Maps : #208 added informations on the sample
    EcoPart Fix : computation of Plankton abondance include only Validated Now (then Reduced & Détailled export too)
    EcoPart Fix #201 : Export of raw now handle not-living exclusion
    EcoPart Fix #196: computation of Plankton abondance use the Deepth offset now, also substracted
    EcoPart Fix #184 : When ecotaxa project are merged, associated PartProject are now associated to the target project
    Also #214,#220,#186,#179,#178,#176,#175,#152,#107
    User Management : Handle Self creation and Country
    Privacy : Added privacy page and Google Analytics Opt-out
2018.08.16 : V 1.5.2
              Added hability to work on database without trust connection configured on pg_hba
              Added CSRF Token on AdminForms most sensibles screens
              Added CSRF protection on console screen
              Added CSP policies to reduce impact of XSS attack
              Fixed several SQL Inject vulnerabilities
              Fixed no more errors if folder SCN_networks is missing
              Removed dead code
2018.03.14 : V 1.5.1b
              Moved Daily task in external launch using cron.py
              fixed computation on particle
              modified handling of ftp export copy due to issue on LOV FTP is on NFS volume
2018.01.16 : V 1.5.1
              Bugfix on privilèges on part module causing performance issues
2017.12.23 : V 1.5
              Minor adjustements
2017.11.08 : V 1.4
              Deep machine learning Integration
              Optimization of classification update query
              Added a table for Statistics by taxo/project to optimize displays on classification
              Bugfix on Particle module
2017.11.03 : V 1.3.2
              On manual classification splitted menu on 2 menu : Project wide and filtered
              Implementing Automatic classification V2
              - Filtered prediction
              - Can save/and predict from model
              - New Screen for PostPredictionMapping
              - Multiple project for Learning Set
              - Handling Nan,+/- Inf as empty value
2017.09.16 : V 1.3.1
              Evolution of Confusion matrix for sklearn,numpy,matplotlib upgrade
              Evolution of RandomForest parameters
2017.07.05 : V 1.3.0
              Introduction of Particle module
2017.03.28 : V 1.2.3
              Bugfix in display annotator on image Popup
              Bugfix is Manage.py where using global db routine.
2017.03.22 : V 1.2.2
              Added composite taxon Taxon(parent) in metadata update screen
2017.03.12 : V 1.2.1
              Improved database transaction management to avoid long transaction
2017.01.30 : V 1.2
              Explore : Improved no result, improved taxo filter
              Explore : Public user can go on manual classification of any visible project
              Explore : Map on home of explore
              Map : Filter by project and Taxo
              Details page : MailTo to notify classif error, display on map,
              Details page : edit data by manager
              Import : Wizard to premapping, added taxo (parent) format allowed at import
              Import : Image import only with form to fill metadata
              Export BD at project level.
              Prediction : Limit count for statistics, predict only filtered taxon on target set
              Conf Matrix : Export TSV
              Topper : Progress bar, improved button clic, improved clear filter
              Contribute : Display selection count, change line selection behavior
              Contribute : Show taxo children
              Task : New menu for app admin + can see all task of all users


2016.12.07 : V 1.1 Several changes on annotation page, filters
              Select project : filter on name, instrument, subset
              Select project : display email
              Manual Classif : Several minor changes
              Manual Classif : Propose last 5 classification
              New Filters : Instrument, Annotator, Free Field, Month, Day period
              Import : New feature to update matadata from file
              Import : Bugfix on uppercase column name
              Project : New status to block prediction
              Filter on feature : Purge, subset, Export
              TSV Export : split in multiple file, predefined check, separate internalID, add 2nd line for reimport
              AutoClean empty sample
              Zoom : 200%
              Admin : All manager can create a project
              Home Page : Custom message by App manager
              Prediction : added PostClassifMapping
2016.06.10 : Removed X before Object name
             if file home.html or homebottom.html is missing use home-model.html and homebottom-model.html
             Theses file are read as UTF-8 Format instead of target platform settings.
             Integration of licenses files as md format before integration to GitHub
2016.03.15 : Added CreateDirConcurrentlyIfNeeded to avoid conflinct in creation of images directory by concurrent task
2016.01.17 : Added parameter PYTHONEXECUTABLE in Config.cfg
             Added objects view creation in Manage CreateDB
             Added a Matplotlib uses to execute correctly on GraphicLess server.
             Added Cascade delete on DB Definition to create them during CreateDB (obj_field & Histo)
             During ImportDb compare Taxon Name and Parent Taxon Name to detect correctly Name duplicate
2015.12.14 : Bugfix in import task, use only ecotaxa prefixed files
2015.12.11 : Improved CSV export to include Direct Taxonomy parent name and Taxonomy hierarchy
             Included license.txt File

"""


def load_admin():
    # Import a sub-application for admin
    # IMPORTANT: The admin blueprint needs to be loaded before flaskAdmin below,
    # as it registers routes/templates in /admin, and flask-admin does it as well.
    from .admin.admin_blueprint import adminBlueprint
    app.register_blueprint(adminBlueprint)
    # noinspection PyUnresolvedReferences
    from .admin.admin_from_flask import flaskAdmin

load_admin()