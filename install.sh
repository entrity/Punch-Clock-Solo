#!/bin/bash

if ! systemd 2>/dev/null; then
	echo 'No systemd available. Just installing limited version'
	LTD=1
fi

cp punch-clock-listen.sh /usr/local/bin && \
cp punch-clock-log.sh /usr/local/bin && \
{ (($LTD)) || cp punch-clock.service /etc/systemd/system } && \
mkdir -p /var/log/punch-clock && \
chmod o+rwx /var/log/punch-clock && \
{ (($LTD)) || systemctl start punch-clock.service } && \
echo DONE
