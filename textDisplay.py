import time

# These globals are kept for compatibility with the original Pacman framework.
DRAW_EVERY = 1
SLEEP_TIME = 0      # Can be overridden externally or via PacmanGraphics(speed)
DISPLAY_MOVES = False
QUIET = False


class NullGraphics:
    """
    A display class used when no graphical output is desired.
    All methods are no-ops, ensuring the game loop proceeds normally.
    """

    def initialize(self, state, isBlue=False):
        pass

    def update(self, state):
        pass

    def checkNullDisplay(self):
        return True

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        # Still prints a state if someone explicitly calls draw()
        print(state)

    def updateDistributions(self, dist):
        pass

    def finish(self):
        pass


class PacmanGraphics:
    """
    Minimal text-based display for Pacman.
    Prints the board state to stdout every few moves and shows score.
    """

    def __init__(self, speed=None):
        # Override global sleep time if provided
        if speed is not None:
            global SLEEP_TIME
            SLEEP_TIME = speed

        self.turn = 0
        self.agentCounter = 0

        # `pacman.nearestPoint` is optional; import lazily.
        try:
            import pacman
            self.pacman_module = pacman
        except Exception:
            self.pacman_module = None

    def initialize(self, state, isBlue=False):
        """Print initial board representation."""
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state):
        """
        Called every time an agent moves.
        Prints score/move info and redraws based on DRAW_EVERY.
        """

        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents

        # Every full round of agent moves = 1 "turn"
        if self.agentCounter == 0:
            self.turn += 1

            # Optional verbose output showing Pacman + Ghost positions
            if DISPLAY_MOVES:
                self._printMoveInfo(state, numAgents)

            # Redraw maze occasionally (controlled by DRAW_EVERY)
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()

        # If game ends, always print final state
        if getattr(state, "_win", False) or getattr(state, "_lose", False):
            self.draw(state)

    def _printMoveInfo(self, state, numAgents):
        """Internal helper to print detailed turn information."""
        try:
            # Use pacman.nearestPoint if available
            if self.pacman_module:
                pacpos = self.pacman_module.nearestPoint(state.getPacmanPosition())
                ghosts = [
                    self.pacman_module.nearestPoint(state.getGhostPosition(i))
                    for i in range(1, numAgents)
                ]
            else:
                pacpos = state.getPacmanPosition()
                ghosts = [state.getGhostPosition(i) for i in range(1, numAgents)]

            print(
                f"{self.turn:4d}) P: {pacpos!s:<8} | "
                f"Score: {state.score:<5} | Ghosts: {ghosts}"
            )
        except Exception:
            # Fall back silently if anything goes wrong
            pass

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        """Print the string representation of the board."""
        print(state)

    def finish(self):
        pass
