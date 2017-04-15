#!/bin/bash

rm_ctns () {
local ctns=`sudo docker ps -a --format "{{.Names}}"`
local ctn
for ctn in $ctns
do
    sudo docker rm $ctn
done
echo RM CTNS Done!
}


stop_ctns () {
local ctns=`sudo docker ps -a --format "{{.Names}}"`
local ctn
for ctn in $ctns
do
    sudo docker stop $ctn
done
echo STOP CTNS Done!
}


rm_images () {
    local images=`sudo docker images --format "{{.ID}}"`
    local image
    for image in $images
    do
        sudo docker rmi $image
    done
    echo REMOVE IMAGES DONE!
}

if [ $1 == rmc ]
then
rm_ctns
fi
if [ $1 == stopc ]
then
stop_ctns
fi
if [ $1 == rmi ]
then
    rm_images
fi
