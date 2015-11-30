#!/usr/bin/env python
from datetime import datetime
from sys import argv

from bcrypt import gensalt, hashpw

from tasks import key, read_cmd

def main(cmd):
    timestamp = str(datetime.now())
    sig = _generate_sig(cmd, timestamp)
    print 'timestamp:', timestamp
    print 'cmd:', cmd
    print 'sig:', sig
    read_cmd.delay(cmd, timestamp, sig)


def _generate_sig(cmd, timestamp):
    return hashpw(cmd + timestamp + key, gensalt())


if __name__ == '__main__':
    main(' '.join(argv[1:]))
