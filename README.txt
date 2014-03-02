planevent README
==================

Getting Started
---------------

- create two db schemas: planevent and planeventTest with collation set to utf-8

- cd <directory containing this file>

- python3 setup.py develop

- initialize_planevent_db development.ini

- npm install

To run app
# - pserve development.ini --reload
- uwsgi development.ini

To run tests
- nosetests

To build static files and run watch
- grunt dev


Requirements
------------
nodejs 0.10, ruby, python3.3, Redis, Mysql/MariaDB

- gem install compass susy


Git flow
--------
git remote add origin git@gitlab.com:Tul/planevent.git
Source code is kept on Gitlab. We have to main branches:
-working: for daily work, push it on gitlab
-master: for deploing to openshift, push it only there. It includes all static files (js, css) which normally should be built using grunt. There is a problem with node version on Openshift (they have 0.6, we require 0.10) and therefore we cannot run grunt.


Openshift
---------
http://planevent-tul.rhcloud.com/

Application is built on git push.

Openshift git repo
-git remote add openshift ssh://52e4eefe4382ecb4e6000037@planevent-tul.rhcloud.com/~/git/planevent.git/

To deploy (from origin working):
./deploy.sh
or
-git checkout master
-git pull openshift master
-git pull origin working
-git add -A
-git commit -m "adding statics for openshift"
-git push openshift master
-git checkout working (get back to working branch)
CAUTION: make sure your statics are updated with grunt and that js and css
         static files are disabled in .gitignore on master branch

To update db:
-rhc ssh planevent
-cd app-root/repo
-initialize_planevent_db production.ini

To browse logs:
-rhc tail planevent

To access redis on openshift
-rhc ssh planevent
-redis-cli -h 127.10.51.3 -p 16379 -a ZTNiMGM0NDI5OGZjMWMxNDlhZmJmNGM4OTk2ZmI5


Celery
------
to run worker
celery -A planevent.tasks worker --loglevel=info --config planevent.settings.development

to run beat
celery -A planevent.tasks beat --loglevel=info --config planevent.settings.development