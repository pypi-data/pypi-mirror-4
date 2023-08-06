from distutils.core import setup

import simpledaemon

setup(
    name='SimpleDaemon',
    version='.'.join(map(str, simpledaemon.VERSION)),
    author="Shane Hathaway",
    author_email="shane@hathawaymix.org",
    maintainer="Don Spaulding",
    maintainer_email="donspauldingii@gmail.com",
    packages=['simpledaemon'],
    license=open('LICENSE.txt').read(),
    description="Provides a simple Daemon class to ease the process of forking a python application on Unix systems.",
    long_description=open('README.rst').read(),
    url='http://bitbucket.org/donspaulding/simpledaemon/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
)
