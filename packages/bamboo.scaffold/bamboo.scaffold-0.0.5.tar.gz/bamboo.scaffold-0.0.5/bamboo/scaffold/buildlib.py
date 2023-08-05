#!/usr/local/bin/python
#! -*- coding: utf-8 -*-



'''

THese are genericm,python package staging and building scripts with a venv testing 


'''
#batteries
import os
import time
#pypi
import fabric
from fabric.operations import put
from fabric.api import sudo, run, local, cd, settings, lcd, execute, roles, env
import pprint

#cnx
from bamboo.scaffold.err import BambooError
import fabpass
import bamboo.scaffold




def stage(code_root=None, stage_root=None):

    """
    given the root of a working copy of a (python package) and root of a
    staging directory (can do anything to that) move code into staging.

    take code to be built from source root and present it 
    to stage root.  The assumptiuon is we will need this step
    when it is necessary to apply patches to code before building it.
    Third party integrations are likely step here.(Aloha)

    example: code_root=~/rhaptos2.repo/ stage_root=/tmp/stage/rhaptos2.repo

    return: count of files moved excl SCM files.
    
    """
    if (not code_root or not stage_root): 
        raise BambooError("null stage or code root")

    #first, clean up the tgt folder.
    if os.path.isdir(stage_root) is True:
        local('rm -rf %s' % stage_root) 

    local('mkdir -p -m 0755 %s' % stage_root) 

    local('cp -r %s/* %s/' % (code_root, stage_root))

    local('rm -rf %s' % os.path.join(stage_root, '.git')) 
    ct = local("find %s -type f | wc -l" % stage_root, 
                                            capture=True)
    return ct

    

def build(stage_root=None, archive_root=None):
    """
    given stage dir of (python package) build the package store the egg, 
    return useful details

    return (python pkg name, pkgname with version, location of tar.gz)

    """
    if not stage_root: raise BambooError("cannot build, Null stage_root")

    with lcd(stage_root):
        local("python setup.py sdist")
        pkgname = local("python setup.py --fullname", capture=True)
        pkgball = pkgname + ".tar.gz"
        local("mkdir -p -m 0755 %s" % archive_root)
        local("cp dist/%s %s/" % (pkgball, archive_root))

    return  (pkgname.split("-")[0],
             pkgname,
             os.path.join(archive_root, pkgball)) 


def venv(pkgname=None, venvpath=None, artifact_path=None, xunitfilepath=None):
    """
    create a virtualenv, install the python pkg, run nose tests and output.

     
    """
    try:
        vbin = local("whereis virtualenv", capture=True)
        vbin = vbin.split()[1] ##virtualenv: /usr/local/bin/virtualenv
    except:
        vbin = "virtualenv" ##todo: this needs re-evaluating.


    if not os.path.isfile("%s/bin/python" % venvpath):
        #no venv yet - create it and populate
        local("mkdir -p -m 0755 %s" % venvpath)
        local("%s  %s" % (vbin,venvpath))   
        local("%s/bin/pip install %s" % (venvpath, artifact_path))    
        local("%s/bin/pip install nose" % (venvpath, artifact_path))    
    else:
        #dont waste time reinstalling venv and deps.  Just do pkg
        local("%s/bin/pip install --no-deps --ignore-installed %s" % (venvpath, artifact_path))

    if xunitfilepath:
        local("%s/bin/nosetests --with-doctest --doctest-extension=txt --doctest-tests --verbosity=3 --with-xunit --xunit-file %s %s" % (venvpath, xunitfilepath, pkgname))
    else:
        local("%s/bin/nosetests --with-doctest --doctest-extension=txt --doctest-tests --verbosity=3 %s" % (venvpath, pkgname))

    
    return {"bamboo_testresults":None}



def restart_nginx():
    sudo('/etc/init.d/nginx restart')




        
def install_cdn():

    '''Static server for tiny. 
    THe app specific html and js is served
    through www.'''

    remote_init(['/usr/share/www/nginx/cdn',])
    sudo('chown -R www-data:www-data /usr/share/www/nginx/cdn')

    put(os.path.join(LOCALSTAGEDIR, 'bamboo/conf.d/nginx/nginx.conf'),
                '/etc/nginx/nginx.conf', use_sudo=True, mode=0755)
    put(os.path.join(LOCALSTAGEDIR, 'bamboo/conf.d/nginx/cdn.conf'), 
                '/etc/nginx/conf.d/', use_sudo=True, mode=0755)
    restart_nginx()

def push_tiny_to_cdn():
    '''timeconsuming thirdparty stuff that never changes '''
    put(os.path.join(confd['bamboo_stage_root'], 'tinymce'),
        '/usr/share/www/nginx/cdn', use_sudo=True, mode=0755)
    restart_nginx()

####### /component: CDN 


####### component: LOADBAL

def install_loadbal():
    '''  '''
    put(os.path.join(LOCALSTAGEDIR, 'bamboo/conf.d/nginx/nginx.conf'),
                '/etc/nginx/nginx.conf', use_sudo=True, mode=0755)

    put(os.path.join(LOCALSTAGEDIR, 'bamboo/conf.d/nginx/www.conf'), 
                '/etc/nginx/conf.d/', use_sudo=True, mode=0755)
    restart_nginx()

####### /component: LOADBAL

def install_resultant_config_file():

    ''' take the current confd, and put it into remote server, 
    as /etc/rhaptos2.ini   
    Want to be more =selective about this in the end'''
    import ConfigParser

    config = ConfigParser.SafeConfigParser()
    config.optionxform = str     #case sensitive    

    config.add_section('rhaptos2')
    for k in confd:
        config.set('rhaptos2', k, confd[k])

    # Writing our configuration file to 'example.cfg'
    with open('/tmp/example.ini', 'wb') as configfile:
        config.write(configfile)

    put("/tmp/example.ini", 
        confd['remote_configfile'],
        use_sudo=True, mode=0755)



def install_pkg(pkgname, localpath=None, url=None):
    """ """
    """ Just install the pkg, from jenkins (!)

    Not sure hwo to install from developer local machine...
    >>> newinstall(localpath="/tmp/foo.tgz")

    """

    if localpath:
        basenm = os.path.basename(localpath)               
        put(localpath,  '/tmp',
            use_sudo=True, mode=0755)
        ##work around for nose
        sudo("pip uninstall -y nose || echo 'Nose not installed'")
        sudo("rm -f /usr/local/man")
        sudo("pip install --no-deps --ignore-installed %s" % os.path.join('/tmp', basenm))
        sudo("ls -l /tmp")
    
    if url:
         sudo("pip install --no-deps --ignore-installed %s" % url)


    return {}



def myput(t):
    put(t, '/etc/init/rhaptos2.repo.conf',
           use_sudo=True, mode=0755)
    

def start_upstart(servicename, **kwds):
    """ 
    """
    cmd = "%s " % servicename
    for k in kwds:
        cmd += " %s=%s " % (k,kwds[k])
    fullcmd = "sudo initctl start %s || sudo initctl restart %s" % (cmd, cmd)
    sudo(fullcmd)
    
def stop_upstart(servicename, **kwds):
    '''On a system that has rhaptos2 and the upstart, stop the service '''
    cmd = "%s " % servicename
    for k in kwds:
        cmd += " %s=%s " % (k,kwds[k])
    fullcmd = "sudo initctl stop %s || echo %s is not running" % (cmd, cmd)
    sudo(fullcmd)

def install_upstart(proj, confd, port=None):
    """ An alias for upstart() """
    return upstart(proj, confd, port=None)

def upstart(proj, confd, port=None):
    """ install onto ubunut a upstart tmpl """

    recipiedir = os.path.dirname(bamboo.scaffold.__file__)
    confdir = os.path.join(recipiedir, "tmpls")
    templates = [os.path.join(confdir, tmpl) for tmpl in os.listdir(confdir)]
    tmpl_repo = os.path.join(confdir, "upstart-rhaptos2.conf")

    tmpl = open(tmpl_repo).read()
    open("/tmp/foo.t", "w").write(tmpl % confd)

    execute(myput, "/tmp/foo.t")







