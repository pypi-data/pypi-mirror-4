#!/usr/local/bin/python

"""
Library functions to re-image, patch, and prepare a (Ubunutu) server 
for use in a (cnx) dev / production environment.

Its basically trying to standardise the build of a server.

"""


import datetime
import os
import random
import pprint
import copy
import sys
import time


import fabric
from fabric.operations import put
from fabric.api import sudo, run, local, cd
from fabric.contrib import files


from err import BambooError
import fabpass


def reimage_server(image_name, server_fqdn):
    """Using pantrybell reimage a cloud server.
    """
    pass

def patch_server(server_fqdn):
    """patch update the server"""
    pass


###################### POST BOOT
def postboot():
    '''perform all base configs needed once Virtual Server is running on network.

    - make python base
    '''
    post_install()


def post_install():
    ubuntu_sys_install()

def ubuntu_sys_install(version='1.0.0'):
    '''entry point for all fabfiles that want to post boot configure an ubuntu system
    
    only one version supported right now :-)
    '''
 
    sudo('apt-get -y update')
#    sudo('apt-get upgrade')
    sys_install_nginx_ubuntu()
    sys_install_git_ubuntu()
    sys_install_pythonenv_ubuntu()

    fixsyslogclient()

    sudo('apt-get -y install emacs')
    sudo('apt-get -y install tree')

    sudo('''cat >> /tmp/mikadodeploy.log << EOF
installed on %s
installed ubuntu_sys_install version 1.0.0
EOF
''' % datetime.datetime.today().isoformat())


def sys_install_nginx_ubuntu():
    
    sudo('apt-get -y install nginx')
    for d in (confd['bamboo_www_server_root'],):
        sudo('mkdir -p -m 0777 %s' % d)


def sys_install_git_ubuntu():
    
    sudo('apt-get -y install git')

def sys_install_pythonenv_ubuntu():
    '''installing most useful python bits


    http://projects.unbit.it/uwsgi/wiki/Install
    '''

    #get easy_install
    sudo('apt-get install -y python-setuptools')
    sudo('easy_install Flask')
    sudo('easy_install pip') 
    sudo('apt-get install -y build-essential python-dev libxml2-dev python-lxml')

    sudo('pip install Fabric')
    sudo('pip install statsd')

    sudo('pip install python-openid')
    sudo('pip install flask-openid')

    

def server_install_nginx_freebsd():
    ''' '''

    raise BambooError('not yet implemented') 



def fixsyslogclient():
    '''fixes to rsyslog that should run on everything.

    server need s extra conf change to /etc/rsyslog.conf '''
    ### alter rsyslog
    files.append('/etc/rsyslog.conf', 
                 ['# Added by Fabric, fab_lxc.py/postboot()',
                  '*.* @@%s:%s' % (confd['bamboo_logserverfqdn'], 
                                   confd['bamboo_logserverport'])], 
                 use_sudo=True)


    files.comment('/etc/rsyslog.d/50-default.conf',
                  r'^.*daemon.*;mail.*;*$',
                  use_sudo=True )

    files.comment('/etc/rsyslog.d/50-default.conf',
                   r'^.*news.err;*',
                   use_sudo=True )

    files.comment('/etc/rsyslog.d/50-default.conf',
                  r'^.*\*.=debug;\*.=info;.*$',
                  use_sudo=True )

    files.comment('/etc/rsyslog.d/50-default.conf',
                  r'^.*\*.=notice;\*.=warn.*|/dev/xconsole.*$',
                  use_sudo=True )


    ### handle weird issue where container has no external response till pings internally
    files.comment('/etc/rc.local',
                  r'^exit 0$',
                  use_sudo=True )

    files.append('/etc/rc.local', 
                 ['# Added by Fabric, fab_lxc.py/postboot()',
                  'ping -c 3 www.google.com'], 
                 use_sudo=True)

    sudo('service rsyslog restart')




def ls():
    """ignore - a test function"""
    sudo("ls /root")
