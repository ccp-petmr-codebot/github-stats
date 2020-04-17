#!/usr/bin/env python
from __future__ import print_function
import json
from clones import urlread_auth, logo64, quote, csd, RE_NW, JSON_OPTS
import sys
__author__ = "Casper da Costa-Luis <imaging@caspersci.uk.to>"

REPO_SLUG = "SyneRBI/SIRF-SuperBuild"
DOCKER_SLUG = "synerbi/sirf"

REPO_W = RE_NW.sub('_', REPO_SLUG)
DB = REPO_W + ".json"
BADGE_LOGO = "https://avatars2.githubusercontent.com/u/16674841?s=32&amp;v=4"
BADGE_URL = "https://img.shields.io/badge/"
JSON_BADGE_URL = "https://img.shields.io/badge/dynamic/json.svg"
JSON_URI = "https://raw.githubusercontent.com/SynerBI/github-stats/" + \
    REPO_SLUG + '/' + DB
DOCKER_STATS_URL = "https://hub.docker.com/v2/repositories/" + DOCKER_SLUG
VM_STATS_URL = None  # TODO


def main():
    # load disk data
    with open(DB) as fd:
        data = json.load(fd)

    # daily: `all clones` - `travis clones` - `travis docker pulls`
    # d = data[REPO_W]["count"]

    # daily: `all cloners` - 0 or 1 (travis user) - `travis docker pulls`
    d = data[REPO_W]["uniques"]

    clones = sum(d.values())
    # clones -= 1540  # hardcode offset
    print("under estimate:", clones)

    # all docker pulls
    docker_pulls = json.loads(urlread_auth(DOCKER_STATS_URL))["pull_count"]
    print("gross docker pulls:", docker_pulls)
    d["docker"] = docker_pulls

    # drupal counts from www.ccpsynerbi.ac.uk
    vm_downloads = 0
    # TODO: vm_downloads = json.loads(urlread_auth(VM_STATS_URL))["download_count"]
    print("VM downloads:", vm_downloads)
    d["vm"] = vm_downloads

    # best estimate of all installs
    installs = clones + docker_pulls + vm_downloads
    print("total:", installs)

    # overwrite disk totals
    data["total"] = installs
    with open(DB, "w") as fd:
        json.dump(data, fd, **JSON_OPTS)

    if len(sys.argv) > 1:
        # static badge
        logo = "logo=data:image/png;base64," + logo64(BADGE_LOGO)
        print("%sinstalls-%s-8000f0.svg?%s" % (
            BADGE_URL, csd(installs), logo))

        # dynamic badge
        print("%s?label=installs&uri=%s&query=%s&colorB=8000f0&%s" % (
              JSON_BADGE_URL, quote(JSON_URI),
              "total",  # REPO_W + ".uniques.*"
              logo))


if __name__ == "__main__":
    main()
