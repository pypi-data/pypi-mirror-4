#!/usr/bin/env python3
# -*- mode: python -*-
from urllib.request import urlopen
def applicable(msg):
    return str(msg['X-RSS-URL']).startswith("https://aur.archlinux.org/packages/")

def reformat(msg):
    if applicable(msg):
        page_link = msg['X-RSS-URL']
        pkg = page_link.split('/')[-2]
        pkgbuild_link = "https://aur.archlinux.org/packages/{0}/{1}/PKGBUILD".format(pkg[:2], pkg)
        pkgbuild = str(urlopen(pkgbuild_link).read(), encoding = 'utf-8')
        msg.set_payload(pkgbuild)
        return True
    return False
