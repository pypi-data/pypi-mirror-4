#!/usr/bin/env python3
# -*- mode: python -*-
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
import tarfile

_tgz_link_template = 'https://pypi.python.org/packages/source/d/{pkg}/{pkg}-{version}.tar.gz'
_readme_path_template = '{pkg}-{version}/{readme}'

def applicable(msg):
    return str(msg['X-RSS-URL']).startswith('http://pypi.python.org')

def get_tarobj(pkg, version):
    tgz_link = _tgz_link_template.format(version = version, pkg = pkg)
    tmpfile = NamedTemporaryFile()
    tmpfile.write(urlopen(tgz_link).read())
    return tarfile.open(tmpfile.name, mode = 'r:gz')

def reformat(msg):
    if applicable(msg):
        url = msg['X-RSS-URL']
        (version, pkg, *_) = reversed(url.split('/'))
        tarobj = get_tarobj(pkg, version)
        for readme in ["README.txt", "README.rst", "PKG-INFO"]:
            try:
                help_text = str(tarobj.extractfile(
                        _readme_path_template.format(version = version, pkg = pkg, readme = readme)).read(),
                                encoding = 'utf-8')
                msg.set_payload(help_text)
                return True
            except KeyError:
                pass
    return False
