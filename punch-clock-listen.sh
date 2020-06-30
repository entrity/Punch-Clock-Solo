#!/bin/bash

function log () {
	/usr/local/bin/punch-clock-log.sh $*
}

gdbus monitor -y -d org.freedesktop.login1 | while read -r line; do
	if [[ $line =~ LockedHint ]]; then
		if [[ $line =~ \<true\> ]]; then
			log Lock
		elif [[ $line =~ \<false\> ]]; then
			log Unlock
		fi
	fi
done
