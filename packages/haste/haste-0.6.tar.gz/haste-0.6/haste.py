#!/usr/bin/env python

"""haste - a client to hastebin.com.

Usage:
    haste [-r] [-]
    haste [-r] FILE

-             read from stdin.
FILE          read from a file.

-h --help     show this message.
-v --version  show version information.
-r --raw      return a URL to the raw paste data.
"""

import json
import sys

from docopt import docopt
import requests

BASEURL = "http://hastebin.com"

kwargs = docopt(__doc__, version='haste 0.5')


def run(**kwargs):
    # get data
    if kwargs['FILE'] and kwargs['FILE'] != '-':
        with open(sys.argv[1], 'r') as filedata:
            data = "".join(filedata.readlines()).strip()
    else:
        data = "".join(sys.stdin.readlines()).strip()

    # POST data and show response
    response = requests.post(BASEURL + "/documents", data)
    if kwargs['--raw']:
        url = "%s/raw/%s\n" % (BASEURL, json.loads(response.text)['key'])
    else:
        url = "%s/%s\n" % (BASEURL, json.loads(response.text)['key'])
    sys.stdout.write(url)


def main():
    run(**kwargs)


if __name__ == "__main__":
    run(**kwargs)
