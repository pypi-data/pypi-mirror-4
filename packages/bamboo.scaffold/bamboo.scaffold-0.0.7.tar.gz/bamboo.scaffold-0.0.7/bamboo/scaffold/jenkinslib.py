#!/usr/local/bin/python

'''
Fab file to install jenkins on a server.

This is part of the network level install for rhaptos2

wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo aptitude update
sudo aptitude install jenkins



'''

import fabric
from fabric.operations import put, open_shell, prompt
from fabric.api import sudo, run, local, env
import os

import urllib
import fabpass


def install_jenkins():
    ''' 


    '''
    sudo('apt-get install -y git') 
    sudo('apt-get install -y jenkins')
    sudo('pip install nose')
    sudo('pip install Flask')
    sudo('pip install Fabric')
    sudo('pip install pylint')
    sudo('pip install statsd')

    sudo('pip install rhaptos2.common')
    sudo('pip install bamboo.pantrybell')


def deploy_pantrybell():
    """ """
   # local("cd /usr/home/pbrian/com.mikadosoftware/pantrybell && python setup.py sdist")
    #local("cp /usr/home/pbrian/com.mikadosoftware/pantrybell/dist/pantrybell-0.0.2.tar.gz /tmp")

    #env.timeout = 30
    #env.connection_attempts = 3
    #put("/tmp/pantrybell-0.0.2.tar.gz", "/tmp/", use_sudo=True)
    bamboolib.install_python_package('bamboo.pantrybell', None, None)
    #needs config, and upostart

from  jenkinsapi import api
import sys
import jenkinsapi
import urllib2

def get_artifactURLs(server, job):

    print "getting artifact URL...", 
    try:
        ### There seems to be a bug in the code 
        d = api.get_artifacts(server, job, proxyhost="pbrian", 
                              proxyport="qwerty1")
    except:
        d = {}

    print d
#    auth = jenkinsapi.utils.urlopener.get_jenkins_auth_handler('pbrian', 'qwerty1', 
#                                                               server)
#    openr = urllib2.build_opener(auth[0])
#    urllib2.install_opener(openr)
#    d = api.get_artifacts(server, job)
    d1 = {}

    for k in d:
        d1[k] = d[k].url
    return d1

import urllib2
import base64


def grab_artifacts(server, jobname, destdir):
    print "using", server, jobname, destdir
    d = get_artifactURLs(server, jobname)
    out = []

    username = 'pbrian'
    password = 'qwerty1'
    base64string = base64.encodestring(
                   '%s:%s' % (username, password))[:-1]
    authheader =  "Basic %s" % base64string


    for k in d:
        url = d[k]
        print "retrieving", d[k]
        req = urllib2.Request(url)
        req.add_header("Authorization", authheader)
        handle = urllib2.urlopen(req)
        data = handle.read()
        open(os.path.join(destdir, k), "wb").write(data)
        out.append(os.path.join(destdir, k))
    return out

