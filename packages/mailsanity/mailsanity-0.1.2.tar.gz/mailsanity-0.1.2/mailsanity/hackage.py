#!/usr/bin/env python3
# -*- mode: python -*-
from urllib.request import urlopen
CABAL_LINK_TEMPLATE = 'http://hackage.haskell.org/packages/archive/{pkg}/{version}/{pkg}.cabal'

def applicable(msg):
    return str(msg['X-RSS-URL']).startswith("http://hackage.haskell.org/")

def reformat(msg):
    if applicable(msg):
        (pkg, version)  = msg['X-RSS-URL'].split('/')[-1].rsplit('-', 1)
        cabal_link = CABAL_LINK_TEMPLATE.format(pkg = pkg, version = version)
        cabal_content = str(urlopen(cabal_link).read(), encoding = 'utf-8')
        msg.set_payload(cabal_content)
        return True
    return False
