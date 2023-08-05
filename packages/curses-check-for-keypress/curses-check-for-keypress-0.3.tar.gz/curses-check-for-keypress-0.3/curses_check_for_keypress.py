#!/usr/bin/python
#
# curses_check_for_keypress - loop until user presses a key.
#
# Copyright (C) 2009-2012 W. Trevor King <wking@tremily.us>
#
# This file is part of curses-check-for-keypress.
#
# curses-check-for-keypress is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# curses-check-for-keypress is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# curses-check-for-keypress.  If not, see <http://www.gnu.org/licenses/>.

"""Enables looping until the user presses a key.

Uses the curses module to monitor for a single keypress, because other
methods of aquiring keyboard input generally require the user to press
enter.

Usual usage looks like the following, but leaving out the `test_mode`
option, which is used to get curses working with doctest's
stdin/stdout manipulations.

>>> c = CheckForKeypress('testing usual usage, press any key to stop loop...',
...     test_mode=True)
testing usual usage, press any key to stop loop...

Use `quiet_sleep` or your own sleep function instead of `_test_sleep`
if you need to reduce the loop rate.

>>> try:
...     while c.input() == None:
...         c.output('sleeping\\n')
...         _test_sleep()
... finally:
...     c.cleanup()  # doctest: +ELLIPSIS
sleeping
...
sleeping

An example with error catching is

>>> c = CheckForKeypress('testing error catching, wait for the error...',
...     test_mode=True)
testing error catching, wait for the error...
>>> i = 0
>>> class TestException (Exception):
...     pass
>>> try:
...     while c.input() == None:
...         if i > 4:
...             size = _sys.stderr.write('testing error output\\n')
...             raise TestException('testing error exception')
...         c.output('sleeping {}\\n'.format(i))
...         _test_sleep()
...         i += 1
...     raise Exception('_test_error_catching() failed!')
... except TestException as e:
...     print('caught exception: {}'.format(e))
... finally:
...     c.cleanup()
sleeping 0
sleeping 1
sleeping 2
sleeping 3
sleeping 4
caught exception: testing error exception
"""

import curses as _curses  # http://www.amk.ca/python/howto/curses/curses.html
import curses.ascii as _curses_ascii
from time import sleep as _sleep
import sys as _sys
try:  # Python 3
    from io import StringIO as _StringIO
except ImportError:  # Python 2
    from StringIO import StringIO as _StringIO


__version__ = '0.3'


def quiet_sleep():
    _sleep(.1)

def _test_sleep():
    _sleep(.5)


class CheckForKeypress (object):
    def __init__(self, prompt="Press any key to continue",
                 timeout_ms=0, test_mode=False):
        self.test_mode = test_mode
        self.last = None  # last byte number read
        self.lasta = None # last as an ASCII character
        if test_mode == True:
            print(prompt)
            self.i = 0
            return None
        # redirect stderr to a file, because exiting curses mode clears
        # any error messages that had been printed to the screen
        _sys.stderr = _StringIO()
        # initialize raw curses mode
        self._active = True
        self.stdscr = _curses.initscr()
        _curses.noecho()
        _curses.cbreak()
        self.stdscr.scrollok(1)
        try:
            self.stdscr.addstr(0,0,prompt+'\n')
            if timeout_ms <= 0:
                self.stdscr.nodelay(True)
            else:
                self.stdscr.halfdelay(timeout_ms)
        except:
            self.cleanup()

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        if self.test_mode or not self._active:
            return None
        # return to standard terminal
        while self.input() != None : # eat up the buffer
            pass
        self.stdscr.scrollok(0)
        _curses.nocbreak()
        _curses.echo()
        _curses.endwin()
        # print any errors and restore stderr
        contents = _sys.stderr.getvalue()
        _sys.stderr = _sys.__stderr__
        if len(contents) > 0:
            _sys.stderr.write(contents)
        self._active = False

    def input(self):
        if self.test_mode == True:
            if self.i < 10:
                self.i += 1
                return None
            else:
                return "a"
        c = self.stdscr.getch()
        if c == _curses.ERR:
            return None
        else:
            self.last = c
            self.lasta = _curses_ascii.unctrl(c)
            return c

    def inputa(self):
        c = self.input()
        if c == None:
            return None
        else:
            return self.lasta

    def _output(self, string):
        if self.test_mode == True:
            _sys.stdout.write(string)
            return None
        #y,x = self.stdscr.getyx()
        self.stdscr.addstr(string)

    def _flush(self):
        if self.test_mode == True:
            return None
        self.stdscr.refresh()

    def output(self, string):
        self._output(string)
        self._flush()


if __name__ == '__main__':
    c = CheckForKeypress('testing...')
    i = 0
    i_max = 20
    try:
        while c.input() == None:
            c.output('{}/{} (sleeping)\n'.format(i, i_max))
            _test_sleep()
            if i >= i_max:
                raise Exception("you didn't press a key!")
            i += 1
    finally:
        c.cleanup()
