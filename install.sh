#!/bin/bash

cp punch-clock-listen.sh /usr/local/bin && \
cp punch-clock-log.sh /usr/local/bin && \
cp punch-clock.service /etc/systemd/system && \
mkdir -p /var/log/punch-clock && \
chmod o+rwx /var/log/punch-clock && \
systemctl start punch-clock.service
