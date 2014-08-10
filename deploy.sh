#!/bin/sh

git checkout master
git pull openshift master
git pull origin working

rm instance

if [ "$1" = "production" ]
then
    REMOTE=openshift
    echo 'production' >> instance
    grunt staging
else
    REMOTE=openshift-staging
    echo 'staging' >> instance
    grunt staging
fi

git add -A
git commit -m "adding statics for openshift"
echo git push $REMOTE master
git push $REMOTE master

git checkout working
