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
Module: GtkGridWorkaround
Created on: 29 Sep 2012
@author: Bob Bowles <bobjohnbowles@gmail.com>

This module contains workarounds for Gtk.Grid
"""

from gi.repository import Gtk



class Grid(Gtk.Grid):
    """
    This is a workaround for the missing method get_child_at in the Gtk.Grid
    API. It is expected this can be removed after release of the new Gtk
    bindings in Ubuntu 12.10.
    This implementation is NOT robust, as several methods that are related are
    not implemented. Also, there is no error checking, and positioning of
    multiple widgets in the same location is not checked or allowed for.
    NOTE:
    Grid Keys: are (x, y) tuples for the child coordinates.
    Grid Values: are (child, width, height) tuples of the child and its
    grid dimensions.
    """


    def __init__(self, *args):
        """
        Constructor
        """

        # make a dictionary so we can remember the grid's children
        self.grid = dict()

        super().__init__(*args)


    def attach(self, child, left, top, width, height):
        """
        Override the attach method to populate the dictionary
        """

        # populate the dictionary
        self.grid[(left, top)] = child, width, height

        super().attach(child, left, top, width, height)


    def get_child_at(self, x, y):
        """
        The missing method to get a child from a specified grid location.
        Returns the widget at the specified grid coordinates.
        """

        # TODO: what happens if the child spans multiple rows/columns and an intermediate x,y is given?

        childDetails = self.grid[(x, y)]
        return childDetails[0]


"""
TODO: The code below is all screwed up. Need to understand how the parent class
does this. For now I don't need it, it is not worth the effort.
"""
#
#
#    def attach_next_to(self, child, sibling, side, width, height):
#        """
#        Override the attach_next_to method to populate the dictionary
#        """
#
#        childCoords = (None, None)
#
#        # for no sibling given use the side to work out the coordinates
#        if sibling == None:
#
#            if side == Gtk.PositionType.BOTTOM \
#            or side == Gtk.PositionType.RIGHT: # add child to top left corner
#                childCoords = (0, 0)
#
#            else: # add the child to the bottom right
#                # TODO: how to work out the coordinates of 'bottom right'?
#                print('WARNING: bottom right not currently implemented: ' +
#                      'Coordinates not defined.')
#
#        else: # use the sibling's coordinates
#            siblingCoords = (None, None, None, None)
#            for coords, widgetDetails in self.grid.items():
#                widget, widgetWidth, widgetHeight = tuple(widgetDetails)
#                if widget == sibling:
#                    siblingCoords = coords[0], coords[1], \
#                                    widgetWidth, widgetHeight
#                    break
#
#            # work out the child's coordinates using the side and sibling coords
#            sibX, sibY, sibW, sibH = tuple(siblingCoords)
#            if side == Gtk.PositionType.BOTTOM: # add the child below sibling
#                childCoords = sibX, (sibY + sibH)
#            elif side == Gtk.PositionType.RIGHT: # add the child to the right
#                childCoords = (sibX + sibW), sibY
#            elif side == Gtk.PositionType.TOP: # add the child above sibling
#                childCoords = sibX, (sibY - height)
#            elif side == Gtk.PositionType.LEFT: # child on the left of sibling
#                childCoords = (sibX - width), sibY
#
#        # add the child to the dictionary at the determined location
#        self.grid[childCoords] = child, width, height
#
#        super().attach_next_to(child, sibling, side, width, height)

