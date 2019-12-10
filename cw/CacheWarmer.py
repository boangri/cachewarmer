import random
import math
import time
import re
import traceback
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from .scw.fetcher import Fetcher
from .scw.app import App


class CacheWarmer():
    def __init__(self, sitemap, processes=100, frequency=1.0):
        self.processes = processes
        self.active_threads = []
        self.app = App()
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

    def start(self):
        """
        Execute the main process
        """
        self.app.printflush('Sitemap: ' + self.sitemap_url)
        self.getUrlsList()
        self.app.printflush('Fetched: ' + str(self.fetched_count))
        self.app.printflush('Processes: ' + str(self.processes))
        self.CheckURLs()
        self.printReport()

    def printReport(self):
        """
        Print a report after process execution
        """
        self.app.printflush('Fetched: ' + str(self.fetched_count), self.app.IGNORE_EXIT_FLAG)
        self.app.printflush('Processes: ' + str(self.processes), self.app.IGNORE_EXIT_FLAG)
        self.app.printflush('Updated: ' + str(self.updated_count), self.app.IGNORE_EXIT_FLAG)
        self.app.printflush('Average page load time: ' + format(self.average_time, '.3f'), self.app.IGNORE_EXIT_FLAG)
        self.app.printflush('Returned with code: ' + repr(self.code_statistics), self.app.IGNORE_EXIT_FLAG)

    def getUrlsList(self):
        """
        Fetch an URLs list from website XML sitemap
        """
        try:
            f = self.app.urlopen(self.sitemap_url)
            res = f.readlines()
            for d in res:
                data = re.findall('<loc>(https?:\/\/.+?)<\/loc>', d.decode("utf-8"))
                for i in data:
                    self.urls.append(i)
        except Exception as e:
            self.app.printflush(str(e))
            self.app.printflush(traceback.format_exc())
        self.fetched_count = len(self.urls)


    def CheckURLs(self):
        self.updated_count = 0
        self.last_start = time.time()
        self.app.setExitFlag(False)
        i = 0
        try:
            for url in self.urls:
                i += 1
                # thread = Fetcher(url, i)
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
