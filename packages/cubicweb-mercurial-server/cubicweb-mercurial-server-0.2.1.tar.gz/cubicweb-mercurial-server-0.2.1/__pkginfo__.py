# -*- coding: utf-8 -*-
# pylint: disable-msg=W0622
"""cubicweb-mercurial-server application packaging information"""

modname = 'mercurial_server'
distname = 'cubicweb-mercurial-server'

numversion = (0, 2, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'Florent Cayré (FRANCE)'
author_email = 'florent.cayre@gmail.com'
description = 'mercurial server integration cube'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ =  {'cubicweb': '>= 3.15',
                'cubicweb-vcsfile': '>= 1.12.2'}
__recommends__ = {}


from os import listdir as _listdir
from os.path import join, isdir, exists
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'wdoc', 'i18n', 'migration'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package
