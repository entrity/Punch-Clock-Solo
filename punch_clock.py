#!/usr/bin/env python3

import sys, os, csv, re, subprocess
from datetime import datetime as dt
from datetime import timedelta

DT_FMT = '%a %b %d %H:%M:%S %Z %Y'
SAVE_DIR = '/var/log/punch-clock'
NOW = dt.now().astimezone()
sunday = NOW - timedelta(NOW.isoweekday())
SAVEFILE_PATH = os.path.join(SAVE_DIR, '%s.tsv' % sunday.strftime('%Y-%m-%d'))
VIM_CMD = "sudo vim %s" % (SAVEFILE_PATH)

def out(txt): sys.stdout.write(txt)
def rst(): out("\033[0m")
def overline(): out("\033[53m")
def colorit(ansi_code_1, txt, ansi_code_2 = None, n = ''):
	pattern = "\033[%sm%"+str(n)+"s\033[%sm"
	return pattern % (ansi_code_1, txt, ansi_code_2 or '0')

def copy_vim_str():
	subprocess.run(["clip.exe"], input=bytes(VIM_CMD, 'utf-8'))
	out(colorit('33', "Copied cmd \'%s\' to your clipboard") % colorit('0', VIM_CMD, '33'))

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
			f.write('%s\t%s\t%s\n' % (code, timestr, msg or ''))

	def calc(self):
		if os.path.exists(SAVEFILE_PATH):
			with open(SAVEFILE_PATH, 'r') as f:
				Calculator(NOW, f).calc()
		else:
			print('No log file found for this week: %s' % (SAVEFILE_PATH), file=sys.stderr)
			sys.exit(1)

class Punch(object):
	def __init__(self, tsvrow, prev_punch):
		self.status, self.timestr, self.message = tsvrow
		self.prev = prev_punch
		self.time = parse_timestr(self.timestr)
		self.interval = None # time since prev punch
		self.day_secs = None # time worked
		self.week_secs = None # time worked

	def _validate(self):
		if self.prev and self.status in ('In', 'Out') and self.status == self.prev.status:
			errmsg = "\"%s\" followed by \"%s\"\033[33m (%s)\033[0m" % (self.status, self.prev.status, colorit('33', self.timestr))
		elif self.status == 'Out' and self.prev is None:
			errmsg = "No prev time for Out"
		else:
			return True
		out(colorit('31', "Error: ") + errmsg)
		copy_vim_str()
		sys.exit(1)

	def calculate(self):
		self._validate()
		if self.prev is None:
			return
		self.interval = self.time - self.prev.time
		self.day_secs = 0 if self._is_new_date() else self.prev.day_secs or 0
		self.week_secs = self.prev.week_secs or 0
		if self.status == 'Out':
			self.day_secs += self.interval.total_seconds()
			self.week_secs += self.interval.total_seconds()

	def _is_new_date(self):
		return self.prev is None or self.prev.time.date() != self.time.date()

	def out(self):
		if self._is_new_date():
			overline()
		do_print_work = self.status == 'Out'
		day_str = colorit('36', clock2str(self.day_secs)) if do_print_work else ''
		week_str = colorit('33', clock2str(self.week_secs)) if do_print_work else ''
		int_color = '32' if self.status == 'Out' else '35'
		int_str = colorit(int_color, clock2str(self.interval) or 'n/a')
		out('%30s\t%8s %8s %8s %s\n' % (self.timestr, day_str, week_str, int_str, self.message or ''))

class Calculator(object):
	def __init__(self, now, savefile):
		self.tsv = csv.reader(savefile, delimiter="\t")
		NOW = now

	def is_today(self, time):
		return time.date() == NOW.date()

	def calc(self):
		today_worked_secs = 0
		worked_secs = 0
		prev_punch = None
		for row in self.tsv:
			punch = Punch(row, prev_punch)
			punch.calculate()
			punch.out()
			prev_punch = punch

		# Print summary
		overline()
		if punch.status == 'In':
			punch = Punch(['Out', NOW.strftime(DT_FMT), ''], prev_punch)
			punch.calculate()
		out('%s\t%s %s\n' % (
			colorit('3;36;1;53', '('+prev_punch.status+')', n=30),
			colorit('36;53', 'today', n=8),
			colorit('35;53', 'week', n=8)))
		out('%s\t%s %s\n' % (
				colorit('90', 'worked', n=30),
				colorit('38;5;70', clock2str(punch.day_secs), n=8),
				colorit('38;5;176', clock2str(punch.week_secs), n=8)))
		remaining_today = clock2str(timedelta(hours=8) - timedelta(seconds=punch.day_secs))
		remaining_this_week = clock2str(timedelta(hours=40) - timedelta(seconds=punch.week_secs))
		out('%s\t%s %s\n' % (
			colorit('90', 'remain', n=30),
			colorit('38;5;64', remaining_today, n=8),
			colorit('38;5;173', remaining_this_week, n=8)))

arg1 = sys.argv[1].lower() if len(sys.argv) > 1 else None
if arg1 is None:
	Runner().calc()
elif re.match(r'^in|^out', arg1):
	Runner().punch_clock(*sys.argv[1:])
elif re.match(r'^path', arg1):
	out('%s\n' % SAVEFILE_PATH)
elif re.match(r'^edit', arg1):
	os.execlp('vim', 'vim', SAVEFILE_PATH)
