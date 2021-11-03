# Punch Clock
Keeps track of my own comings and goings, writing them to files in `/var/log`. Each week, starting Sunday, gets written to its own file.

## Usage
```bash
# Punch the clock
# <Mode> is {In|Out|...}
punch-clock-login.sh <Mode> [comment]
# Compute stats
punch-clock-login.sh
```

If the first arg is `In` or `Out`, then the punch will be used to compute the hours worked.
