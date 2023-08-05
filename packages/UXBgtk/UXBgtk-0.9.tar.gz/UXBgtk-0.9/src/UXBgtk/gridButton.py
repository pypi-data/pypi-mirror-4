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
from getImage import getImage, updateImage
from gtkPause import pause
from constants import TOOL_SIZE, GRID_SIZE, BUTTON_PAD


# grid direction vectors (8 points of the compass)
directions = []
for x in range(-1, 2):
    for y in range(-1, 2):
        # we skip the centre
        if not (x == y == 0): directions.append((x, y))



class GridButton(Gtk.ToggleButton):
    """Visual representation of a minefield grid square. Contains all the
    information it needs to display itself and interact with the game."""


    def __init__(self, parent=None, pos=None, mined=False):
        """Do the class initialization and prepare the game-specific
        attributes."""

        super().__init__()

        # the game grid parent
        self.parent = parent

        # this button's grid position.
        self.pos = pos

        # is this button mined?
        self.mined = mined
        self.exploded = False

        # is this button flagged? - initialize to False
        self.flagged = False

        # initialize the mine count to zero
        self.neighbourMines = 0

        # initialize the neighbour flag count to zero
        self.neighbourFlags = 0

        # flag to emulate disabled when mines are exposed
        self.exposed = False

        # initialize the image to empty at 20 pixels
        self.imageKey = 'Empty'
        self.imageSize = GRID_SIZE
        self.image = getImage(self.imageKey)
        self.add(self.image)
        updateImage(self.image, self.imageKey, self.imageSize)

        # set up the GTK event handlers
        self.connect("button_press_event", self.on_button_press_event)
        self.connect("button_release_event", self.on_button_release_event)


    def updateNeighbourMines(self):
        """Update the number of neighbouring mines after initialization. This
        only happens at the start of each game, but the cache of neighbours is
        used later."""

        # decide if periodic boundaries are being applied
        pbc = self.parent.parent.pbcButton.get_active()

        # initialize the list of neighbours
        self.neighbourList = []
        for dir in directions:
            x = self.pos[0] + dir[0]
            y = self.pos[1] + dir[1]

            # grid boundary conditions
            if x < 0 or x >= self.parent.cols or \
               y < 0 or y >= self.parent.rows:
                if pbc:             # apply periodic constraints to grid numbers
                    x = x % self.parent.cols
                    y = y % self.parent.rows
                else: continue      # no neighbours beyond grid edge

            neighbour = self.parent.grid.get_child_at(x, y)
            self.neighbourList.append(neighbour)

            # count the neighbours that are mined
            if neighbour.mined: self.neighbourMines += 1


    def updateNeighbourFlags(self, increment):
        """Increment or decrement the count of neighbour flags when notified of
        a change. The Boolean increment argument determines whether we add or
        remove from the tally."""

        if increment: self.neighbourFlags += 1
        else: self.neighbourFlags -= 1


    def resize(self, imageSize):
        """Resize the grid button's child (image or text) to match the current
        window size. (The button looks after itself.)"""

        self.imageSize = imageSize
        updateImage(self.image, self.imageKey, self.imageSize)


    def on_button_press_event(self, widget, event):
        """Event handler for button presses. The handler must decide which
        mouse button was clicked. We are only interested in leftMouse clicks."""

        # determine left- or right- click, feed the appropriate method. 
        if event.get_button()[1] == 1: # left-mouse
            updateImage(self.parent.parent.startImage, 'Click', TOOL_SIZE)
#        else:
#            print('Event button # is ' + str(event.get_button())
#                  + '... not handled')


    def on_button_release_event(self, widget, event):
        """Event handler for button releases. The handler must decide which
        mouse button was clicked. The invocation is forwarded to leftMouse() or
        rightMouse()."""

        # determine left- or right- click, feed the appropriate method.
        if event.get_button()[1] == 1: # left-mouse
            self.leftMouse(widget)
        elif event.get_button()[1] == 3: # right-mouse
            self.rightMouse()
#        else:
#            print('Mouse button ' + str(event.get_button())
#                  + ' not handled')


    def leftMouse(self, widget):
        """Left-Mouse handler. We use this to clear the area."""

        # action exclusions
        if self.exposed: return False
        if self.flagged: return False
        if self.exploded: return False

        # disable the button and change its colour once it has been left-clicked
        self.set_sensitive(False)
        if not self.parent.exploded: self.set_active(True)

        exposedNeighbours = 0

        # end game - we hit a mine - lose
        if self.mined:
            self.exploded = True

            # choose the image
            if self.parent.exploded: # cleardown mode
                self.imageKey = 'Quit'
            else: # normal mode
                self.set_active(True)
                self.imageKey = 'Explosion' # lose

            updateImage(self.image, self.imageKey, self.imageSize)

            # short pause to let gtk events sort themselves out
            if not self.parent.exploded:
                pause(200)
                self.parent.exploded = True # notify end-game

        else: # expose the button, display the number of neighbour mines
            self.exposed = True

            # update the image
            self.imageKey = 'Empty'
            if self.neighbourMines > 0:
                self.imageKey = str(self.neighbourMines)
            updateImage(self.image, self.imageKey, self.imageSize)

            # propagate exposure to the neighbours if mines = flags
            if self.neighbourFlags == self.neighbourMines:
                for neighbour in self.neighbourList:
                    exposedNeighbours += neighbour.leftMouse(widget)

        # update count of exposed buttons - potential win end game
        exposedNeighbours += 1 # add self to the count
        if widget == self:
            self.parent.incrementExposedCount(exposedNeighbours)

            # reset the start button image
            if not self.parent.gameOver:
                updateImage(self.parent.parent.startImage, 'Start', TOOL_SIZE)

        else: return exposedNeighbours


    def rightMouse(self):
        """Right-Mouse handler. We use this to toggle mine flags."""

        # action exclusions
        if not self.get_sensitive(): return
        if self.exposed: return

        # toggle the flag state
        self.flagged = not self.flagged
        self.set_active(self.flagged)

        # update the button image
        if self.flagged:
            self.imageKey = 'Flag'
        else:
            self.imageKey = 'Empty'
        updateImage(self.image, self.imageKey, self.imageSize)

        # notify neighbours and parent of the change
        self.parent.updateFlags(self.flagged)
        for neighbour in self.neighbourList:
            neighbour.updateNeighbourFlags(self.flagged)
