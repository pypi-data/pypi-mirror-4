
'''
setup.py for rhaptos2

'''
#from distutils.core import setup
#from distribute_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages
import os, glob
from bamboo.setuptools_version import versionlib




setup(name='rhaptos2.common',
          version=versionlib.get_version('.'),
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
                            "bamboo.setuptools_version"],
          include_package_data = True,
          package_data={'': ['*.txt', 'version.py']
                        }

          )



