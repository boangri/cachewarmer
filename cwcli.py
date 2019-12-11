import os
from cw.CacheWarmer import CacheWarmer
import sys
import getopt

#__path__=[os.path.dirname(os.path.abspath(__file__))]
def main(argv):
    sitemap_url = ''
    threads_count = 100
    frequency = 1
    try:
        opts, args = getopt.getopt(argv, "hs:c:n:", ["sitemap=", "threads=", "number"])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()
        if opt in ("-s", "--sitemap"):
            sitemap_url = arg.strip("'\"")
        elif opt in ("-c", "--threads"):
            threads_count = int(arg)
        elif opt in ("-n", "--number"):
            frequency = float(arg)
    if sitemap_url != '':
        cw = CacheWarmer(sitemap_url, threads_count, frequency)
        cw.start()


def printHelp():
    file = os.path.basename(__file__)
    print(file + ' -s|--sitemap <url> [-c|--threads <threads count>] [-n|--number <frequency, Hz>]')


if __name__ == "__main__":
    main(sys.argv[1:])
