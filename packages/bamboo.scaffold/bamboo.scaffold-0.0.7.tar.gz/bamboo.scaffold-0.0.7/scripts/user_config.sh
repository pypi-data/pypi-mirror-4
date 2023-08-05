
export bamboo_projectname=rhaptos2.user
export bamboo_appnamespace=rhaptos2user

export BUILD_TAG=t1
export WORKSPACE=/tmp/cnx
export bamboo_modusdir=~/src/bamboo.recipies/recipies/
export bamboo_confdir=/tmp/confdir


export bamboo_code_root=~/src/$bamboo_projectname
export bamboo_stage_root=$WORKSPACE/stage/$bamboo_projectname
export bamboo_archive_root=$WORKSPACE/archive
export bamboo_venvpath=$WORKSPACE/venv/$BUILD_TAG
export bamboo_xunitfilepath=$WORKSPACE/nosetests.xml

export bamboo_remote_build_root=/home/deployagent/
export bamboo_deployagent_keypath=~/.ssh/deployagent
export bamboo_deployagent=deployagent
export bamboo_www_server_root=/usr/share/www/nginx/www
export bamboo_logserverfqdn=log.frozone.mikadosoftware.com
export bamboo_logserverport=5147
export bamboo_install_to=www.frozone.mikadosoftware.com::www.frozone.mikadosoftware.com
export bamboo_statsd_host=log.frozone.mikadosoftware.com
export bamboo_statsd_port=8125


export ${bamboo_appnamespace}_www_server_name=www.frozone.mikadosoftware.com
export ${bamboo_appnamespace}_cdn_server_name=www.frozone.mikadosoftware.com
export ${bamboo_appnamespace}_use_logging=Y
export ${bamboo_appnamespace}_loglevel=DEBUG



