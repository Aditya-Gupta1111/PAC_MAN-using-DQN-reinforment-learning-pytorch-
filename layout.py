# layout.py
# Modernized Python-3 friendly version. Keeps API identical.

from util import manhattanDistance
from game import Grid
import os
import random
from functools import reduce


# Cache for visibility matrices
VISIBILITY_MATRIX_CACHE = {}


class Layout:
    """
    Static representation of the Pacman maze.
    Includes walls, food, capsules, agent positions, and visibility matrix.
    """

    def __init__(self, layoutText):
        self.width = len(layoutText[0])
        self.height = len(layoutText)

        self.walls = Grid(self.width, self.height, False)
        self.food = Grid(self.width, self.height, False)

        self.capsules = []
        self.agentPositions = []
        self.numGhosts = 0

        self.layoutText = layoutText
        self.processLayoutText(layoutText)
        self.totalFood = len(self.food.asList())

    def getNumGhosts(self):
        return self.numGhosts

    # -----------------------------------------------------
    #   Visibility matrix (used by advanced agents)
    # -----------------------------------------------------
    def initializeVisibilityMatrix(self):
        """
        Builds a mapping of visible cells from each cell in each direction.
        This is computationally expensive but cached.
        """
        global VISIBILITY_MATRIX_CACHE
        key = reduce(str.__add__, self.layoutText)

        if key not in VISIBILITY_MATRIX_CACHE:
            from game import Directions

            offsets = [(-0.5, 0), (0.5, 0), (0, -0.5), (0, 0.5)]
            dirs = [Directions.NORTH, Directions.SOUTH,
                    Directions.WEST, Directions.EAST]

            vis = Grid(
                self.width, self.height,
                {Directions.NORTH: set(),
                 Directions.SOUTH: set(),
                 Directions.EAST: set(),
                 Directions.WEST: set(),
                 Directions.STOP: set()}
            )

            # Visibility propagation
            for x in range(self.width):
                for y in range(self.height):
                    if not self.walls[x][y]:
                        for (dx, dy), direction in zip(offsets, dirs):
                            nextx, nexty = x + dx, y + dy

                            # Pseudo-continuous ray casting
                            while True:
                                ix, iy = int(nextx), int(nexty)
                                if ix < 0 or iy < 0 or ix >= self.width or iy >= self.height:
                                    break
                                if self.walls[ix][iy]:
                                    break

                                vis[x][y][direction].add((nextx, nexty))

                                nextx += dx
                                nexty += dy

            self.visibility = vis
            VISIBILITY_MATRIX_CACHE[key] = vis
        else:
            self.visibility = VISIBILITY_MATRIX_CACHE[key]

    # -----------------------------------------------------
    #   Basic helpers
    # -----------------------------------------------------
    def isWall(self, pos):
        x, y = pos
        return self.walls[x][y]

    def getRandomLegalPosition(self):
        """Return a random non-wall position."""
        while True:
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if not self.isWall((x, y)):
                return (x, y)

    def getRandomCorner(self):
        """Return one of the four corners."""
        poses = [
            (1, 1),
            (1, self.height - 2),
            (self.width - 2, 1),
            (self.width - 2, self.height - 2)
        ]
        return random.choice(poses)

    def getFurthestCorner(self, pacPos):
        """Return the corner farthest from Pacman."""
        poses = [
            (1, 1),
            (1, self.height - 2),
            (self.width - 2, 1),
            (self.width - 2, self.height - 2)
        ]
        return max(poses, key=lambda p: manhattanDistance(p, pacPos))

    def isVisibleFrom(self, ghostPos, pacPos, pacDirection):
        """Check if ghostPos is in the visibility set of pacPos."""
        row, col = int(pacPos[0]), int(pacPos[1])
        return ghostPos in self.visibility[row][col][pacDirection]

    def __str__(self):
        return "\n".join(self.layoutText)

    def deepCopy(self):
        return Layout(self.layoutText[:])

    # -----------------------------------------------------
    #   Parse layout text lines into walls/food/capsules/etc.
    # -----------------------------------------------------
    def processLayoutText(self, layoutText):
        """
        Parse characters in layout:
            % = Wall
            . = Food
            o = Capsule
            G = Ghost
            P = Pacman
            1,2,3,4 = Ghosts with IDs
        Layout lines are given top-to-bottom; we convert to our grid's bottom-to-top.
        """

        maxY = self.height - 1

        for y in range(self.height):
            for x in range(self.width):
                char = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, char)

        # Sort agent positions by ID: (0 for pacman, then ghosts)
        self.agentPositions.sort()

        # Convert the format to: (isPacman, position)
        self.agentPositions = [(i == 0, pos) for i, pos in self.agentPositions]

    def processLayoutChar(self, x, y, char):
        """Map a single character to game object(s)."""

        if char == '%':
            self.walls[x][y] = True

        elif char == '.':
            self.food[x][y] = True

        elif char == 'o':
            self.capsules.append((x, y))

        elif char == 'P':  # Pacman
            self.agentPositions.append((0, (x, y)))

        elif char == 'G':  # Ghost (generic)
            self.agentPositions.append((1, (x, y)))
            self.numGhosts += 1

        elif char in ['1', '2', '3', '4']:  # Specific ghost index
            self.agentPositions.append((int(char), (x, y)))
            self.numGhosts += 1


# -----------------------------------------------------
#   Layout file loading helpers
# -----------------------------------------------------
def getLayout(name, back=2):
    """
    Search for layout files up to `back` directories upward.
    Handles absolute names, filenames with or without .lay extension.
    """

    if name.endswith('.lay'):
        layout = tryToLoad('layouts/' + name) or tryToLoad(name)
    else:
        layout = tryToLoad('layouts/' + name + '.lay') or tryToLoad(name + '.lay')

    if layout is None and back > 0:
        curdir = os.path.abspath('.')
        os.chdir('..')
        layout = getLayout(name, back - 1)
        os.chdir(curdir)

    return layout


def tryToLoad(fullname):
    """Try reading a layout file and return a Layout object if successful."""
    if not os.path.exists(fullname):
        return None

    with open(fullname) as f:
        lines = [line.strip() for line in f]
    return Layout(lines)
