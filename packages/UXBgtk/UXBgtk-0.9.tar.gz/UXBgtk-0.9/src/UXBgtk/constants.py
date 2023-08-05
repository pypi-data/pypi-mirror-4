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
Created on 13 Sep 2012
@author: bob
"""

"""This file just collects all the configuration constants used by the game in
one place for ease of maintenance."""

import os

# define the resource paths
UI_BUILD_FILE = os.path.join(os.getcwd(), 'UXBgtk.glade')
UI_CSS_FILE = os.path.join(os.getcwd(), 'UXBgtk.css')
UI_GRAPHICS_PATH = os.path.join(os.getcwd(), 'images')

# define initial button sizes
TOOL_BUTTON_SIZE = 50
TOOL_SIZE = (TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
GRID_INITIAL_SIZE = 20
BUTTON_PAD = 10
GRID_SIZE = (GRID_INITIAL_SIZE, GRID_INITIAL_SIZE)

# dictionary of image file names and the tokens used in-game
IMAGE_NAMES = {
               # grid cell non-number images
               'Empty': 'Empty.gif',
               'Flag': 'Flag.gif',
               'Explosion': 'Explosion.gif',

               # toolbar button images
               'Quit': 'UXB.gif',
               'Win': 'VeryHappy.gif',
               'Lose': 'Confused.gif',
               'Start': 'Smile.gif',
               'Click': 'OMG.gif',
               'Hint': 'Unsure.gif',
               'PBC_Off': 'SquareNoLoop.gif',
               'PBC_On': 'SquareLoop.gif',

               # the numbers
               '1': '1.gif',
               '2': '2.gif',
               '3': '3.gif',
               '4': '4.gif',
               '5': '5.gif',
               '6': '6.gif',
               '7': '7.gif',
               '8': '8.gif',
               }

