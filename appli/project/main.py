#Todo details histo & Save change
#Todo filtres
#todo icone refresh annotation
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,time,math,collections
from appli.database import GetAll,GetClassifQualClass,db

@app.route('/prj/')
@login_required
def indexProjects():
    txt = "<h3>Select your Project</h3>"
    sql="select p.projid,title,status,pctvalidated from projects p"
    if not current_user.has_role(database.AdministratorLabel):
        sql+=" Join projectspriv pp on p.projid = pp.projid and pp.member=%d"%(current_user.id)
    sql+=" order by title"
    res = GetAll(sql) #,debug=True
    txt+="""<table class='table table-bordered table-hover'>
            <tr><th width=100>ID</td><th>Title</td><th width=100>Status</td><th width=100>Progress</td></tr>"""
    for r in res:
        txt+="""<tr><td><a class="btn btn-primary" href='/prj/{0}'>Go !</a> {0}</td>
        <td>{1}</td>
        <td>{2}</td>
        <td>{3}</td>
        </tr>""".format(*r)
    txt+="</table>"

    return PrintInCharte(txt)

def GetFieldList(Prj):
    fieldlist=collections.OrderedDict()
    fieldlist["orig_id"]="Image Name"
    objmap=DecodeEqualList(Prj.mappingobj)
    #fieldlist fait le mapping entre le nom fonctionnel et le nom à affiche
    # cette boucle permet de faire le lien avec le nom de la colonne (si elle existe.
    for field,dispname in DecodeEqualList(Prj.classiffieldlist).items():
        for ok,on in objmap.items():
            if field==on :
                fieldlist[ok]=dispname
    return fieldlist

@app.route('/prj/<int:PrjId>')
@login_required
def indexPrj(PrjId):
    data={ 'ipp':str(current_user.GetPref('ipp',100))
          ,'zoom':str(current_user.GetPref('zoom',100))
          ,'sortby':current_user.GetPref('sortby',"")
          ,'dispfield':current_user.GetPref('dispfield',"")
          ,'sortorder':current_user.GetPref('sortorder',"")
          ,'magenabled':str(current_user.GetPref('magenabled',1))
          }
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    fieldlist=GetFieldList(Prj)
    data["fieldlist"]=fieldlist
    data["sortlist"]=collections.OrderedDict({"":""})
    for k,v in fieldlist.items():data["sortlist"][k]=v
    data["sortlist"]["classifname"]="Category Name"
    data["sortlist"]["random_value"]="Random"
    if not Prj.CheckRight(0): # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot view this project','error')
        return PrintInCharte("<a href=/prj/>Select annother project</a>")
    g.PrjAnnotate=g.PrjManager=Prj.CheckRight(2)
    if not g.PrjManager: g.PrjAnnotate=Prj.CheckRight(1)
    right='dodefault'
    classiftab=GetClassifTab(Prj)
    g.headmenu = []
    g.headmenu.append(("/prj/%d"%(PrjId,),"Project home/Annotation"))
    g.headmenu.append(("","SEP"))
    if g.PrjManager:
        g.headmenu.append(("/Task/Create/TaskImport?p=%d"%(PrjId,),"Import data"))


    return render_template('project/projectmain.html',top="",lefta=classiftab
                           ,right=right,data=data,projid=PrjId)

@app.route('/prj/LoadRightPane', methods=['GET', 'POST'])
@login_required
def LoadRightPane():
    # récupération des parametres d'affichage
    ipp=int(gvp("ipp","10"))
    zoom=int(gvp("zoom","100"))
    pageoffset=int(gvp("pageoffset","0"))
    sortby=gvp("sortby","")
    sortorder=gvp("sortorder","")
    dispfield=gvp("dispfield","")
    PrjId=gvp("projid")
    # dispfield=" dispfield_orig_id dispfield_n07"
    # on sauvegarde les parametres dans le profil utilisateur
    if current_user.SetPref("ipp",ipp) + current_user.SetPref("zoom",zoom)+ current_user.SetPref("sortby",sortby)\
            + current_user.SetPref("sortorder",sortorder)+ current_user.SetPref("dispfield",dispfield) >0:
        database.ExecSQL("update users set preferences=%s where id=%s",(current_user.preferences,current_user.id),True)
        user_datastore.ClearCache()
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    fieldlist=GetFieldList(Prj)
    fieldlist.pop('orig_id','')
    t=[]
    sqlparam={'projid':gvp("projid")}
    sql="""select o.objid,t.name taxoname,o.classif_qual,u.name classifwhoname,i.file_name
  ,i.height,i.width,i.thumb_file_name,i.thumb_height,i.thumb_width
  ,o.depth_min,o.depth_max,s.orig_id samplename,o.objdate,o.objtime
  ,o.latitude,o.orig_id,o.imgcount"""
    for k in fieldlist.keys():
        sql+=",o."+k+" as extra_"+k
    sql+=""" from objects o
Join images i on o.img0id=i.imgid
left JOIN taxonomy t on o.classif_id=t.id
LEFT JOIN users u on o.classif_who=u.id
LEFT JOIN  samples s on o.sampleid=s.sampleid
where o.projid=%(projid)s
"""
    if(gvp("taxo")!=""):
        sql+=" and o.classif_id=%(taxo)s "
        sqlparam['taxo']=gvp("taxo")
    sqlcount="select count(*) from ("+sql+") q"
    nbrtotal=GetAll(sqlcount,sqlparam,False)[0][0]
    pagecount=math.ceil(nbrtotal/ipp)
    if sortby=="classifname":
        sql+=" order by t.name "+sortorder
    elif sortby!="":
        sql+=" order by o."+sortby+" "+sortorder
    sql+=" Limit %d offset %d "%(ipp,pageoffset*ipp)
    res=GetAll(sql,sqlparam,False)
    trcount=1
    t.append("<table class=imgtab><tr id=tr1>")
    WidthOnRow=0
    #récuperation et ajustement des dimensions de la zone d'affichage
    try:
        PageWidth=int(gvp("resultwidth"))-40 # on laisse un peu de marge à droite et la scroolbar
        if PageWidth<200 : PageWidth=200
    except:
        PageWidth=200;
    try:
        WindowHeight=int(gvp("windowheight"))-100 # on enleve le bandeau du haut
        if WindowHeight<200 : WindowHeight=200
    except:
        WindowHeight=200;
    #print("PageWidth=%s, WindowHeight=%s"%(PageWidth,WindowHeight))
    # Calcul des dimmensions et affichage des images
    for r in res:
        filename=r['file_name']
        origwidth=r['width']
        origheight=r['height']
        thumbfilename=r['thumb_file_name']
        thumbwidth=r['thumb_width']
        thumbheight=r['thumb_height']
        width=origwidth*zoom//100
        height=origheight*zoom//100
        if max(width,height)<20: # en dessous de 20 px de coté on ne fait plus le scaling
            if max(origwidth,origheight)<20:
                width=origwidth   # si l'image originale est petite on l'affiche telle quelle
                height=origheight
            elif max(origwidth,origheight)==origwidth:
                width=20
                height=origheight*20//origwidth
                if height<1 : height=1
            else:
                height=20
                width=origwidth*20//origheight
                if width<1 : width=1

        # On limite les images pour qu'elles tiennent toujours dans l'écran
        if width>PageWidth:
            width=PageWidth
            height=math.trunc(r['height']*width/r['width'])
            if height==0: height=1
        if height>WindowHeight:
            height=WindowHeight
            width=math.trunc(r['width']*height/r['height'])
            if width==0: width=1
        if WidthOnRow!=0 and (WidthOnRow+width)>PageWidth:
            trcount+=1
            t.append("</tr></table><table class=imgtab><tr id=tr%d>"%(trcount,))
            WidthOnRow=0
        cellwidth=width+22
        # Met la fenetre de zoon la ou il y plus de place, sachant qu'elle fait 400px et ne peut donc pas être callée à gauche des premieres images.
        if (WidthOnRow+cellwidth)>(PageWidth/2):
            pos='left'
        else: pos='right'
        #Si l'image affiché est plus petite que la miniature, afficher la miniature.
        if thumbwidth is None or thumbwidth<width or thumbfilename is None: # sinon (si la miniature est plus petite que l'image à afficher )
            thumbfilename=filename # la miniature est l'image elle même

        txt="<td width={3}><img class='lazy' id=I{4} data-src='/vault/{6}' data-zoom-image='{0}' width={1} height={2} pos={5}>"\
            .format(filename,width,height,cellwidth,r['objid'],pos,thumbfilename)
        # Génération de la popover qui apparait pour donner quelques détails sur l'image
        poptxt=("<p style='white-space: nowrap;'>cat. %s")%(r['taxoname'],)
        if r[3]!="":
            poptxt+="<br>Identified by %s"%(r[3])
        for k,v in fieldlist.items():
            poptxt+="<br>%s : %s"%(v,ScaleForDisplay(r["extra_"+k]))
        # Génération du texte sous l'image qui contient la taxo + les champs à afficher
        bottomtxt=""
        for k,v in fieldlist.items():
            if k in dispfield:
                bottomtxt+="<br>%s : %s"%(v,ScaleForDisplay(r["extra_"+k]))

        txt+="<div class='subimg {1}' data-title=\"{2}\" data-content=\"{3}\"><span class=taxo >{0}</span>{4}<div class=ddet>Details {5}</div></div>"\
            .format(r['taxoname'],GetClassifQualClass(r['classif_qual']),r['orig_id'],poptxt,bottomtxt
                    ,"(%d)"%(r['imgcount'],) if r['imgcount']>1 else "")
        txt+="</td>"

        WidthOnRow+=max(cellwidth,80) # on ajoute au moins 80 car avec les label c'est rarement moins
        t.append(txt)

    t.append("</tr></table>")
    t.append("""<span id=PendingChanges></span><br>
        <button class='btn btn-primary' onclick='SavePendingChanges();'><span class='glyphicon glyphicon-floppy-open' /> Save changes</button>
        <button class='btn btn-success' onclick='ValidateAll();'><span class='glyphicon glyphicon-ok' /> Validate all objects</button>""")
    # Gestion de la navigation entre les pages
    if(pagecount>1):
        t.append("<p align=center> Page %d/%d - Go to page : "%(pageoffset+1,pagecount))
        if pageoffset>0:
            t.append("<a href='javascript:gotopage(%d);'>&lt;</a>"%(pageoffset-1))
        for i in range(0,pagecount-1,math.ceil(pagecount/20)):
            t.append("<a href='javascript:gotopage(%d);'>%d</a> "%(i,i+1))
        t.append("<a href='javascript:gotopage(%d);'>%d</a>"%(pagecount-1,pagecount))
        if pageoffset<pagecount-1:
            t.append("<a href='javascript:gotopage(%d);'>&gt;</a>"%(pageoffset+1))
        t.append("</p>")
    t.append("""
    <script>
        // Required to  have Select2 component working on Bootstrap Popup
        $.fn.modal.Constructor.prototype.enforceFocus = function() {};
        // Add Zoom
        jQuery('div#column-right img.lazy').Lazy({bind: 'event',afterLoad: function(element) {
            if($('#magenabled').prop("checked")==false)
                return; // Si il y a une checkbox magenabled et qu'elle est decochée on ne met pas le zoom
            AddZoom(element);}});
        // Make sub image draggable
        jQuery('.imgtab td .subimg').draggable({revert:true,revertDuration:0});
        // Make the cell clickable for selection
        jQuery('.imgtab td').click(function(e){
            if (!e.ctrlKey)
                $('.ui-selected').toggleClass('ui-selected');
            $(e.target).closest('td').toggleClass('ui-selected');
            //alert('test');
            });
        // Make ZoomTracker Clickable for selection
        jQuery('body').delegate('.zoomtracker','click',function(e){
            if (!e.ctrlKey)
                $('.ui-selected').toggleClass('ui-selected');
            $($(e.target).data("specs").origImg.parents("td")[0]).toggleClass('ui-selected')
            });
        // setup zoomtracker creation tracking to make them draggable
        var target = $( "body" )[0];
        var observer = new MutationObserver(function( mutations ) {
          mutations.forEach(function( mutation ) {
            var newNodes = mutation.addedNodes; // DOM NodeList
            if( newNodes !== null ) { // If there are new nodes added
                var $nodes = $( newNodes ); // jQuery set
                $nodes.each(function() {
                    var $node = $( this );
                    if( $node.hasClass( "zoomtracker" ) ) {
                        //console.log("zoomtracker");
                        jQuery($node).draggable({revert:true,revertDuration:0});
                    }
                });
            }
          });
        });
        var config = {attributes: true,childList: true,characterData: true};
        observer.observe(target, config);
        // Enable the popover
        var option={'placement':'bottom','trigger':'hover','html':true};
        $('div.subimg').popover(option);
        $('div.ddet').click(function(e){
            e.stopPropagation();
//            var url="/objectdetails/"+$(e.target).closest('td').find('img').prop('id').substr(1);
//            var win = window.open(url, '_blank');
            var url="/objectdetails/"+$(e.target).closest('td').find('img').prop('id').substr(1)+"?w="+($(window).width()-400)+"&h="+($(window).height()-40)+"&ajax=1";
            var options={}
            $("#PopupDetails .modal-content").html("Loading...");

            $('#PopupDetails .modal-lg').css('width',$(window).width()-40);
            $('#PopupDetails').modal(options);
            $("#PopupDetails .modal-content").load(url);
            });
$('#PopupDetails').on('hidden.bs.modal', function (e) {
    $("#PopupDetails .modal-content").html("CLEAN");
    $(".zoomContainer").remove();
})
        </script>""")
    return "\n".join(t)

def GetClassifTab(Prj):
    if Prj.initclassiflist is None:
        InitClassif="0" # pour être sur qu'il y a toujours au moins une valeur
    else:
        InitClassif=Prj.initclassiflist
    InitClassif=", ".join(["("+x.strip()+")" for x in InitClassif.split(",") if x.strip()!=""])
    sql="""select t.id,t.name taxoname,Nbr,NbrNotV
    from (  SELECT    o.classif_id,   c.id,count(classif_id) Nbr,count(case when classif_qual='V' then NULL else o.classif_id end) NbrNotV
        FROM (select * from objects where projid=%(projid)s) o
        FULL JOIN (VALUES """+InitClassif+""") c(id) ON o.classif_id = c.id
        GROUP BY classif_id, c.id
      ) o
    JOIN taxonomy t on coalesce(o.classif_id,o.id)=t.id
    order by t.name       """
    param={'projid':Prj.projid}
    res=GetAll(sql,param,False)
    return render_template('project/classiftab.html',res=res)