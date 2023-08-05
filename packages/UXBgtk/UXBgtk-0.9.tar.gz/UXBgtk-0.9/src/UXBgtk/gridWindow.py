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

from gi.repository import Gtk
from GtkGridWorkaround import Grid    # TODO: remove after Ubuntu 12.10
import random
from gridButton import GridButton
from getImage import updateImage
from constants import TOOL_SIZE, BUTTON_PAD



class GridWindow(Gtk.Frame):
    """This class defines the layout of the grid buttons for the game."""

    def __init__(self, parent=None, rows=1, cols=1, mines=[]):
        super().__init__()

        # reference to the parent object
        self.parent = parent

        # define the rows and columns
        self.rows = rows
        self.cols = cols

        # the randomised list of mines
        self.nmines = mines.count(True)
        self.mines = mines
        self.exploded = False # if a bomb has been hit
        self.gameOver = False # flag for game over - used for cleardown

        # tally of exposed minefield squares
        self.exposed = 0

        # the number of flags in use
        self.flags = 0

        # a convenient way to keep a reference to all the buttons
        self.buttons = list()

        # try to fix the aspect ratio of the grid by using an AspectFrame
        self.frame = Gtk.AspectFrame(label=None,
                                     xalign=0.5,
                                     yalign=0.5,
                                     ratio=self.cols / self.rows,
                                     obey_child=False)
        self.add(self.frame)

        # define the grid for the game
        # TODO: change constructor on upgrade to Ubuntu 12.10        
#        self.grid = Gtk.Grid()
        self.grid = Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.frame.add(self.grid)

        self.createWidgets()


    def createWidgets(self):
        """Make up the grid of buttons for the game."""

        for x in range(self.cols):
            for y in range(self.rows):

                # grid button
                button = GridButton(parent=self,
                                    pos=(x, y),
                                    mined=self.mines.pop())
                self.grid.attach(button, x, y, 1, 1)
                self.buttons.append(button)


    def start(self):
        """Prepare the grid before the player starts pressing buttons..."""

        # work out the neighbour bomb counts for this game
        for button in self.buttons:
            button.updateNeighbourMines()


    def incrementExposedCount(self, increment):
        """Every time a button is exposed increment the count. When the count is
        big enough the game has been won."""

        # no count required during cleardown
        if self.gameOver: return

        self.exposed += increment
        self.parent.exposedCount.set_text(str(self.exposed))

        # test if we have won
        self.haveWeWonYet()


    def updateFlags(self, increment):
        """Increment or decrement the count of flags used when notified of
        a change. The Boolean increment argument determines whether we add or
        remove from the tally."""

        if increment: self.flags += 1
        else: self.flags -= 1
        self.parent.flagCount.set_text(str(self.flags))

        # test if we have won
        if not self.gameOver: self.haveWeWonYet()


    def haveWeWonYet(self):
        """Have we won yet?"""

        if self.exploded: self.endGame(False)

        elif not ((self.rows * self.cols) - (self.flags + self.exposed)) \
                  and not (self.flags - self.nmines):
            self.endGame(True)


    def endGame(self, success):
        """Finish the game."""

        self.gameOver = True # avoids recursion issues during cleardown

        # clear down the grid
        for button in self.buttons:
            if button.exposed: continue

            elif button.flagged:
                if button.mined: # button correctly flagged
                    button.set_sensitive(False)

                else: # incorrect flag - remove it
                    button.flagged = False
                    button.set_active(True)
                    self.updateFlags(False)

            # 'press' the button
            button.leftMouse(button)

        # update the start button image
        if success:
            updateImage(self.parent.startImage, 'Win', TOOL_SIZE)
        else:
            updateImage(self.parent.startImage, 'Lose', TOOL_SIZE)

        # update the sensitivity of the other toolbar buttons
        self.parent.hintButton.set_sensitive(False)
        self.parent.pbcButton.set_sensitive(True)
        self.parent.configurationBox.set_button_sensitivity(
                                                        Gtk.SensitivityType.ON)


    def giveHint(self):
        """Find an unplayed, unmined button near a played button and reveal it.
        """

        # get a randomised list of all the buttons
        buttons = self.buttons[:]
        random.shuffle(buttons)

        # find an unplayed, unmined button
        for button in buttons:
            if button.mined or button.exposed or button.flagged: continue

            # if this is not the start of the game check the button's neighbours
            if (self.flags + self.exposed):
                for neighbour in button.neighbourList:
                    if neighbour.exposed or neighbour.flagged:
                        button.leftMouse(button)
                        return

            # at the start of the game no need to check neighbours
            else:
                # look for a button with no neighbour mines
                if not button.neighbourMines:
                    # left-click the button
                    button.leftMouse(button)
                    return


    def resize(self, allocation):
        """Defines the resize behaviour of the button grid. The allocation is
        taken from the gridContainer in the parent window."""

        # work out the best size for the grid buttons
        gridWidth = allocation.width
        gridHeight = allocation.height

        # choose the smaller dimension for scaling the images
        imageWidth = gridWidth // self.cols - 10
        imageHeight = gridHeight // self.rows - 10
        imageSize = min(imageWidth, imageHeight)

        # now tell the buttons to sort themselves out
        for button in self.buttons:
            button.resize((imageSize, imageSize))
