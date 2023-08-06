import os
from distutils.core import setup

VERSION = "0.2.2"

setup(
    name = "smartparse", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/smartparse",
    download_url = "https://pypi.python.org/packages/source/s/smartparse/smartparse-{version}.tar.gz".format(version=VERSION),
    description = 'Makes the ConfigParser smarter.',
    long_description = open('README.rst').read() if os.path.isfile('README.rst') else str(),
    py_modules = ["smartparse"],
    install_requires = ['timeparser'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    license='GPL',
    keywords='config configfile ConfigParser datetime',
)
