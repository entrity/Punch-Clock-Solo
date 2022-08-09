#!/bin/bash

set -euo pipefail

# Today or the most recent Sunday
SUNDAY=`date -d "-$(date +%w) days" +%Y-%m-%d`
LOG=/var/log/punch-clock/$SUNDAY.tsv
if ! [[ -e $LOG ]]; then
	touch $LOG
	chmod a+rw $LOG
fi
SECS_IN_40_HRS=$(( 60 * 60 * 40 ))

uri_escape () {
	jq -Rr @uri <<< "$*"
}

punch_clock () {
	local CODE="$1"
	local MSG="${@:2}"
	# Save locally
	echo -e "${CODE}\t$(date)\t${MSG}" >> "$LOG"
}

# Read clock punches from /var/log and compute stats for the current week
compute_stats () {
	WORKED_SEC=0
	TODAY_WORKED_SEC=0
	LAST_STATUS=Out
	LAST_TIME=
	LAST_TIMESTR=
	while IFS=$'\t' read STATUS TIMESTR MESSAGE; do
		INTERVAL=0
		DISPLAY_INTERVAL=
		TIME=`date -d "$TIMESTR" +%s`
		if (($TIME)) && (($LAST_TIME)); then
			INTERVAL=$(( TIME - LAST_TIME ))
		fi
		if [[ $STATUS =~ In|Out ]] && [[ $LAST_STATUS == $STATUS ]]; then
			>&2 echo "Error $STATUS followed by $LAST_STATUS ($TIMESTR)"
			>&2 printf "sudo vim %q\n" "$LOG"
			printf "sudo vim %q\n" "$LOG" | xsel -i -b
			exit 1
		fi
		if [[ $STATUS == Out ]]; then
			WORKED_SEC=$(( WORKED_SEC + INTERVAL ))
			if is_today $TIME; then
				TODAY_WORKED_SEC=$(( $TODAY_WORKED_SEC + $TIME - $LAST_TIME ))
			fi
			printf -v DISPLAY_INTERVAL "\033[32m%8s\033[0m" $(clock2str $INTERVAL)
			printf -v SUM "\033[33m%8s\033[0m" $(clock2str $WORKED_SEC)
		elif [[ $STATUS == In ]]; then
			printf -v DISPLAY_INTERVAL "\033[35m%8s\033[0m" $(clock2str $INTERVAL)
			printf -v SUM "%8s\033[0m" ""
		fi
		if [[ ${TIMESTR::3} != ${LAST_TIMESTR::3} ]]; then
			printf "\033[53m"
		fi
		printf "%-30s %s %s %s\n" "$TIMESTR" "$SUM" "$DISPLAY_INTERVAL" "$MESSAGE"
		LAST_STATUS=$STATUS
		LAST_TIME=$TIME
		LAST_TIMESTR="$TIMESTR"
	done < "$LOG"
	if [[ $LAST_STATUS == In ]]; then
		TIME=`date +%s`
		WORKED_SEC=$(( $WORKED_SEC + $TIME - $LAST_TIME ))
		if is_today $TIME; then
			TODAY_WORKED_SEC=$(( $TODAY_WORKED_SEC + $TIME - $LAST_TIME ))
		fi
	fi
	printf '%10s\t%8s\t(%s today)\n' worked `clock2str $WORKED_SEC` `clock2str $TODAY_WORKED_SEC`
	REMAIN_SEC=$(( $SECS_IN_40_HRS - $WORKED_SEC ))
	REMAIN_HR=$(( $REMAIN_SEC / 3600 ))
	REMAIN_FOR_8_HRS_TODAY=$(( 60 * 60 * 8 - $TODAY_WORKED_SEC ))
	printf '%10s\t%8s\t(%s to 8hrs)\n' remain `clock2str $REMAIN_SEC` `clock2str $REMAIN_FOR_8_HRS_TODAY`
}

is_today () {
	local FMT=%Y%m%d
	[[ `date -d @$1 +$FMT` == `date +$FMT` ]]
}

clock2str () {
	local HRS=$(( $1 / 3600 ))
	printf '%2d:%s' $HRS `date -d @$1 -u +%M:%S`
}

if ! (($#)); then
	compute_stats
elif [[ ${*,,} =~ ^in|^out ]]; then
	punch_clock $*
elif [[ ${*,,} =~ ^path ]]; then
	echo "$LOG"
elif [[ ${*,,} =~ ^edit ]]; then
	vim "$LOG"
fi
