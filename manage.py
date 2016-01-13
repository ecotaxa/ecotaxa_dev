# manage.py

from flask.ext.script import Manager
from flask.ext.security.utils import encrypt_password
from flask.ext.migrate import Migrate, MigrateCommand
from appli import db,user_datastore,database
from appli import app
import shutil,os

manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def hello():
    print ("hello")

@manager.command
def createadminuser():
    """
    Create Admin User in the database admin/password
    """

    from appli.database import roles
    r=roles.query.filter_by(id=1).first()
    if r is None:
        print("Create role ",database.AdministratorLabel)
        db.session.add(roles(id=1,name=database.AdministratorLabel))
        db.session.commit()
    r=roles.query.filter_by(id=2).first()
    if r is None:
        print("Create role ",database.UserAdministratorLabel)
        db.session.add(roles(id=2,name=database.UserAdministratorLabel))
        db.session.commit()

    u=user_datastore.find_user(email='admin')
    if u is not None:
        print("drop user ",u)
        user_datastore.delete_user(u)
        db.session.commit()
    print("Create user 'admin' with password 'ecotaxa'")
    user_datastore.create_user(email='admin', password=encrypt_password('ecotaxa'),name="Application Administrator")
    user_datastore.add_role_to_user('admin','Application Administrator')
    db.session.commit()

@manager.command
def dbdrop():
    db.drop_all()
@manager.command
def dbcreate():
    db.create_all()
    from flask.ext.migrate import _get_config
    config = _get_config(None)
    from alembic import command
    command.stamp(config, 'head')
    database.ExecSQL("""create view objects as select oh.*,ofi.*
    from obj_head oh left join obj_field ofi on oh.objid=ofi.objfid""")


@manager.command
def createsampledata():
    r=database.Projects.query.filter_by(projid=1).first()
    if r is None:
        db.session.add(database.Projects(projid=1,title="Test Project 1"))
        db.session.commit()

@manager.command
def ForceTest1Values():
    from appli import ObjectToStr
    from appli.tasks.taskmanager import AsyncTask,LoadTask
    t=LoadTask(14)
    t.param.IntraStep=0
    t.task.taskstep=1
    t.UpdateParam()

@manager.command
def ResetDBSequence(cur=None):
    print("Start Sequence Reset")
    if cur is None:
        cur=db.session
    cur.execute("SELECT setval('seq_acquisitions', (SELECT max(acquisid) FROM acquisitions), true)")
    cur.execute("SELECT setval('seq_images', (SELECT max(imgid) FROM images), true)")
    cur.execute("SELECT setval('seq_objects', (SELECT max(objid) FROM obj_head), true)")
    cur.execute("SELECT setval('seq_process', (SELECT max(processid) FROM process), true)")
    cur.execute("SELECT setval('seq_projects', (SELECT max(projid) FROM projects), true)")
    cur.execute("SELECT setval('seq_projectspriv', (SELECT max(id) FROM projectspriv), true)")
    cur.execute("SELECT setval('seq_samples', (SELECT max(sampleid) FROM samples), true)")
    cur.execute("SELECT setval('seq_taxonomy', (SELECT max(id) FROM taxonomy), true)")
    cur.execute("SELECT setval('seq_temp_tasks', (SELECT max(id) FROM temp_tasks), true)")
    cur.execute("SELECT setval('seq_users', (SELECT max(id) FROM users), true)")
    cur.execute("SELECT setval('roles_id_seq', (SELECT max(id) FROM roles), true)")
    print("Sequence Reset Done")


@manager.command
def FullDBRestore():
    """
    Will restore an exported DB as is and replace all existing data
    """
    from appli.tasks.taskimportdb import RestoreDBFull
    if input("This operation will import an exported DB and DESTROY all existings data of the existing database.\nAre you SURE ? Confirm by Y !").lower()!="y":
        print("Import Aborted !!!")
        exit()
    RestoreDBFull()

@manager.command
def RecomputeStats():
    """
    Recompute stats related on Taxonomy and Projects
    """
    import appli.cron
    appli.cron.RefreshAllProjectsStat()
    appli.cron.RefreshTaxoStat()

@manager.command
def CreateDB():
    if input("This operation will create a new empty DB.\n If a database exists, it will DESTROY all existings data of the existing database.\nAre you SURE ? Confirm by Y !").lower()!="y":
        print("Import Aborted !!!")
        exit()

    print("Configuration is Database:",app.config['DB_DATABASE'])
    print("Login: ",app.config['DB_USER'],"/",app.config['DB_PASSWORD'])
    print("Host: ",app.config['DB_HOST'])
    import psycopg2

    if os.path.exists("vault"):
        print("Drop existings images")
        shutil.rmtree("vault")
        os.mkdir("vault")

    print("Connect Database")
    # On se loggue en postgres pour dropper/creer les bases qui doit être déclaré trust dans hba_conf
    conn=psycopg2.connect(user='postgres',host=app.config['DB_HOST'])
    cur=conn.cursor()

    conn.set_session(autocommit=True)
    print("Drop the existing database")
    sql="DROP DATABASE IF EXISTS "+app.config['DB_DATABASE']
    cur.execute(sql)

    print("Create the new database")
    sql="create DATABASE "+app.config['DB_DATABASE']+" WITH ENCODING='LATIN1'  OWNER="+app.config['DB_USER']+" TEMPLATE=template0 LC_CTYPE='C' LC_COLLATE='C' CONNECTION LIMIT=-1 "
    cur.execute(sql)

    print("Create the Schema")
    dbcreate()
    print("Create Roles & Users")
    createadminuser()
    print("Creation Done")


if __name__ == "__main__":
    manager.run()