#!/bin/bash

cp punch-clock-listen.sh /usr/local/bin && \
cp punch-clock-log.sh /usr/local/bin && \
cp punch-clock.service /etc/systemd/system && \
systemctl start punch-clock.service
