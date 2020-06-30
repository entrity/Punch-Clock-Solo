#!/bin/bash

MSG="$*"
# Save locally
LOG="/var/log/punch-clock-log.tsv"
echo -e "${MSG}\t$(date)" >> "$LOG"
# Save in Google Sheets
curl -L "https://script.google.com/macros/s/AKfycbyyVE3K-qXEXBgHdekpnFMznilz8Dux_zhNgQS2BJsgkBpMCK4/exec?t=${MSG}"
