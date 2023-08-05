# -*- coding: utf-8 -*-
from fabric.context_managers import prefix, cd, settings
from fabric.state import env
from fabric.decorators import task
from fabric.operations import local as fabric_local, run as fabric_run, sudo
from contextlib import contextmanager
from string import Template
from fabric import colors
from fabric.contrib.console import confirm
import webbrowser
import os


@contextmanager
def virtualenv():
    with cd(env.project):
        with prefix('source %(env)s/bin/activate' % env):
            yield


@task
def sh(cmd, is_cd=True):
    if is_cd:
        with cd(env.project):
            env.method(cmd)
    else:
        env.method(cmd)


@task
def vsh(cmd):
    with virtualenv():
        sh(cmd, False)


@task
def push(message='Blank message'):
    fabric_local('git commit -a -m "%s"' % message)
    fabric_local('git push')


@task
def run(cmd=None):
    if cmd:
        vsh(env['run_' + cmd])
    else:
        vsh(env.run)


@task
def pull():
    sh('git pull')


@task
def update():
    push()
    pull()


# ====================================================================================================
# Django
# ====================================================================================================
@task
def dj(cmd):
    vsh('export FABRICATOR_ENV="%s" && python manage.py %s --settings %s' % (env.target, cmd, env.settings_path))


@task
def sync():
    dj('syncdb --noinput')


@task
def static():
    dj('collectstatic --noinput')


@task
def requirements():
    with virtualenv():
        sh('pip install -r %(requirements)s' % env)


@task
def virtualenv_init():
    sh('virtualenv %(virtualenv_params)s %(env)s' % env)


@task
def init():
    if env.production:
        sh('mkdir -p %s' % env.project, False)
        sh('git clone %s .' % env.repository)
    virtualenv_init()
    requirements()


@task
def tests(cv=False):
    with settings(warn_only=True):
        update()
    params = '--with-coverage --cover-html' if cv else ''
    vsh('nosetests -s %s' % params)


@task(alias='make_admin')
def create_superuser(user='admin', email='admin@admin.com'):
    dj('createsuperuser --username %s --email %s' % (user, email))


@task(alias='south_schema')
def south_schema_migration():
    for app in env.migration_apps:
        dj('schemamigration %s --initial' % app)


@task(alias='south_migrate')
def south_migrate(app=None):
    if app:
        dj('migrate %s' % app)
    else:
        dj('migrate')


@task
def fixture(name):
    dj('generate_fixture %s.test_data' % name)


@task(alias='import_dump_pg')
def import_dump_postgresql(dump):
    env.method('PGPASSWORD=%(PASSWORD)s psql -U %(USER)s %(NAME)s < ' % env.postgresql + dump)


# ====================================================================================================
# Supervisor
# ====================================================================================================
@task(alias='sv_cmd')
def supervisor_cmd(cmd):
    sudo('supervisorctl %s' % cmd)


@task(alias='sv_status')
def supervisor_status():
    supervisor_cmd('status')


@task(alias='sv_tail')
def supervisor_tail(service):
    supervisor_cmd('tail %s' % service)


@task(alias='sv_stop')
def supervisor_stop(service):
    supervisor_cmd('stop %s' % service)


@task(alias='sv_start')
def supervisor_start(service):
    supervisor_cmd('start %s' % service)


@task(alias='sv_restart')
def supervisor_restart(service):
    supervisor_cmd('restart %s' % service)


# ====================================================================================================
# Mongodb
# ====================================================================================================
@task(alias='mdb_cmd')
def mongodb_run_command(cmd):
    env.method('echo "%s" | mongo' % cmd)


@task(alias='mdb_web')
def mongodb_open_web_console():
    webbrowser.open('http://%s:28017' % env.ssh_host)


@task(alias='mdbrs_init')
def mongodb_replicaset_init():
    mongodb_run_command('rs.initiate();')


@task(alias='mdbrs_status')
def mongodb_replicaset_status():
    mongodb_run_command('rs.status();')


@task(alias='mdbrs_add')
def mongodb_replicaset_add(host):
    mongodb_run_command("rs.add('%s');" % host)


@task(alias='mdbrs_info')
def mongodb_replicaset_info():
    mongodb_run_command('rs.isMaster();')


@task(alias='mdbrs_conf')
def mongodb_replicaset_conf():
    mongodb_run_command('rs.conf();')


# ====================================================================================================
# Remote servers
# ====================================================================================================
def get_script(filename, **kwargs):
    template = open('files/' + filename).read()
    if kwargs:
        return Template(template).substitute(**kwargs)
    else:
        return template


@task(alias='srv_launch')
def server_launch(user=None, password=None):
    if 'vagrant' == env.cloud_type:
        server = env.server
        dir = '/tmp/%s' % server
        if not os.path.exists(dir):
            os.mkdir(dir)
        if os.path.exists('%s/Vagrantfile' % dir):
            print colors.red('Machine <%s> exists.' % server)

        fabric_local('cd %s && echo "%s" > Vagrantfile' % (dir, get_script('Vagrantfile',
            host=server,
            ip_addr=env.ssh_host
        )))
        fabric_local('cd %s && vagrant up' % dir)
    elif 'vps' == env.cloud_type:
        env.user = user if user else env.user
        if password:
            env.password = password
            env.key_filename = None

    bootstrap_script = get_script(
        env.bootstrap_script,
        puppet_source=env.repository,
        user=env.ssh_user,
        sshd_config=get_script('sshd_config'),
        vcs_known_hosts=get_script('vcs_known_hosts'),
        vcs_deploy_public=get_script('vcs_deploy_public'),
        vcs_deploy_private=get_script('vcs_deploy_private'),
    )

    fabric_run('echo "%s" > bootstrap.sh' % bootstrap_script)
    sudo('chmod +x bootstrap.sh && ./bootstrap.sh')


@task(alias='srv_apply')
def server_apply():
    sudo('cd /etc/puppet && git pull')
    sudo('cd /etc/puppet && git submodule update --init --recursive')
    sudo('puppet apply /etc/puppet/manifests/init.pp')


@task
def ssh():
    if 'vagrant' == env.cloud_type:
        fabric_local('cd /tmp/%s && vagrant ssh' % env.server)
    elif 'vps' == env.cloud_type:
        fabric_local('ssh %(ssh_user)s@%(ssh_host)s -i %(ssh_key)s' % env)


@task(alias='srv_reboot')
def server_reboot():
    if 'vagrant' == env.cloud_type:
        fabric_local('cd /tmp/%s && vagrant reload' % env.server)


@task(alias='srv_stop')
def server_stop():
    if 'vagrant' == env.cloud_type:
        fabric_local('cd /tmp/%s && vagrant halt' % env.server)


@task(alias='srv_start')
def server_start():
    if 'vagrant' == env.cloud_type:
        fabric_local('cd /tmp/%s && vagrant up' % env.server)


@task(alias='srv_destroy')
def server_destroy():
    if confirm(colors.red('Destroy machine <%s> (Danger operation!!!!!!!)' % env.server)):
        if 'vagrant' == env.cloud_type:
            dir = '/tmp/%s' % env.server
            fabric_local('cd %s && vagrant destroy' % dir)
            fabric_local('rm -rf %s' % dir)
