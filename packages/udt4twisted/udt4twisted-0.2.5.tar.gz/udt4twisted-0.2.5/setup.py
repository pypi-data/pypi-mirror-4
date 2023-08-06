#
#   @author         Martin N. Gergov    <martingergov1@gmail.com>
#   @license        GPLv3
#   @date           11/02/2013 (dd-mm-yyyy)
#
#Thanks for:
#http://reinout.vanrees.org/weblog/2009/12/17/managing-dependencies.html

#from distutils.core import setup
from setuptools import setup, find_packages
import os

VERSION = {
        'major' : 0,
        'minor' : 2,
        'patch' : 5,
        }
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name            = 'udt4twisted',
        version         = '%(major)i.%(minor)i.%(patch)s' % VERSION,
        description     = 'An UDT4 integration package for twisted.',
        author          = 'Martin N. Gergov',
        author_email    = 'martingergov1@gmail.com',
        packages        = ['udt4twisted', 'twisted.plugins',],
        package_data={
            'twisted': ['plugins/udtplugin.py'],
        },
        license         = 'GPLv3',
        download_url    = 'https://bitbucket.org/marto1/udt4twisted/',
        keywords        = ['udt4twisted', 'pyudt', 'udt4', 'twisted'],
        long_description=read('README.rst'),
        classifiers     = [
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Topic :: Software Development :: Libraries',
            'Programming Language :: Python :: 2.7'
            ],
        install_requires=[
        "pyudt4",
        "twisted",
        ],
    )
