# -*- coding: utf-8 -*-
import socket
import os
import imp


DEFAULTS = dict(
    project='.',
    env='%(project)s/.env',
    production=False,
    requirements='config/requirements.txt',
    virtualenv_params='',
    settings_path='config.settings',
    run='echo "add run command to config"',
    bootstrap_script='bootstrap.sh'
)


def set_defaults(config):
    for k, v in DEFAULTS.iteritems():
        if k not in config:
            config[k] = v
    return config


def make_params(config):
    for k, v in config.iteritems():
        if str == type(v) and '%(' in v:
            config[k] = v % config
    return config


def make_config(config):
    config = set_defaults(config)
    config = make_params(config)
    return config


def get_config(module, name=None):
    if str == type(module):
        if module.endswith('.py'):
            module = imp.load_source('', module)
        else:
            module = __import__(module)
    configs = dir(module)
    if 'FABRICATOR_ENV' in os.environ:
        name = os.environ['FABRICATOR_ENV']
    safe = False if name else True
    name = name if name else socket.gethostname()
    if name and name in configs:
        config = getattr(module, name)
        config['target'] = name
        return make_config(config)
    else:
        if safe:
            return make_config({})
        else:
            config_names = ', '.join(filter(lambda c: not c.startswith('__'), dir(module)))
            raise Exception('Config with name <%s> not found in module <%s>. Available configs: <%s>' % (name, module.__name__, config_names))


def fill_fabric_env(module, name=None):
    from fabric.operations import local as fabric_local, run as fabric_run
    from fabric.state import env
    config = get_config(module, name)
    env.update(config)
    env.method = fabric_run if 'ssh_host' in config else fabric_local

    if 'ssh_host' in config:
        host = config.get('ssh_host', [])
        if list == type(host):
            env.hosts = host
        else:
            env.hosts = [host]
        env.user = config.get('ssh_user', None)

        if 'ssh_pass' in config:
            env.password = config['ssh_pass']

        if 'ssh_key' in config:
            env.key_filename = config['ssh_key']
