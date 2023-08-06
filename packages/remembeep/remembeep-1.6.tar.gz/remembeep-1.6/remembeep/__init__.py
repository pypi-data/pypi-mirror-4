#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
remembeep
=========
Simple script for plaing mp3 file periodically

Install
-------
    $ sudo aptitude install mpg123
    $ sudo pip install remembeep

Usage
-----
Play sound every 15 minutes:

    $ remembeep 15

Stop plaing:

    $ remembeep stop

All options:

    $ remembeep -h


'''
__version__ = '1.6'

import os
import time
import doctest
from datetime import datetime, timedelta

try:
    import argparse
    from simple_daemon import Daemon
except ImportError:
    pass


rel2abs = lambda path: os.path.join(os.path.dirname(
        os.path.abspath(__file__)), *path.split('/'))
PID_FNAME = '/tmp/remembeep.pid'
MP3_FNAME = rel2abs('default.mp3')


def main():
    parser = argparse.ArgumentParser(description='Signal every x minutes')
    parser.add_argument('command', nargs='?', default='20',
            help='signal period in minutes, "stop" or "test"')
    parser.add_argument('-f', '--signal-filename', action='store',
            default=MP3_FNAME, help='mp3 audio file name')
    parser.add_argument('-r', '--replay', action='store', type=int,
            default=3, help='replay count')
    parser.add_argument('--no-daemon', action='store_true',
        help='disable daemonisation')
    run_command(**vars(parser.parse_args()))


def run_command(command, signal_filename, no_daemon, replay):
    daemon = Daemon(PID_FNAME)
    if command == 'stop':
        daemon.stop()
    elif command == 'test':
        run_tests()
    elif command.isdigit():
        every = int(command)
        print_intro(every)
        run = lambda: main_cycle(every, signal_filename, replay)
        if no_daemon:
            run()
        else:
            daemon.run = run
            daemon.start()
    else:
        print 'unknown command'


def run_tests():
    return doctest.testmod(verbose=True)

def print_intro(every):
    next_time = calculate_start_time(every)
    print 'rememBeep will beep every %s minutes from %s' % (every, next_time)


def main_cycle(every, fname, replay):
    next_time = calculate_start_time(every)
    while True:
        now = datetime.now()
        if now < next_time:
            time.sleep(0.5)
            continue
        print 'beep at %s %s' % (now, fname)
        for i in range(replay):
            play_mp3(fname)
        next_time = calculate_next_time(next_time, every)
        print 'next beep will be at ', next_time


def calculate_start_time(every_minutes, now=None):
    '''
        >>> calculate_start_time(10, datetime(2013, 02, 13, 02, 48, 10, 2303))
        datetime.datetime(2013, 2, 13, 2, 50)

        >>> calculate_start_time(15, datetime(2013, 02, 13, 23, 48, 10, 2303))
        datetime.datetime(2013, 2, 14, 0, 0)

        >>> calculate_start_time(150, datetime(2013, 02, 13, 23, 48, 10, 2303))
        datetime.datetime(2013, 2, 14, 0, 0)
    '''
    now = now or datetime.now()
    now = now.replace(microsecond=0, second=0)
    next_minute = (now.minute / every_minutes + 1) * every_minutes
    if next_minute >= 60:
        next_time = now.replace(minute=0, second=0) + timedelta(hours=1)
    else:
        next_time = now.replace(minute=next_minute, second=0)
    return next_time


def calculate_next_time(last_time, every_minutes, now=None):
    '''
        >>> last_time = datetime(2013, 2, 13, 2, 50)

        >>> calculate_next_time(last_time, 10, last_time +
        ...     timedelta(seconds=10, microseconds=100))
        datetime.datetime(2013, 2, 13, 3, 0)

        >>> calculate_next_time(last_time, 100, last_time +
        ...     timedelta(seconds=110*60, microseconds=100))
        datetime.datetime(2013, 2, 13, 6, 10)
    '''
    now = now or datetime.now()
    next_time = last_time
    period = timedelta(seconds=every_minutes * 60)
    while True:
        next_time = next_time + period
        if next_time > now:
            break
    return next_time


def play_mp3(fname):
    os.system('mpg123 %s' % fname)


if __name__ == '__main__':
    main()
