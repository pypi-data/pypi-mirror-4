# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

from __future__ import with_statement

import time
import os
import errno
import signal
from buildbot.scripts import base

def stop(config, signame="TERM", wait=False):
    basedir = config['basedir']
    quiet = config['quiet']

    if not base.isBuildmasterDir(config['basedir']):
        print "not a buildmaster directory"
        return 1

    pidfile = os.path.join(basedir, 'twistd.pid')
    try:
        with open(pidfile, "rt") as f:
            pid = int(f.read().strip())
    except:
        if not config['quiet']:
            print "buildmaster not running"
        return 0

    signum = getattr(signal, "SIG"+signame)
    try:
        os.kill(pid, signum)
    except OSError, e:
        if e.errno != errno.ESRCH:
            raise
        else:
            if not config['quiet']:
                print "buildmaster not running"
            try:
                os.unlink(pidfile)
            except:
                pass
            return 0

    if not wait:
        if not quiet:
            print "sent SIG%s to process" % signame
        return 0

    time.sleep(0.1)
    for _ in range(10):
        # poll once per second until twistd.pid goes away, up to 10 seconds
        try:
            os.kill(pid, 0)
        except OSError:
            if not quiet:
                print "buildbot process %d is dead" % pid
            return 0
        time.sleep(1)
    if not quiet:
        print "never saw process go away"
    return 1
