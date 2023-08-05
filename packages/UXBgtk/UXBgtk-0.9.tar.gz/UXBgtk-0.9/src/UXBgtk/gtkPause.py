# Copyright (C) 2012 Bob Bowles <bobjohnbowles@gmail.com>
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

"""
Created on 7 Oct 2012
@author: Bob Bowles <bobjohnbowles@gmail.com>
Utility wait method for Gtk.
"""

from gi.repository import Gtk
import time


def pause(milliseconds):
    """
    Wait a predetermined time given in milliseconds, without blocking the Gtk
    event loop. Note the timing is approximate.
    """

    for hundredth in range(milliseconds // 10):
        while Gtk.events_pending():
            Gtk.main_iteration()
        time.sleep(.01)

