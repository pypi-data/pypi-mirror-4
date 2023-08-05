
'''
setup.py for rhaptos2

'''
#from distutils.core import setup
#from distribute_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages
import os, glob


def get_version():
    try:
        v = open("version.txt").read().strip()
    except:
        v = "UNABLE_TO_FIND_RELEASE_VERSION_FILE"
    return v




setup(name='rhaptos2.common',
          version=get_version(),
          packages=['rhaptos2.common',
                   ],
          namespace_packages = ['rhaptos2'],
          author='See AUTHORS.txt',
          author_email='info@cnx.org',
          url='https://github.com/Connexions/rhaptos2.common',
          license='LICENSE.txt',
          description='Common libraries for Rhaptos2',
          long_description='see description',
          install_requires=["statsd",
                           ]

          )



