# pylint: disable=W0622
"""cubicweb-apycot application packaging information"""

modname = 'apycot'
distname = 'apycot'

numversion = (2, 2, 4)
version = '.'.join(str(num) for num in numversion)

license = 'GPL'
description = 'Continuous testing / integration tool for the CubicWeb framework'
author = 'Logilab'
author_email = 'contact@logilab.fr'
web = 'http://www.logilab.org/project/apycot'
classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends__ = {'pyro': None,
               'cubicweb': '>= 3.14.0',
               'cubicweb-vcsfile': '>= 1.6.1',
               'cubicweb-file': None,
               'cubicweb-narval': '>= 3.0.2',
               }
__recommends__ = {'cubicweb-tracker': None,
                  'cubicweb-nosylist': '>= 0.5.0',
                  'cubicweb-jqplot': '>= 0.1.2',
                  }

# packaging ###

from os import listdir as _listdir
from os.path import join, isdir
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
for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration', 'wdoc'):
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

if isdir('narval'):
    data_files.append([join('var', 'lib', 'narval', 'plugins'), listdir('narval')])
if isdir('ext'):
    data_files.append([join('share', 'apycot', 'ext'), listdir('ext')])
