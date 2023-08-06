import os
import sys
import tempfile
from time import sleep
from subprocess import call

def run_daemon(daemon, pidfile, logfile, search_text):
    try:
        assert not os.path.exists(logfile), "Can't trust an old logfile at '%s'" % logfile
        assert os.path.exists(daemon), "Could not find daemon: '%s'" % daemon
        retcode = invoke(daemon, '--help')
        assert retcode == 0, "'%s' does not appear to be a daemon (couldn't call --help on it)." % daemon
        retcode = invoke(daemon, '--start')
        sleep(1)  # give the daemon a second to start up.
        assert retcode == 0, "Could not start '%s'" % daemon
        assert os.path.exists(pidfile), "pidfile '%s' not found" % pidfile
        assert os.path.exists(logfile), "logfile '%s' not found" % logfile
        retcode = invoke(daemon, '--stop')
        assert retcode == 0, "'%s' did not stop." % daemon
        assert search_text in open(logfile).read(), "'%s' not found in logfile '%s'" % (search_text, logfile)
        assert not os.path.exists(pidfile), "pidfile '%s' stuck around" % pidfile
    finally:
        if os.path.exists(logfile):
            os.unlink(logfile)
            # pass
        if os.path.exists(pidfile):
            os.unlink(pidfile)
        try:
            invoke(daemon, '--stop')
        except:
            pass

def invoke(daemon, *args):
    with tempfile.TemporaryFile() as fp:
        return call(['python', daemon] + list(args), stdout=fp, stderr=fp)

def test_daemon():
    run_daemon('hello.py', 'hello.pid', 'hello.log', "says hello")    

if __name__ == '__main__':
    test_daemon()
