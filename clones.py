#!/usr/bin/env python
"""Get number of clones for a GitHub repository via its API,
caching JSON locally since old data isn't stored.

Usage:
    github-clones.py [--help | options] <repo>

Arguments:
  <repo>  : `user/repository` or `org/repository`

Options:
  -l TOKEN, --login TOKEN     : `user:TOKEN`|`TOKEN` for private API login.
      Will look for $GITHUB_API_TOKEN if not specified
  -u URL, --url URL           : default:
      https://api.github.com/repos/{REPO}/traffic/clones?per=day
  -o OUT, --output OUT        : output file
      re.sub(r'\W', '_', <repo>).FMT will be (re)written to disk
  -k K, --key K  : [default: count]|uniques for total clones/unique cloners
  -p P, --decrement-prefix P  : [default: -]
  --decrement    : subtract one from "P{DATE_TODAY}" (note the prefix 'P')
  --log LVL      : logging level [default: INFO]
"""
from __future__ import print_function
from argopt import argopt
import re
from os import getenv
import json
from time import strftime
import logging
try:
    from urllib.request import Request, urlopen, quote
except ImportError:
    from urllib2 import Request, urlopen, quote
from base64 import b64encode
__author__ = "Casper da Costa-Luis <imaging@caspersci.uk.to>"


RE_NW = re.compile(r"\W+")
JSON_OPTS = dict(indent=0, separators=",:", sort_keys=True)


def urlread_auth(url, login=None, decode=True):
    request = Request(url)
    if login:
        request.add_header('Authorization',
                           b'Basic ' + b64encode(login.encode()))
    res = urlopen(request).read()
    return res.decode() if decode else res


def logo64(url):
    return quote(b64encode(urlread_auth(url, decode=False)))


def csd(x):
  """Comma separate digit"""
  # return ''.join(reversed([x + (',' if i and not i % 3 else '')
  #                for (i, x) in enumerate(reversed(str(hits)))]))
  from re import sub
  return sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1,", str(x))


def cleanTime(time):
    """2018-02-22T00:00:00Z -> 20180222"""
    return time[:len("2018-02-22")].replace('-', '')


def countMap(data, key=None, subkey="count"):
    """convert github API dictionary to desired dictionary"""
    res = dict((cleanTime(d["timestamp"]), d[subkey])
               for d in data["clones"])
    return {key: res} if key else res


def run(args):
    log = logging.getLogger(__name__)
    eg_link = args.url or \
        "https://api.github.com/repos/{REPO}/traffic/clones?per=day"

    login = args.login or getenv("GITHUB_API_TOKEN")
    log.debug("url:" + eg_link)

    eg_link = eg_link.format(REPO=args.repo)
    repo_w = RE_NW.sub('_', args.repo)
    eg_out = args.output or repo_w + ".json"
    log.info("output:" + eg_out)

    # load disk data
    try:
        with open(eg_out) as fd:
            data = json.load(fd)
    except IOError:
        data = {}

    # update with new data
    newData = countMap(json.loads(urlread_auth(eg_link, login)),
                       subkey=args.key)
    log.debug(newData)
    data.setdefault(repo_w, {})
    data[repo_w].setdefault(args.key, {})
    d = data[repo_w][args.key]  # convenience pointer
    d.update(newData)

    # assume one extra clone to decrease for today
    d[strftime("run%Y%m%d")] = -1

    if args.decrement:
        now = strftime(args.decrement_prefix + "%Y%m%d")
        d.setdefault(now, 0)
        d[now] -= 1

    # overwrite disk
    with open(eg_out, "w") as fd:
        json.dump(data, fd, **JSON_OPTS)

    log.debug(d)
    if args.decrement:
        log.info("decrements:%s:%d" % (
            args.decrement_prefix,
            sum(v for (k, v) in d.items()
                if k.startswith(args.decrement_prefix))))
    else:
        log.info("decrements:ALL:%d" % sum(v for v in d.values() if v < 0))
    log.info("total:%d" % sum(d.values()))


def main():
    args = argopt(__doc__).parse_args()
    logging.basicConfig(level=getattr(logging, args.log, logging.INFO))
    log = logging.getLogger(__name__)
    log.debug(args)
    return run(args) or 0


if __name__ == "__main__":
    main()
