from croniter.croniter import croniter
from utils import now

class crontab:
	""" Like a :manpage:`cron` job, you can specify units of time of when you would like the task to execute. """

	def __init__(self, minute='*', hour='*', day_of_week='*',
	             day_of_month='*', month_of_year='*', timezone=None):
		self.minute = minute
		self.hour = hour
		self.day_of_week = day_of_week
		self.day_of_month = day_of_month
		self.month_of_year = month_of_year
		self.timezone = timezone
		self.__cron_iter = None

	def __str__(self):
		return "%s %s %s %s %s" % (self.minute, self.hour, self.day_of_month, self.month_of_year, self.day_of_week)

	@property
	def cron(self):
		if not self.__cron_iter:
			self.__cron_iter = croniter(str(self), now(self.timezone))
		return self.__cron_iter

	@property
	def next(self):
		value = self.cron.get_next()
		self.cron.get_prev()
		return value

	def move_next(self):
		self.__cron_iter = None