#!/usr/bin/python

# Copyright (c) 2011 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import time

from lava_android_test.utils import stop_at_pattern

if len(sys.argv) == 1:
    adb_cmd = "adb"
else:
    adb_cmd = "adb -s %s" % (sys.argv[1])

logcat_cmd = '%s logcat' % (adb_cmd)
pattern = "Displayed org.zeroxlab.zeroxbenchmark/.Report"

if not stop_at_pattern(command=logcat_cmd, pattern=pattern, timeout=2400):
    print "0xbench Test: TIMEOUT Fail"
    sys.exit(1)

time.sleep(3)
sys.exit(0)
