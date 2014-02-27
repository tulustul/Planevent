#!/bin/sh
git checkout master
git pull openshift master
git pull origin working
git add -A
git commit -m "adding statics for openshift"
git push openshift master
git checkout working
