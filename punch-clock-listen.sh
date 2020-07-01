#!/bin/bash

function log () {
	# /usr/local/bin/punch-clock-log.sh $*
	echo log  $*
}

gdbus monitor -y -d org.freedesktop.login1 | while read -r line; do
	if [[ $line =~ org\.freedesktop\.login1\.Session ]]; then
		if [[ $line =~ \'LockedHint\':\ \<true\> ]]; then
			log Lock
		elif [[ $line =~ \'LockedHint\':\ \<false\> ]]; then
			log Unlock
		fi
	elif [[ $line =~ org\.freedesktop\.login1\.Manager ]]; then
		if [[ $line =~ \'PowerOff\':\ \<true\> ]]; then
			log PowerOff
		elif [[ $line =~ \'Reboot\':\ \<true\> ]]; then
			log Reboot
		elif [[ $line =~ \'Suspend\':\ \<true\> ]]; then
			log Suspend
		elif [[ $line =~ \'Hibernate\':\ \<true\> ]]; then
			log Hibernate
		fi
	fi
done
