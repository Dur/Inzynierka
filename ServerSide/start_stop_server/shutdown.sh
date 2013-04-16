#!/bin/bash

sudo /etc/init.d/apache2 stop

cd /home/dur/Projects/ServerSide/config
rm -f *.lock
cd pass
rm -f *.lock
cd ..
cd database_config
rm -f *.lock
