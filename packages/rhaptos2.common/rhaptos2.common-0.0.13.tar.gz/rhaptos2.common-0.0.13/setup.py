
'''
setup.py for rhaptos2

'''

from distutils.core import setup
import os, glob

def get_version():
    '''
    visit a file we assume exists, grab the version number from there.

    returns a string expected in format of 0.0.0
    '''
   
    v = open('rhaptos2/common/version.txt').read().strip()
    return v

def main():

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
          install_requires=["statsd",],

          package_data={'rhaptos2.common': ['version.txt',]}


          )



if __name__ == '__main__':
    main()

