#!/usr/local/bin/bash

export PKGNAME=rhaptos2.repo
export appnamespace=rhaptos2repo
export bamboo_appnamespace=rhaptos2repo
export BUILD_TAG=t1
export WORKSPACE=/tmp/cnx
export bamboo_modusdir=~/src/bamboo.recipies/recipies/
export bamboo_confdir=/tmp/confdir

##deployment specific
export bamboo_code_root=~/src/$PKGNAME
export bamboo_stage_root=$WORKSPACE/stage/$PKGNAME
export bamboo_archive_root=$WORKSPACE/archive
export bamboo_venvpath=$WORKSPACE/venv/$BUILD_TAG
export bamboo_xunitfilepath=$WORKSPACE/nosetests.xml
export bamboo_remote_build_root=/home/deployagent/
export bamboo_deployagent_keypath=~/.ssh/deployagent
export bamboo_deployagent=deployagent
export bamboo_www_server_root=/usr/share/www/nginx/www


export bamboo_install_to=www.frozone.mikadosoftware.com::www.frozone.mikadosoftware.com

##system globals
export bamboo_logserverfqdn=log.frozone.mikadosoftware.com
export bamboo_logserverport=5147
export ${appnamespace}_statsd_host=log.frozone.mikadosoftware.com
export ${appnamespace}_statsd_port=8125

export bamboo_userserver=http://www.frozone.mikadosoftware.com:81/user/
#URL to GET userdetails document, based on an identifier passed in after user/



export ${appnamespace}_repodir=/tmp/repo
export ${appnamespace}_www_server_name=www.frozone.mikadosoftware.com
export ${appnamespace}_cdn_server_name=www.frozone.mikadosoftware.com
export ${appnamespace}_openid_secretkey=usekeyczar
export ${appnamespace}_use_logging=Y
export ${appnamespace}_loglevel=DEBUG



