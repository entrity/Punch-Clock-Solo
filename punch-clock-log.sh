#!/bin/bash

# Today or the most recent Sunday
SUNDAY=`date -d "$day -$(date +%w) days" +%Y-%m-%d`
LOG=/var/log/punch-clock/$SUNDAY.tsv
if ! [[ -e $LOG ]]; then
	touch $LOG
	chmod a+rw $LOG
fi
SECS_IN_40_HRS=$(( 60 * 60 * 40 ))

punch_clock () {
	MSG="$*"
	# Save locally
	echo -e "${MSG}\t$(date)" >> "$LOG"
	# Save in Google Sheets
	curl -L "https://script.google.com/macros/s/AKfycbyyVE3K-qXEXBgHdekpnFMznilz8Dux_zhNgQS2BJsgkBpMCK4/exec?t=${MSG}"
}

# Read clock punches from /var/log and compute stats for the current week
compute_stats () {
	WORKED_SEC=0
	LAST_STATUS=Out
	LAST_TIME=
	while read STATUS TIMESTR; do
		TIME=`date -d "$TIMESTR" +%s`
		if [[ $STATUS =~ In|Out ]] && [[ $LAST_STATUS == $STATUS ]]; then
			>&2 echo "Error $STATUS followed by $LAST_STATUS ($TIMESTR)"
			exit 1
		elif [[ $STATUS == In ]]; then
			LAST_STATUS=$STATUS
			LAST_TIME="$TIME"
		elif [[ $STATUS == Out ]]; then
			WORKED_SEC=$(( $WORKED_SEC + $TIME - $LAST_TIME ))
			LAST_STATUS=$STATUS
			LAST_TIME="$TIME"
		fi
		printf "%-30s %3s \t%s\n" "$TIMESTR" "$STATUS" `clock2str $WORKED_SEC`
	done < "$LOG"
	if [[ $LAST_STATUS == In ]]; then
		TIME=`date +%s`
		WORKED_SEC=$(( $WORKED_SEC + $TIME - $LAST_TIME ))
	fi
	printf '%10s\t%s\n' worked `clock2str $WORKED_SEC`
	REMAIN_SEC=$(( $SECS_IN_40_HRS - $WORKED_SEC ))
	REMAIN_HR=$(( $REMAIN_SEC / 3600 ))
	printf '%10s\t%s\n' remain `clock2str $REMAIN_SEC`
}

clock2str () {
	local HRS=$(( $1 / 3600 ))
	printf '%2d:%s' $HRS `date -d @$1 -u +%M:%S`
}

if (($#)); then
	punch_clock $*
else
	compute_stats
fi
