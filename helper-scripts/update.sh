#!/bin/bash

BASEDIR="/root/ExplaneCode/helper-scripts"

######
# Check for new update script 
######
if [ ${BASEDIR}/update.sh -nt /root/update.sh ]
then
	echo "New update script found then installed : update"
	cp -p ${BASEDIR}/update.sh /root/update.sh
fi

######
# Check for new report script 
######
if [ ${BASEDIR}/report.sh -nt /root/report.sh ]
then
	echo "New report script found then installed : update"
	cp -p ${BASEDIR}/report.sh /root/report.sh
fi


######
# check out new version 
# check requirements and install new modules if needed
# restart explane daemon
######
cd ~/ExplaneCode
#git checkout dev-branch
git pull
pip3 install -r requirements.txt -t .

cd ~/ExplaneCode/flaskapp
pip3 install -r requirements.txt -t .

systemctl daemon-reload  
systemctl restart explane

######
# copy files for the explane service 
######
if [ ! -f /etc/systemd/system/explane.service ]
then 
	echo "explane service script does not exist : install"
	cp -p ${BASEDIR}/explane.service /etc/systemd/system/explane.service
	cp -p ${BASEDIR}/explane.logrotate /etc/logrotate.d/explane
	systemctl daemon-reload  
	systemctl enable explane
	systemctl start explane
elif [ ${BASEDIR}/explane.service -nt /etc/systemd/system/explane.service ]
then
	echo "explane service script newer then installed : update"
	cp -p ${BASEDIR}/explane.service /etc/systemd/system/explane.service
        cp -p ${BASEDIR}/explane.logrotate /etc/logrotate.d/explane
	systemctl daemon-reload  
	systemctl enable explane
	systemctl restart explane
fi

######
# copy files for the flaskapp service 
######
if [ ! -f /etc/systemd/system/flaskapp.service ]
then 
	echo "flaskapp service script does not exist : install"
	cp -p ${BASEDIR}/flaskapp.service /etc/systemd/system/flaskapp.service
	systemctl daemon-reload  
	systemctl enable flaskapp
	systemctl start flaskapp
elif [ ${BASEDIR}/flaskapp.service -nt /etc/systemd/system/flaskapp.service ]
then
	echo "flaskapp service script newer then installed : update"
	cp -p ${BASEDIR}/flaskapp.service /etc/systemd/system/flaskapp.service
	systemctl daemon-reload  
	systemctl enable flaskapp
	#systemctl restart flaskapp
fi


######
# copy files for the autousb mounter
######
if [ ! -f /usr/local/bin/usb-mount.sh ]
then
	echo "usb-mount shell script does not exist : install" 
	cp -p ${BASEDIR}/usb-mount.sh /usr/local/bin/usb-mount.sh
elif [ ${BASEDIR}/usb-mount.sh -nt /usr/local/bin/usb-mount.sh ]
then
	echo "usb-mount shell script newer then installed : update"
	cp -p ${BASEDIR}/usb-mount.sh /usr/local/bin/usb-mount.sh
fi

if [ ! -f /etc/udev/rules.d/99-usb-mounter.rules ]
then 
	echo "udev rules does not exist : install"
	cp -p ${BASEDIR}/99-usb-mounter.rules /etc/udev/rules.d/99-usb-mounter.rules
	udevadm control --reload-rules
elif [ ${BASEDIR}/99-usb-mounter.rules -nt /etc/udev/rules.d/99-usb-mounter.rules ]
then
	echo "udev rules is newer then installed : update"
	cp -p ${BASEDIR}/99-usb-mounter.rules /etc/udev/rules.d/99-usb-mounter.rules
	udevadm control --reload-rules
fi

if [ ! -f /etc/systemd/system/usb-mount@.service ]
then 
	echo "usb-mount service script does not exist : install"
	cp -p ${BASEDIR}/usb-mount@.service /etc/systemd/system/usb-mount@.service
	systemctl daemon-reload  
elif [ ${BASEDIR}/usb-mount@.service -nt /etc/systemd/system/usb-mount@.service ]
then
	echo "service script newer then installed : update"
	cp -p ${BASEDIR}/usb-mount@.service /etc/systemd/system/usb-mount@.service
	systemctl daemon-reload  
fi

######
# Check for new crontab
######
/usr/bin/crontab -l > /tmp/crontab.tmp
cmp -s /tmp/crontab.tmp ${BASEDIR}/crontab.txt
DELTA=$?

if [ ${DELTA} -eq 0 ]
then
	echo "No new crontab"
elif [ ${DELTA} -ne 0  ]
then
	echo "New crontab found"
	crontab ${BASEDIR}/crontab.txt
fi
rm /tmp/crontab.tmp

######
# Check for new nginx config
######
if [ ${BASEDIR}/nginx-default -nt /etc/nginx/sites-enabled/default ]
then
	echo "nginx config newer then installed : update"
	cp -p ${BASEDIR}/nginx-default /etc/nginx/sites-enabled/default
	systemctl restart nginx
fi

