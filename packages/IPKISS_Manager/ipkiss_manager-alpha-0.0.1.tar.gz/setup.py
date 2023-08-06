#!/usr/bin/env python

import os
from setuptools import setup
from ipkiss_manager import utils


if os.name == 'posix':
    utils.install_dependencies([["mercurial", "purehg"],
                                ["shapely", "shapely"],
                                ["descartes","descartes"],],
                                posix_safe=True)


setup(name='IPKISS_manager',
      version='0.0.1',
      description='IPKISS framework manager',
      author='Antonio Ribeiro',
      author_email='antonio.ribeiro@intec.ugent.be',
      url='www.ipkiss.org',
      packages=['ipkiss_manager', 'ipkiss_manager.pyhg', 'ipkiss_manager.app'],
      package_dir={'ipkiss_manager': 'ipkiss_manager'},
      package_data= {'ipkiss_manager': ['fixtures/*.json'], },
      entry_points = {
        'console_scripts': [
            'ipkiss_manager = ipkiss_manager.app.cl:main',
        ],
      },
     )
