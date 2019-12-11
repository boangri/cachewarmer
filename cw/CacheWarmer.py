import random
import math
import time
import re
import traceback
import threading
from urllib.error import HTTPError
import sys
from urllib.request import Request, urlopen


class CacheWarmer:
    def __init__(self, sitemap, processes=100, frequency=1.0):
        self.processes = processes
        self.active_threads = []
        self.urls = []
        self.updated_count = 0
        self.fetched_count = 0
        self.sitemap_url = sitemap
        self.code_statistics = {}
        self.average_time = 0.0
        self.tau = 1.0 / frequency
        self.last_start = 0.0
        self.code = None
        self.load_time = None
        self.exit_flag = False
        self.IGNORE_EXIT_FLAG = True

    def start(self):
        """
        Execute the main process
        """
        self.printflush('Sitemap: ' + self.sitemap_url)
        self.getUrlsList()
        self.printflush('Fetched: ' + str(self.fetched_count))
        self.printflush('Processes: ' + str(self.processes))
        self.CheckURLs()
        self.printReport()

    def printflush(self, string, ignore_exit=False):
        """
        Print text and flush stdout
        """
        if not self.exit_flag or ignore_exit == self.IGNORE_EXIT_FLAG:
            print(str(string))
            sys.stdout.flush()

    def printReport(self):
        """
        Print a report after process execution
        """
        self.printflush('Fetched: ' + str(self.fetched_count), self.IGNORE_EXIT_FLAG)
        self.printflush('Processes: ' + str(self.processes), self.IGNORE_EXIT_FLAG)
        self.printflush('Updated: ' + str(self.updated_count), self.IGNORE_EXIT_FLAG)
        self.printflush('Average page load time: ' + format(self.average_time, '.3f'), self.IGNORE_EXIT_FLAG)
        self.printflush('Returned with code: ' + repr(self.code_statistics), self.IGNORE_EXIT_FLAG)

    def getUrlsList(self):
        """
        Fetch an URLs list from website XML sitemap
        """
        try:
            if self.sitemap_url.startswith('http'):
                f = self.urlopen(self.sitemap_url)
                res = f.readlines()
                for d in res:
                    data = re.findall('<loc>(https?:\/\/.+?)<\/loc>', d.decode("utf-8"))
                    for url in data:
                        self.urls.append(url)
            else:  # sitemap is a file
                f = open(self.sitemap_url, 'r')
                res = f.readlines()
                for d in res:
                    data = re.findall('<loc>(https?:\/\/.+?)<\/loc>', d)
                    for url in data:
                        self.urls.append(url)
        except Exception as e:
            self.printflush(str(e))
            self.printflush(traceback.format_exc())
        self.fetched_count = len(self.urls)

    def CheckURLs(self):
        self.updated_count = 0
        self.last_start = time.time()
        self.exit_flag = False
        i = 0
        try:
            for url in self.urls:
                i += 1
                thread = threading.Thread(target=self.fetcher, args=(url, i))
                self.delay()
                thread.start()
                self.active_threads.append(thread)
        except KeyboardInterrupt as e:
            print("Interrupted!")
        for thread in self.active_threads:
            thread.join()
        if self.updated_count > 1:
            self.average_time /= self.updated_count

    def delay(self):
        """
        Delays for random period
        :return:
        """
        x = random.random()  # 0 <= x < 1
        delay = -1 * self.tau * math.log(1 - x)
        self.last_start += delay
        t = self.last_start - time.time()
        if t > 0:
            time.sleep(t)

    def fetcher(self, url, i):
        p_start = time.time()
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=hdr)
        try:
            res = urlopen(req)
            p_end = time.time()
            code = res.getcode()
        except HTTPError as http_error:
            p_end = time.time()
            code = http_error.code
        load_time = p_end - p_start
        print(i, str(format(load_time, '.3f')) + ' ' + str(code) + ' ' + url)
        self.average_time += load_time
        self.updated_count += 1
        if code not in self.code_statistics:
            self.code_statistics[code] = 1
        else:
            self.code_statistics[code] += 1

    def urlopen(self, url):
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=hdr)
        return urlopen(req)
