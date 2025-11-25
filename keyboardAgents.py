from game import Agent
from game import Directions
import random

# KeyboardAgent: controls Pacman with keys (default WASD or arrow keys)
class KeyboardAgent(Agent):
    """
    An agent controlled by the keyboard.
    Arrow keys also work (via graphicsUtils key handling).
    """

    WEST_KEY = 'a'
    EAST_KEY = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__(self, index=0):
        # maintain Agent indexing
        super().__init__(index)
        self.lastMove = Directions.STOP
        self.index = index
        self.keys = []

    def getAction(self, state):
        """
        Read current key presses and return a legal move.
        Falls back to a random legal action if necessary.
        """
        # Import lazily to avoid cyclic imports when running headless tests
        from graphicsUtils import keys_waiting, keys_pressed

        keys = keys_waiting() + keys_pressed()
        if keys:
            self.keys = keys

        legal = state.getLegalActions(self.index)
        move = self.getMove(legal)

        # If stop chosen, prefer previous move if still legal
        if move == Directions.STOP and self.lastMove in legal:
            move = self.lastMove

        # STOP key forces a stop if legal
        if (self.STOP_KEY in self.keys) and Directions.STOP in legal:
            move = Directions.STOP

        if move not in legal:
            # choose a random legal action to avoid illegal moves
            move = random.choice(legal)

        self.lastMove = move
        return move

    def getMove(self, legal):
        """Map current keys to a direction if that direction is legal."""
        move = Directions.STOP
        if (self.WEST_KEY in self.keys or 'Left' in self.keys) and Directions.WEST in legal:
            move = Directions.WEST
        if (self.EAST_KEY in self.keys or 'Right' in self.keys) and Directions.EAST in legal:
            move = Directions.EAST
        if (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Directions.NORTH in legal:
            move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Directions.SOUTH in legal:
            move = Directions.SOUTH
        return move


# KeyboardAgent2: alternative keys for a second player
class KeyboardAgent2(KeyboardAgent):
    """
    A second agent controlled by the keyboard (uses IJKL).
    """

    WEST_KEY = 'j'
    EAST_KEY = 'l'
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal):
        move = Directions.STOP
        if (self.WEST_KEY in self.keys) and Directions.WEST in legal:
            move = Directions.WEST
        if (self.EAST_KEY in self.keys) and Directions.EAST in legal:
            move = Directions.EAST
        if (self.NORTH_KEY in self.keys) and Directions.NORTH in legal:
            move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys) and Directions.SOUTH in legal:
            move = Directions.SOUTH
        return move
