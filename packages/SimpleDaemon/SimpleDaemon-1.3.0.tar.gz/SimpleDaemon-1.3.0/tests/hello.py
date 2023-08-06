import time
import logging

from simpledaemon import Daemon


class HelloDaemon(Daemon):
    default_conf = 'hello.conf'
    section = 'hello'

    def run(self):
        while True:
            logging.info('The daemon says hello')
            time.sleep(3)


if __name__ == '__main__':
    HelloDaemon().main()
