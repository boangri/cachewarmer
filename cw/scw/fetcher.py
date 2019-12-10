import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class Fetcher(threading.Thread):
	def __init__(self, url, i):
		super(Fetcher, self).__init__()
		self.url = url
		self.num = i
		self.load_time = 0.0
		self.code = None

	def run(self):
		p_start = time.time()
		hdr = {'User-Agent': 'Mozilla/5.0'}
		req = Request(self.url, headers=hdr)
		try:
			res = urlopen(req)
			p_end = time.time()
			self.code = res.getcode()
		except HTTPError as http_error:
			p_end = time.time()
			self.code = http_error.code
		self.load_time = p_end - p_start
		print(self.num, str(format(self.load_time, '.3f')) + ' ' + str(self.code) + ' ' + self.url)
