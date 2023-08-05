================
Hadrian.Conf.Fab
================

This is helpful for my deployments to webfaction.  It may or may not be right for your environment.  Use with caution.



Required Environment Variables
==============================

The following variables must be declared in your ``local`` fabfile::

    env.id = PROJECT_ID
    env.user = PROJECT_USER
    env.hosts = PROJECT_HOSTS
    
    env.directory = '~/projects/%s' % PROJECT_ID
    env.virtual_dir = '~/.virtualenvs'
    env.static_dir = '~/static/prod/fotochest/assets'
    env.project_virtual = '~/.virtualenvs/%s' % PROJECT_ID
    env.activate = 'source ~/.virtualenvs/%s/bin/activate' % PROJECT_ID
    env.deploy_user = PROJECT_USER
    env.apache_bin_dir = "~/webapps/django_env/apache2/bin"
    env.log_location = "~/logs/user/error_django_env.log"
    env.git_repo = "git@bitbucket.org:dstegelman/fotochest.git"
    env.production_branch = "prod-2"
    env.docs_dir = "~/webapps/docs_static/fotochest"



Command Reference
=================

Fabric Command Reference::

    # Local Development
    def run_local_server():
        """ Runs local development Django server """
        local("python manage.py runserver --settings=settings.local")
        
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
        local("python manage.py collectstatic --noinput --settings=settings.%s" % env.branch)
    
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
            
    def custom_migration(app, migration, environment):
        """ Runs a custom migration, takes App, Migration, and the settings environment to be run on.  HOSTED ONLY. """
        virtualenv('python manage.py migrate:%s %s --settings=settings.%s' % (app, migration, environment))
    
    def build_migration(app):
        """ (app) Builds a migration for the specified app. """
        local("python manage.py schemamigration %s --auto --settings=settings.local" % app)

        
    # Remote commands
    
    def view_log():
        """ View the log of a given app. """
        run('sudo cat %s' % env.log_location)
    
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
        env.branch = "production"
    
    def deploy(release_tag=None):
        """ Deploy an app on either alpha or production.  If production, a tag is required. """
        get_code_latest(env.branch)
        sync_db(env.branch)
        migrate(env.branch)
        collect_static()
        kick_apache()
        # Need to find out what we are going to do to restart.
        print("Deployment completed.")