from __future__ import with_statement
from fabric.api import *
import os
import glob
import time


# Local Development
def run_local_server():
    """ Runs local development Django server """
    local("python manage.py runserver_plus --settings=settings.local")
    
def run_local():
    """ Runs the local development process.  PIP, SYNC, MIGRATE """
    pip_install_req('local')
    sync_db('local')
    migrate('local')
    run_local_server()
    
def start_celery():
    """ Start a local celery instance with the django broker. """
    local("python manage.py celeryd -l info --concurrency=5 --settings=settings.local")
    
def test(app=None):
    """ Test(app) tests a given app name, if none is provided, runs the test runner for every single app, Django included. """
    if app:
        local('python manage.py test %s --settings=settings.local' % app)
    else:
        local('python manage.py test --settings=settings.local')
        
        
def self_upgrade(version):
    """ Upgrades the version of Hadrian in your local and to your designated server.  Pass the version (Branch, Tag) """
    local("pip install git+git://github.com/dstegelman/hadrian@%s#egg=hadrian --upgrade" % version)
    if env.branch:
        virtualenv("pip install git+git://github.com/dstegelman/hadrian@%s#egg=hadrian --upgrade" % version)

# Helper Functions

def collect_static():
    """ Collect static files, run before comitting call alpha or production first """
    virtualenv("python manage.py collectstatic --noinput --clear --settings=settings.%s" % env.settings)

def update_index():
    local("python manage.py update_index --settings=settings.local")

def virtualenv(command):
    with cd(env.directory):
        run(env.activate + '&&' + command)

def pip_install_req(environment):
    if environment == 'local':
        local("pip install -r conf/requirements.txt")
    else:
        virtualenv('pip install -r conf/requirements.txt') 

def sync_db(environment):
    if environment == "local":
        local("python manage.py syncdb --settings=settings.local")
    else:
        virtualenv('python manage.py syncdb --settings=settings.%s' % environment)
    
def migrate(environment):
    if environment == "local":
        local("python manage.py migrate --settings=settings.local")
    else:
        virtualenv('python manage.py migrate --settings=settings.%s' % environment)
        
def build_migration(app):
    """ (app) Builds a migration for the specified app. """
    local("python manage.py schemamigration %s --auto --settings=settings.local" % app)
 
def load_data(datafile):
    virtualenv('python manage.py loaddata %s --settings=settings.%s' % (datafile, env.branch))

def dump_data(app):
    virtualenv('python manage.py dumpdata %s --indent=2 --settings=settings.%s' % (app, env.branch))    

# Remote commands

def kick_apache():
    """ Kick the apache server for this app. """
    with cd(env.apache_bin_dir):
            run("./restart")

def get_code_latest(branch):
    with cd(env.directory):
        run('git pull origin %s' % branch)
        
def get_code_release(tag):
    with cd(env.directory):
        run('git fetch --tags')
        run('git checkout %s' % tag)
                
        
def production():
    """ Set environment to production. """
    env.branch = env.production_branch
    env.settings = env.production_settings

def deploy(release_tag=None):
    """ Deploy an app  """
    get_code_latest(env.branch)
    pip_install_req(env.branch)
    sync_db(env.settings)
    migrate(env.settings)
    collect_static()
    kick_apache()
    # Need to find out what we are going to do to restart.
    print("Deployment completed.")