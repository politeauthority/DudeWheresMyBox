import os
from urllib2 import urlopen
from datetime import datetime, timedelta
import json
import smtplib

class WhatsMyIpAgain(object):

	def run(self):
		my_ip = self.get_current_ip()
		comparer_ip_issues = self.compare_ips(my_ip)
		if comparer_ip_issues:
			self.send_alert(['3154302940@txt.att.net'], comparer_ip_issues)

	def get_current_ip(self):
		my_ip = str(urlopen('http://ip.42.pl/raw').read()).strip()
		print 'Current IP: %s' % my_ip	
		return my_ip

	def compare_ips(self, current_ip):
		last_ip_txt = os.path.join(
			os.path.dirname(os.path.realpath(__file__)),
			'last_ip.txt'
		)
		d = json.dumps({
			'last_ip': current_ip,
			'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		})
		file_ = None
		if os.path.exists(last_ip_txt):
			file_ = open(last_ip_txt, 'r')
			compare = json.loads(str(file_.read()).strip())
		else:
			compare = {'date':None, 'last_ip':None}

		error = None
		if compare['last_ip'] != current_ip:
			error = 'Not Matching IP'

		if compare['date']:
			compare_date = datetime.strptime(compare['date'], "%Y-%m-%d %H:%M:%S")
			print 'theres a date to check'
			minutes_old = (datetime.now() - compare_date).seconds / 60
			print minutes_old
			if minutes_old >= 1:
				error = 'Havent Emailed in %s minutes' % str(minutes_old)
		if file_:
			file_.close()
		file_ = open(last_ip_txt, 'w')
		file_.write(d)
		file_.close()
		if error:
			return error
		return False

	def send_alert(self, numbers, msg):
		carrier_dict = {
			'at&t': 'txt.att.net',
			't-mobile': 'tmomail.net',
			'verizon': 'vtext.com',
			'sprint': 'page.nextel.com',
		}
		self.__setup_smtp()
		for to in numbers:
			subject ='youre cool'
			message = ("From: %s\r\n" % self.SMTP_EMAIL + "To: %s\r\n" % to + "Subject: %s\r\n" % subject + "\r\n" + msg)
			print self.smtp_server.sendmail(from_, to, message)

	def __setup_smtp(self):
		self.SMTP_HOST = os.environ.get('SMTP_HOST')
		self.SMTP_EMAIL = os.environ.get('SMTP_ACCOUNT')
		self.SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
		self.smtp_server = smtplib.SMTP( self.SMTP_HOST, 587 )
		self.smtp_server.starttls()
		self.smtp_server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)

if __name__ == "__main__":
	WhatsMyIpAgain().run()

# End File: whats_my_ip_again.py
