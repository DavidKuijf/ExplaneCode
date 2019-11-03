#!/bin/bash

if [ ! -d ~/reports ]
then
        mkdir ~/reports
fi

TODAY=`date +'%b[[:space:]]%d'`
YESTERDAY=`date -d "1 day ago" +'%b[[:space:]]%d'`
HTMLDAY=`date -d '1 day ago' +%Y%m%d`
REPORT_YESTERDAY=`date -d "1 day ago" +'%b_%d'`
SERIAL=`ifconfig eth0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}'`
LOGFILE="/root/reports/${SERIAL}-${REPORT_YESTERDAY}.rpt.gz"

grep "${YESTERDAY}" /var/log/daemon.log* | gzip > ${LOGFILE}

/usr/bin/curl localhost:5000 -o /var/www/html/${HTMLDAY}.html

systemctl restart flaskapp
