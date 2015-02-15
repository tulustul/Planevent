#!/bin/bash

trap "handle_user_interrupted" INT

RED='tput setaf 1'
GREEN='tput setaf 2'
RESET='tput sgr0'

VIRTUALENV_NAME = 'planevent'

function handle_user_interrupted {
	warn 'User interrupted'
	fail
}

function fail {
	warn 'Failed due to previous errors'
	exit
}

function info {
	echo $(${GREEN})${1}$(${RESET})
}

function warn {
	echo $(${RED})${1}$(${RESET})
}

info 'Installing system dependencies'
sudo apt-get install python3-pip python3-dev mariadb-server redis-server nodejs npm ruby ruby-dev gem -y
if [ $? -ne 0 ]; then
	warn 'Cannot install system dependencies'
	fail
fi

sudo ln -s /usr/bin/nodejs /usr/bin/node

# info 'Configuring virtualenv'
# export WORKON_HOME=~/.envs
# mkdir -p $WORKON_HOME
# export VIRTUALENVWRAPPER_PYTHON=$(which python3)
# source /usr/local/bin/virtualenvwrapper.sh

# info 'Switching to virtualenv'
# workon $VIRTUALENV_NAME
# if [ $? -ne 0 ]; then
# 	warn 'Virtualenv not created.'
# 	info 'Creating virtualenv'
# 	mkvirtualenv $VIRTUALENV_NAME
# 	if [ $? -ne 0 ]; then
# 		warn 'Cannot create virtualenv'
# 		fail
# 	fi
# fi

info 'Installing python dependencies'
python3 setup.py develop
if [ $? -ne 0 ]; then
	warn 'Cannot install python dependencies'
	fail
fi

info 'Installing nodejs dependencies'
npm install
if [ $? -ne 0 ]; then
	warn 'Cannot install nodejs dependencies'
	fail
fi

info 'Installing bower dependencies'
./node_modules/.bin/bower install
if [ $? -ne 0 ]; then
	warn 'Cannot install bower dependencies'
	fail
fi

info 'Installing ruby dependencies'
sudo gem install sass compass
if [ $? -ne 0 ]; then
	warn 'Cannot install bower dependencies'
	fail
fi

info 'Installed successfully'
info 'Build frontend with'
info './node_modules/.bin/grunt dev'
info 'for development'
info 'and run'
info 'uwsgi development.ini'
info 'to run server'
