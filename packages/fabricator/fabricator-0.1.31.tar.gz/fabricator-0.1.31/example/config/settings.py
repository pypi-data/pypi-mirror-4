# -*- coding: utf-8 -*-

# Config for remote server with ssh key authentication
hostname1 = dict(
    ssh_host='111.222.333.444',
    ssh_user='user',
    ssh_key='/path/to/private/ssh/key/id_rsa'
)

# Config for remote server with ssh password authentication
hostname12 = dict(
    ssh_host='111.222.333.444',
    ssh_user='user',
    ssh_pass='password'
)


digitaldemiurge = dict(
    ssh_host='10.10.10.2',
    ssh_user='vagrant',
    ssh_key='/home/vitalis/.vagrant.d/insecure_private_key'
)
