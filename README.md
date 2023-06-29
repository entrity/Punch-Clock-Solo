# Punch Clock
Keeps track of my own comings and goings, writing them to files in `/var/log`. Each week, starting Sunday, gets written to its own file.

## Usage
```bash
# Punch the clock
# <Mode> is {In|Out|...}
punch-clock-log.sh <In|Out> [comment]
# Echo path to log file
punch-clock-log.sh path
# Open vim on log file
punch-clock-log.sh edit
# Compute stats
punch-clock-log.sh
```

If the first arg is `In` or `Out`, then the punch will be used to compute the hours worked.

## Installation
`sudo ./install.sh`

## Listen
`punch-clock-listen.sh` is not maintained but was used at one point to automatically record punches when the system hibernated, etc.
