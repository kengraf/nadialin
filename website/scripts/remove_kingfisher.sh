#!/bin/bash
#Kingfisher
#Deletes kingfisher user and removes kingfisher's groups sudo capabilities

userdel -r kingfisher
groupdel -f kingfisher

cd /etc

sed -i '/%kingfisher/d' sudoers


