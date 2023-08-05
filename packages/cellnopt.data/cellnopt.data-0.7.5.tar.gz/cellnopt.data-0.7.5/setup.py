# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 2614 2012-10-23 09:18:51Z cokelaer $"

import sys
import os
from setuptools import setup, find_packages
import glob


_MAJOR               = 0
_MINOR               = 7
_MICRO               = 5
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)

metainfo = {
    'authors': {'Cokelaer':('Thomas Cokelaer','cokelaer@ebi.ac.uk')},
    'version': version,
    'license' : 'GPL',
    'download_url' : ['http://pypi.python.org/pypi/cellnopt.data'],
    'url' : ['http://www.ebi.ac.uk/~cokelaer/cellnopt/data'],
    'description':'data and model repository' ,
    'platforms' : ['Linux', 'Unix', 'MacOsX', 'Windows'],
    'keywords' : ['Graph Theory', 'Genetic Algorithm', 'Cell Theory',
        'Signalling Pathways', 'CellNOpt', 'rpy2', 'cno'],
    'classifiers' : [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics']
    }


# todo : simplify this 
namespace = 'cellnopt'
pkg_root_dir = 'src'
pkgs = [ pkg for pkg in find_packages(pkg_root_dir)]
top_pkgs = [pkg for pkg in pkgs if  len(pkg.split('.')) < 2]
packages = pkgs
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir + "/" + pkg) for pkg in top_pkgs] )

# files in share/data
datadir = os.path.join('share','data')
datafiles = [(datadir, [f for f in glob.glob(os.path.join(datadir, '*'))])]


models = [x for x in glob.glob(os.path.join("share",'data', "*")) if os.path.isdir(x)]
datafiles = [(datadir, [f for f in glob.glob(os.path.join(datadir, '*')) if os.path.isfile(f)]) for datadir in models]





setup(
    name             = 'cellnopt.data',
    version          = version,
    maintainer       = metainfo['authors']['Cokelaer'][0],
    maintainer_email = metainfo['authors']['Cokelaer'][1],
    author           = metainfo['authors']['Cokelaer'][0],
    author_email     = metainfo['authors']['Cokelaer'][1],
    long_description = open("README.txt").read(),
    keywords         = metainfo['keywords'],
    description = metainfo['description'],
    license          = metainfo['license'],
    platforms        = metainfo['platforms'],
    url              = metainfo['url'],      
    download_url     = metainfo['download_url'],
    classifiers      = metainfo['classifiers'],

    # package installation
    packages = find_packages('src'),
    package_dir  = package_dir,
    namespace_packages = [namespace],
    #create_namespaces = True,
    install_requires = ['easydev>=0.5.2'],
    data_files = datafiles,
    )


