============
SimpleDaemon
============

A fork of `Shane Hathaway's daemon.py <http://hathawaymix.org/Software/Sketches/daemon.py>`_ script.


Features
========

* reads the command line
* reads a configuration file
* configures logging
* calls root-level setup code
* drops privileges
* calls user-level setup code
* detaches from the controlling terminal
* checks and writes a pidfile


Installation
============
::
    pip install simpledaemon


Example
=======
Writing a daemon requires creating two files, a daemon
file which simply enters an infinite loop and does whatever
you want it to do, and a configuration file with the same name
which tells `simpledaemon` how to setup your daemon.

hellodaemon.py::

    import simpledaemon
    import logging
    import time

    class HelloDaemon(simpledaemon.Daemon):
        default_conf = '/etc/hellodaemon.conf'
        section = 'hello'

        def run(self):
            while True:
                logging.info('The daemon says hello')
                time.sleep(1)

    if __name__ == '__main__':
        HelloDaemon().main()

hellodaemon.conf::

    [hello]
    pidfile = ./hellodaemon.pid
    logfile = ./hellodaemon.log
    loglevel = info


Usage
=====
To use your new daemon, execute your script like so::

    ./hello.py --start

Stopping is similar::

    ./hello.py --stop

For a full list of options, see the help::

    ./hello.py --help


Bugs
====
If you come across any bugs in simpledaemon.  Kindly file an issue at: https://bitbucket.org/donspaulding/simpledaemon/issues/new

Pull requests are also welcome.