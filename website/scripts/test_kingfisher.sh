#!/bin/bash
#Kingfisher
#Test ssh connection if connected should utilize keys and copy, if not prompted for password and denied
scp -i /home/kingfisher/.ssh/key -o StrictHostKeyChecking=no kingfisher@localhost:/home/kingfishe/.ssh/authorized_keys pub

