#!/usr/local/bin/python
#! -*- coding: utf-8 -*-

'''
main bamboo script.

When running bamboo, you are intending to execute a recipie or python script
that will do one of 

* stage
* build
* unittest
* deploy
* functionaltest
* uxtest

This is done by calling ::

  bamboo.py <recipiename> <command> <command> <command>

  bamboo.py rhaptos2_repo --stage --build --unittest


Bamboo expects a number of environment variables to be set.

A
 recipie is a python module, stored out of sys.path if needed
that supplies one or all of functions stage(), build(),

  Each function needs to take "confdict" as an argument,
  confdict will be a dictionary holding the needed environment variables

 

'''

from optparse import OptionParser
import os, sys
import imp
from rhaptos2.common import conf
import inspect
import pprint
import types
import copy
import json
from fabric.api import env, run, execute, local
import datetime
import fabric.state

from bamboo.scaffold import fabpass


class BambooError(Exception):
    pass

def dict_diff(dA, dB):
    """
    Managing config - given "before" and "after" dicts, return diff.

    return three tuple of  dicts of the differences in the config object 
    before and after a step.

    >>> expectedval = ({'c': 3}, {'a': 1}, {'b': '2->4'})        
    >>> da = {'a':1, 'b':2}
    >>> db = {'c':3, 'b':4}
    >>> testd = dict_diff(da, db)
    >>> assert testd == expectedval

    """
    addedd = {}
    removedd = {}
    changedd = {}

    #assume I am reciveing dicts!
    if not isinstance(dA, types.DictType): raise BambooError("First param must be a dict")
    if not isinstance(dB, types.DictType): return dA
 
    #first find keys that are different:
    #we have two dicts now.
    #Ohh Err Missus
    removedkeys = set(dA) - set(dB)    
    addedkeys = set(dB) - set(dA)
    unchangedkeys = set(dA) & set(dB)
    keysofchangedvals = [k for k in unchangedkeys if dA[k] != dB[k]]

    for k in removedkeys: 
        removedd[k] = dA[k]
    for k in addedkeys:
        addedd[k] = dB[k]

    for k in keysofchangedvals:
        changedd[k] = "%s->%s" % (dA[k], dB[k])
        
    return (addedd, removedd, changedd)

def pprint_dict_diff(addedd, removedd, changedd):
    """
    given the diff between "before" and "after" dicts, prettify output


    #formatting problem for doctest - TODO
    >> pprint_dict_diff({'c': 3}, {'a': 1}, {'b': '2->4'})
    #'***+ c:3\\n- a:1\\n> b: 2->4\\n***'    
    """
    s = "***\n"
    for k in addedd:
        s += "+ %s:%s\n" % ( k, addedd[k] )

    for k in removedd:
        s += "- %s:%s\n" % (k, removedd[k]) 

    for k in changedd:
        s += "> %s: %s\n" % (k, changedd[k])

    s += "***\n"
    return s



def parse_args():

    usage = "usage: %prog --recipie <modulename> [stage|build|test|deploy|functest|uxtest]"
    parser = OptionParser()
    parser.add_option("-r", "--recipie", dest="recipie", 
     help="Give the name of the python module that when imported is a recipie")

    valid_args = ["stage", "build", "test", "deploy", "functest", "uxtest"] 
    found_args = []

    (options, args) = parser.parse_args()
    if not options.recipie :
        print usage
        sys.exit()

    for arg in args:
        if arg not in valid_args:
            raise BambooError("Argument %s is not valid" % arg)
        else:
            found_args.append(arg)

    #sort found args?    
    return (options, found_args)

def sort_arg():
    pass

def validate_recipie():
    """
    in the namespace we have CurrentRecipie
    This should provide build(), stage() etc etc.
    Check that it does

    return message and t/f
    """
    msg = "The module %s needs to provide functions named "
    ok = True
    valid_args = ["stage", "build", "test", "deploy", "functest", "uxtest"]
    for arg in valid_args:
        if not hasattr(CurrentRecipie, arg):
            msg += " %s " % arg
            ok = False

    msg += ". It is possible to use defaults in bamboo.scaffold. Please see docs"
    return (ok, msg)




def dumpconf(confd, changes, shareddir):
    """ """
    try:
        js = json.dumps(confd, sort_keys=True, indent=4)
        open(os.path.join(shareddir, "conf.json"), "w").write(js)
        open(os.path.join(shareddir, "history.json"), "a").write(changes)
    except:
        pass#!!!!


def loadconf(shareddir):
    try:
        s = open(os.path.join(shareddir, "conf.json"), 'r').read()
        d = json.loads(s)
    except:
        d = {}

    return d


def handle_buildtag(confd):
    """Called at start of build (stage), ensures correct buildtag will follow change

    We assume all builds / tests relate to a code change in the component
    We will either get the code change from the SCM (git) as a commit ID
    or we will assume we are on a deeloper machine under development, and
    so just use todays date - the idea is development is entrirely serial 
    so can be just repeated over and again
    
    """
    if "JENKINS_URL" in os.environ:
        #we are in jenkins env (assume!)
        confd['bamboo_trackid'] = os.environ['GIT_BRANCH'] + "-" + os.environ['GIT_COMMIT']

    else:
        confd['bamboo_trackid'] = "dev-" + str(datetime.datetime.today().strftime("%Y%m%d"))

    confd['bamboo_curr_artifact_dir'] = os.path.join(confd['bamboo_archive_root'],
                                               confd['bamboo_trackid'])
    
    local("mkdir -p -m 0755 %s" % confd['bamboo_curr_artifact_dir'])

    return confd

def set_verbosity():
    """ """
    

    fabric.state.output['stdout'] = False
    fabric.state.output['user'] = False
    fabric.state.output['warnings'] = False
    fabric.state.output['running'] = False


def main():
    '''
    This is the main deployment script for bamboo.
    
    $ bamboo.py --recipie rhaptos2 stage build test deploy functest uxtest

    bamboo.py will pull in from os.environ the current config, 
    namespaced by bamboo_ and <recipiename>_
   
    It will then import a recipie of name <recipiename>, where that recipie 
    should be a python module (not necessarily on PYTHONPATH) that supplies the 
    six functions build(confd), test(confd), stage(confd) etc.

    Each function will pass *in* a dictionary representing the configuration,
    and pass back out the dictionary, altered as maybe by the process.

    This altered dict is then stored onto local disk and passed to the next invocation
    of stage / build / etc.


    scaffold libraries supply default actions to stage build etc.


    stage(confd): default: copy the (python) code from
                           bamboo_code_root and put in
                           bamboo_stage_root, remove SCM markers Will
                           insert a valid bamboo_buildtag.  It is
                           assumed stage is alwasy the first process
                           after a code change, so bamboo_buildtag
                           will follow that change through till the end.
                           bamboo_curr_artifact_dir is where we put artifcats

    build(confd): default: run python setup.py sdist
                           store the location of the tar.gz in bamboo_buildtag

    test(confd): default: locally instantiate a virtualenv, and pip install
                          the artifcat from build process.  
                          Run nose across the package, collecting doctests, 
                          nosetests and unittests.
     
    deploy(confd): default: cp tar to remote hosts as specified in bamboo_installto
                            Optionally create upstart conf file to run / moniotr the
                            service.
                            There is an assumption that all
                            "backing services" have been created.
                            More work needed

    functest(confd): default: run nose, on the above venv, looking specifically
                              for functest marked tests, presumption is these are 
                              network based integration tests testing the deploy 

    uxtest(confd): Default: run specific splinter / selenioum based tests on a X
                            enabled server.



    
    '''
    global CurrentRecipie

    opts, args = parse_args()
    modname = opts.recipie

    
    set_verbosity() 
    
    ##get namspeaces of bamboo and whatever name of this recipie is
    confdict = conf.get_config(["bamboo", opts.recipie])
    confdict = handle_buildtag(confdict)

    onfileconf = loadconf(confdict["bamboo_curr_artifact_dir"])
    onfileconf.update(confdict) ##right way round???
    confdict = onfileconf ##env takes precendance over disk

    print "Conf checking *********"
    pprint.pprint(confdict)
    print "opts.recipie, used as namesapce", opts.recipie
        

    #set the keypaths used (only one key for whole deploy - not great)
    fabpass.setpass(confdict)
    
    modus_dirs = [confdict['bamboo_modusdir'],]

    ### Find a module named modname, in the dirs named modus_dirs
    try:
        found_module = imp.find_module(modname, modus_dirs)
    except ImportError:
        print "Unable to find an importable recipie named %s in %s" % (modname, 
                             str(modus_dirs))
        sys.exit()

    try:
        filehandle, fpath, desc = found_module
        CurrentRecipie = imp.load_module(modname, filehandle, fpath, desc)
    finally:
        filehandle.close()

    #validate recipie has necessary functions.
    ok, msg = validate_recipie()
    if not ok: 
        print msg % modname
        sys.exit()

    ordered_args = ["stage", "build", "test", "deploy", "functest", "uxtest"]
    for orderedarg in ordered_args:   
        if orderedarg in args:


            snapshotd = copy.deepcopy(confdict)

            #At this point we *may* change desired target dirs.
            if orderedarg == "deploy":
                env.hosts = confdict['bamboo_install_to'].split("::")

            print "[Bamboo is Running %s from recipie %s]" % (orderedarg, opts.recipie)
            print "[Bamboo will target hosts: %s]" % env.hosts 

            ##every call to stage, build etc should accept and return
            ##confd.  However confd is updated in place, so bit of
            ##workaround to catch all cases and that execute will
            ##return a output for each env it ran on.

            newdicts = execute(getattr(CurrentRecipie, orderedarg), confdict)

            #we have now got back a confd (returned by stage()) but
            # keyed on the host it was run.  so we *coudl* get back
            # multiple confds
            for host in newdicts:
                newdict = newdicts[host]
                addedd, removedd, changedd = dict_diff(snapshotd, newdict)
                changes = pprint_dict_diff(addedd, removedd, changedd)
                print changes 
                confdict.update(newdict)
                dumpconf(confdict, changes, confdict["bamboo_curr_artifact_dir"])  
    

if __name__ == '__main__':
    main()
    #import doctest
    #doctest.testmod()



