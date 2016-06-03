import sys
import os
from argparse import ArgumentParser
from urllib2 import urlopen
from datetime import datetime, timedelta
import json
import smtplib

class DudeWheresMyBox(object):

	def __init__(self, args):
		self.args = args
		self.minutes_old_alert = 10

	def run(self):
		my_ip = self.get_current_ip()
		self.determine_alerts()
		comparer_ip_issues = self.compare_ips(my_ip)
		if comparer_ip_issues and self.alert:
			self.send_alert(comparer_ip_issues)

	def determine_alerts(self):
		if not self.args.to or len(self.args.to) == 0:
			print 'No one to alert'
			self.alert = False
			return
		self.alert = True

	def get_current_ip(self):
		my_ip = str(urlopen('http://ip.42.pl/raw').read()).strip()
		print 'Current IP: %s' % my_ip	
		return my_ip

	def compare_ips(self, current_ip):
		last_ip_txt = os.path.join(
			os.path.dirname(os.path.realpath(__file__)),
			'last_ips.txt'
		)
		d = json.dumps({
			'last_wan_ip': current_ip,
			'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		})
		file_ = None
		error = None
		msg = None
		compare = {'date':None, 'last_wan_ip':None}		
		if os.path.exists(last_ip_txt):
			file_ = open(last_ip_txt, 'r')
			try:
				compare = json.loads(str(file_.read()).strip())
			except ValueError:
				pass

		else:
			error = 'No History'
			msg = 'Current WAN IP: %s' % current_ip

		if compare['last_wan_ip'] != current_ip:
			error = 'Not Matching IP'
			msg = 'Old WAN IP: %s, new WAN IP: %s' % (compare['last_wan_ip'], current_ip)

		if compare['date']:
			compare_date = datetime.strptime(compare['date'], "%Y-%m-%d %H:%M:%S")
			minutes_old = (datetime.now() - compare_date).seconds / 60
			if  minutes_old >= self.minutes_old_alert:
				error = 'Havent Emailed in %s minutes' % str(minutes_old)
				msg = 'WAN IP is still %s' % current_ip
		if file_:
			file_.close()
		if error:
			print error
			print msg
			ret = {
				'subject': error,
				'msg': msg
			}
			file_ = open(last_ip_txt, 'w')
			file_.write(d)
			file_.close()			
			return ret
		return False

	def send_alert(self, msg):
		carrier_dict = {
			'at&t': 'txt.att.net',
			't-mobile': 'tmomail.net',
			'verizon': 'vtext.com',
			'sprint': 'page.nextel.com',
		}
		self.__setup_smtp()
		for to in self.args.to:
			message = ("From: %s\r\n" % self.SMTP_EMAIL + "To: %s\r\n" % to + "Subject: %s\r\n" % msg['subject'] + "\r\n" + msg['msg'])
			if self.args.debug:
				print 'DEBUG -- not sending'
				print message
			self.smtp_server.sendmail(self.SMTP_EMAIL, to, message)

	def __setup_smtp(self):
		self.SMTP_HOST = os.environ.get('SMTP_HOST')
		self.SMTP_EMAIL = os.environ.get('SMTP_ACCOUNT')
		self.SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
		self.smtp_server = smtplib.SMTP( self.SMTP_HOST, 587 )
		self.smtp_server.starttls()
		self.smtp_server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)

def parse_args( args ):
	parser = ArgumentParser(description='')
	parser.add_argument(
		'-t', '--to', 
		default=False, 
		help='Email address/numbers to alert'
	)
	parser.add_argument(
		'--debug',
		action='store_true',
		default=False,
		help='Enable the Debugger!'
	)
	args = parser.parse_args()
	if args.to and ',' in args.to:
		args.to = args.to.split(',')
	elif isinstance(args.to, basestring):
		args.to = [args.to]
	return args

if __name__ == "__main__":
	args = parse_args( sys.argv )
	DudeWheresMyBox(args).run()

# End File: dude_wheres_my_box.py
