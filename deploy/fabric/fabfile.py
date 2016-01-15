from fabric.api import run, sudo, env, cd, prefix, task, quiet, prompt
from fabric.colors import red, yellow
from fabtools import require
from fabtools.python import virtualenv
import time
import fabtools
import ConfigParser


NGINX_TPL = '''
upstream labrepo {
    server 127.0.0.1:8001;
}

server {
    listen %(port)d;
    server_name %(server_name)s;

    charset utf-8;

    client_max_body_size 512m;

    access_log /var/log/nginx/%(server_name)s-access.log;
    error_log /var/log/nginx/%(server_name)s-error.log error;


    set $static_root "%(project_dir)s/public";

    location /static/ {
         alias $static_root/static/;
    }

    location /media/ {
         alias $static_root/media/;
    }

    location /favicon.ico {
        alias $static_root/static/favicon.ico;
    }

    location / {
        proxy_pass         http://labrepo;
        proxy_redirect     off;
        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
    }
}
'''

DOTENV_TPL = '''
DOMAIN="%(domain)s"
ADMIN_EMAIL="%(admin_email)s"
SECRET_KEY="%(secret_key)s"
LANGUAGE_CODE="%(language_code)s"
MONGODB_USER="%(mongodb_user)s"
MONGODB_PASSWD="%(mongodb_passwd)s"
MONGODB_NAME="%(mongodb_name)s"
MONGODB_HOST="%(mongodb_host)s"
MONGODB_PORT="%(mongodb_port)s"
EMAIL_HOST="%(email_host)s"
EMAIL_PORT=%(email_port)s
EMAIL_HOST_USER="%(email_host_user)s"
EMAIL_HOST_PASSWORD="%(email_host_password)s"
EMAIL_USE_TLS=%(email_use_tls)s
SERVER_EMAIL="%(server_email)s"
SOCIAL_AUTH_FACEBOOK_KEY="%(social_auth_facebook_key)s"
SOCIAL_AUTH_FACEBOOK_SECRET="%(social_auth_facebook_secret)s"
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="%(social_auth_google_oauth2_key)s"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="%(social_auth_google_oauth2_secret)s"
SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY="%(social_auth_linkedin_oauth2_key)s"
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET="%(social_auth_linkedin_oauth2_secret)s"
'''


@task
def read_config():
    env.hosts = [env.remote_host]
    env.path = '/home/{}/{}'.format(env.user, env.dir)
    env.settings = 'production'


env.use_ssh_config = True

ENV_COMMAND = 'source env/bin/activate'


@task
def manage(command):
    with cd(env.path), prefix(ENV_COMMAND):
        run('python manage.py {} --settings=settings.{}'.format(command, env.settings))


@task
def setup():
    prepare_env()
    if env.repo_url[:4] != 'http':
        deploy_key(show_only=False)
    get_code()
    start_services()
    final_steps()


@task
def prepare_env():
    require.deb.package('sudo')
    require.group('supervisor')
    fabtools.user.modify(env.user, extra_groups=['supervisor', 'sudo'])
    #ElasticSearch
    fabtools.deb.add_apt_key(url='http://packages.elasticsearch.org/GPG-KEY-elasticsearch')
    require.deb.source('elasticsearch', 'http://packages.elasticsearch.org/elasticsearch/1.2/debian', 'stable', 'main')
    #MongoDB
    fabtools.deb.add_apt_key(keyid='7F0CEB10', keyserver='hkp://keyserver.ubuntu.com:80')
    require.deb.source('mongodb', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart', 'dist', '10gen')
    fabtools.deb.update_index
    require.deb.packages([
        'python-dev',
        'python-pip',
        'python-virtualenv',
        'build-essential',
        'git',
        'supervisor',
        'openjdk-7-jre-headless',
        'nginx',
        'elasticsearch',
        'libjpeg-dev',
        'zlib1g-dev',
        'libpng12-dev',
        'libfreetype6-dev',
        'gettext',
        'gettext-doc',
    ])
    require.deb.package('mongodb-org', version='2.6.4')
    fabtools.service.stop('mongod')
    #Mongod configuration
    sudo('sed -i "s/#replSet=setname/replSet=rs0/g" /etc/mongod.conf')
    sudo('sed -i "s/#oplogSize=1024/oplogSize=128/g" /etc/mongod.conf')
    sudo('grep smallfiles /etc/mongod.conf || echo "smallfiles = true" >> /etc/mongod.conf')
    #Make Elasticsearch start with boot
    sudo('update-rc.d elasticsearch defaults')
    #Plugins for ElasticSearch
    if not fabtools.files.is_dir('/usr/share/elasticsearch/plugins/mapper-attachments'):
        sudo('/usr/share/elasticsearch/bin/plugin --install elasticsearch/elasticsearch-mapper-attachments/2.3.1')
    if not fabtools.files.is_dir('/usr/share/elasticsearch/plugins/river-mongodb'):
        sudo('/usr/share/elasticsearch/bin/plugin --install com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/2.0.1')
    # if not fabtools.files.is_dir('/usr/share/elasticsearch/plugins/jetty-1.2.1'):
    #     sudo('/usr/share/elasticsearch/bin/plugin -url https://oss-es-plugins.s3.amazonaws.com/elasticsearch-jetty/elasticsearch-jetty-1.2.1.zip -install elasticsearch-jetty-1.2.1')
    #Supervisor configuration
    fabtools.service.stop('supervisor')
    sudo('sed -i "s/chmod=0700.*/chmod=0770\\nchown=root:supervisor/g" /etc/supervisor/supervisord.conf')
    #Add security for elasticsearch
    sudo('iptables -A INPUT ! -s 127.0.0.1 -p tcp -m tcp --dport 9200 -j DROP')
    sudo('iptables -A INPUT ! -s 127.0.0.1 -p tcp -m tcp --dport 9300 -j DROP')


@task
def get_code():
    #Checkout code from repository
    with cd('/home/{}'.format(env.user)):
        if env.repo_url[:4] != 'http':
            git_host = env.repo_url.split(':')[0].split('@')[1]
            run('ssh-keyscan {} >> .ssh/known_hosts'.format(git_host))
        require.git.working_copy(env.repo_url, branch=env.branch, path=env.dir)


@task
def deploy_key(user=env.user, show_only=True):
    with quiet():
        with cd('/home/{}'.format(env.user)):
            if (not show_only) or (show_only == 'False'):
                run('[ -d /home/{0}/.ssh ] || mkdir /home/{0}/.ssh'.format(user))
                run('[ -f /home/{0}/.ssh/id_rsa ] || ssh-keygen -C "deploy@{1}" -f /home/{0}/.ssh/id_rsa -P "" -q'.format(user, env.hosts[0]))
            key = run('ssh-keygen -y -f .ssh/id_rsa'.format(env.user))
    print (red("Add this key as deployment key in your repository settings"))
    print (yellow(key))
    prompt('Hit Enter to continue')


@task
def start_services():
    require.service.started('mongod')
    require.service.started('elasticsearch')
    require.service.started('supervisor')
    require.service.started('nginx')


@task
def final_steps():
    require.python.virtualenv('{}/env'.format(env.path))
    require.files.directory('/home/{}/log'.format(env.user))
    mongo_replica_set_init()
    time.sleep(10)
    if run('mongo {} --quiet --eval \'db.getUser(\"{}\")\''.format(env.mongodb_name, env.mongodb_user)) == 'null':
        run('mongo {} --quiet --eval \'db.createUser({{ user: \"{}\", pwd: \"{}\", roles: [\"readWrite\"]}})\''.format(env.mongodb_name, env.mongodb_user, env.mongodb_passwd))
    update()
    create_mongo_superuser()
    manage('syncdb --noinput')


@task
def prepare_configuration_files():
    require.nginx.site(
        env.domain,
        template_contents=NGINX_TPL,
        port=80,
        project_dir=env.path
    )
    require.supervisor.process(
        'django_labrepo',
        command='{}/env/bin/gunicorn wsgi --bind=127.0.0.1:8001'.format(env.path),
        directory=env.path,
        user=env.user,
        environment='LANG="ru_RU.utf8", LC_ALL="ru_RU.UTF-8", LC_LANG="ru_RU.UTF-8"',
        stdout_logfile='/home/{}/log/django-stdout.log'.format(env.user),
    )
    require.supervisor.process(
        'celery_labrepo',
        command='{}/env/bin/python manage.py celeryd --settings=settings.production'.format(env.path),
        directory=env.path,
        environment='LANG="ru_RU.utf8", LC_ALL="ru_RU.UTF-8", LC_LANG="ru_RU.UTF-8"',
        user=env.user,
        stdout_logfile='/home/{}/log/celery-stdout.log'.format(env.user),
    )
    populate_dotenv()


@task
def populate_dotenv():
    config = ConfigParser.ConfigParser()
    config.readfp(open(env.get('rcfile')))
    django_settings = config._sections['Django']
    django_settings['domain'] = env.domain
    require.files.template_file(
        path='{}/settings/.env'.format(env.path),
        template_contents=DOTENV_TPL,
        context=django_settings
        )


@task
def update():
    require.git.working_copy(env.repo_url, branch=env.branch, path=env.path)
    with cd(env.path):
        run('find . -name "*.pyc" -exec rm -f {} \;')
        with virtualenv('{}/env'.format(env.path)):
            require.python.requirements('requirements.txt')
            prepare_configuration_files()
            collectstatic()
            makemessages()
            compilemessages()
        restart()


@task
def create_mongo_superuser():
    with virtualenv('{}/env'.format(env.path)):
        manage('createmongosuperuser')


@task
def makemessages():
    with virtualenv('{}/env'.format(env.path)):
        manage('makemessages -a --ignore=env/*')
        manage('makemessages -d djangojs -a --ignore=env/*')


@task
def compilemessages():
    with virtualenv('{}/env'.format(env.path)):
        manage('compilemessages')


@task
def collectstatic():
    with virtualenv('{}/env'.format(env.path)):
        manage('collectstatic --noinput --verbosity=0')


@task
def restart():
    fabtools.supervisor.update_config()
    fabtools.supervisor.restart_process('django_labrepo')
    fabtools.supervisor.restart_process('celery_labrepo')


@task
def start():
    fabtools.supervisor.start_process('django_labrepo')
    fabtools.supervisor.start_process('celery_labrepo')


@task
def stop():
    fabtools.supervisor.stop_process('django_labrepo')
    fabtools.supervisor.stop_process('celery_labrepo')


@task
def status():
    run('supervisorctl status')


@task
def mongo_replica_set_init():
    mongo_script = 'rs.initiate( {{ "_id": "rs0", "members": [{{"_id":1, "host":"{}:{}"}}]}} )'.format(env.mongodb_host, env.mongodb_port)
    require.file('/tmp/rs_create.js', mongo_script)
    run('mongo /tmp/rs_create.js')


@task
def mongo_collection_remove(collection):
    run('mongo %s --eval "db.%s.remove()"' % (collection, env.mongodb_name))


@task
def mongo_remove_index(doc):
    run('mongo %s --eval "db.%s.dropIndex({description : 1 })"' % (doc, env.mongodb_name))


@task
def mongo_remove_all_indexes(doc):
    run('mongo %s --eval "db.%s.dropIndexes()"' % (doc, env.mongodb_name))


@task
def create_test_lab():
    with virtualenv('{}/env'.format(env.path)):
        manage('createtestlab')
