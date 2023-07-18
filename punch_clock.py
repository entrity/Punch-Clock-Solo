#!/usr/bin/env python3

import sys, os, csv, re, subprocess
from datetime import datetime as dt
from datetime import timedelta

DT_FMT = '%a %b %d %H:%M:%S %Z %Y'
SAVE_DIR = '/var/log/punch-clock'
NOW = dt.now().astimezone()
sunday = NOW - timedelta(NOW.isoweekday())
SAVEFILE_PATH = os.path.join(SAVE_DIR, '%s.tsv' % sunday.strftime('%Y-%m-%d'))

def out(txt): sys.stdout.write(txt)
def rst(): out("\033[0m")
def overline(): out("\033[53m")

def error(msg, code=None):
	print("\033[31m%s\033[0m" % (msg), file=sys.stderr)
	if code is not None: sys.exit(code)

def clock2str(td):
	if td is None: return None
	if type(td) in (int, float): td = timedelta(seconds=td)
	hours, rem_secs = divmod(td.total_seconds(), 3600)
	mins, secs = divmod(rem_secs, 60)
	return "%2d:%02d:%02d" % (hours, mins, secs)

def parse_timestr(timestr):
	return dt.strptime(timestr.strip(), DT_FMT)

class Runner(object):
	def punch_clock(self, code, msg=None):
		with open(SAVEFILE_PATH, 'a') as f:
			timestr = NOW.strftime(DT_FMT)
			f.write('%s\t%s\t%s\n' % (code, timestr, msg))

	def calc(self):
		if os.path.exists(SAVEFILE_PATH):
			with open(SAVEFILE_PATH, 'r') as f:
				Calculator(NOW, f).calc()
		else:
			print('No log file found for this week: %s' % (SAVEFILE_PATH), file=sys.stderr)
			sys.exit(1)


class Calculator(object):
	def __init__(self, now, savefile):
		self.tsv = csv.reader(savefile, delimiter="\t")
		NOW = now

	def is_today(self, time):
		return time.date() == NOW.date()

	def calc(self):
		today_worked_secs = 0
		worked_secs = 0
		prev_status = 'Out'
		prev_time = None
		for status, timestr, message in self.tsv:
			time = parse_timestr(timestr)
			interval = time - prev_time if prev_time is not None else None

			if status in ('In', 'Out') and status == prev_status:
				vimcmd = "sudo vim %s" % (SAVEFILE_PATH)
				subprocess.run(["clip.exe"], input=bytes(vimcmd, 'utf-8'))
				error('''Error \"%s\" followed by \"%s\"\033[33m (%s)\033[0m\nCopied cmd \'%s\' to your clipboard'''
					% (status, prev_status, timestr, vimcmd))
				sys.exit(1)
			elif status == 'Out' and prev_time is None:
				error("No prev time for Out")
			elif status == 'Out':
				worked_secs += interval.total_seconds()
				if self.is_today(time): today_worked_secs += interval.total_seconds()
				acc = clock2str(worked_secs)
				human_interval = "\033[32m%8s\033[0m" % clock2str(interval)
			elif status == 'In':
				acc = ''
				human_interval = "\033[35m%8s\033[0m" % (clock2str(interval) or 'n/a')
			if prev_time is not None and prev_time.date() != time.date():
				overline() # Change of day. Add overline

			# Print one punch
			out("%-30s \033[33m%8s\033[0m %s %s\n" % (timestr, acc, human_interval, message or ''))
			prev_time, prev_status = (time, status)

		# Print summary
		overline()
		if status == 'In':
			interval = NOW - time.astimezone()
			worked_secs += interval.total_seconds()
			today_worked_secs += interval.total_seconds()
		remaining_time_for_week = timedelta(hours=40) - timedelta(seconds=worked_secs)
		remaining_time_for_day = timedelta(hours=8) - timedelta(seconds=today_worked_secs)
		out('\033[3;36m(%3s)\033[0;53m %6s\t%8s\t(%s today)\033[0m\n' % (status, 'worked', clock2str(worked_secs), clock2str(today_worked_secs)))
		out('%12s\t\033[2m%8s\t(%s to 8hrs)\033[0m\n' % ('remain', clock2str(remaining_time_for_week), clock2str(remaining_time_for_day)))

# if sys.
arg1 = sys.argv[1].lower() if len(sys.argv) > 1 else None
if arg1 is None:
	Runner().calc()
elif re.match(r'^in|^out', arg1):
	Runner().punch_clock(*sys.argv[1:])
elif re.match(r'^path', arg1):
	out('%s\n' % SAVEFILE_PATH)
elif re.match(r'^edit', arg1):
	os.execlp('vim', 'vim', SAVEFILE_PATH)
