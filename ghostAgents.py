from game import Agent, Actions, Directions
from util import manhattanDistance, Counter, raiseNotDefined
import util
import random


class GhostAgent(Agent):
    """
    Base class for all ghost agents.
    Each ghost must define getDistribution(), which returns a Counter
    giving a probability distribution over legal actions.
    """

    def __init__(self, index):
        super().__init__(index)

    def getAction(self, state):
        """
        Sample an action from the distribution returned by getDistribution().
        """
        dist = self.getDistribution(state)
        if not dist:
            return Directions.STOP
        return util.sample(dist)

    def getDistribution(self, state):
        """
        Returns: Counter(action -> probability)
        Must be implemented in subclasses.
        """
        raiseNotDefined()


class RandomGhost(GhostAgent):
    """
    Chooses uniformly among all legal actions.
    """

    def getDistribution(self, state):
        legal = state.getLegalActions(self.index)
        dist = Counter()
        for a in legal:
            dist[a] = 1.0
        dist.normalize()
        return dist


class DirectionalGhost(GhostAgent):
    """
    A ghost that:
      - Moves toward Pacman when not scared (attack mode)
      - Moves away from Pacman when scared (flee mode)
    """

    def __init__(self, index, prob_attack=0.8, prob_scaredFlee=0.8):
        super().__init__(index)
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state):
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)

        isScared = ghostState.scaredTimer > 0
        speed = 0.5 if isScared else 1

        # Compute new positions for each legal action
        actionVectors = [Actions.directionToVector(a, speed) for a in legalActions]
        newPositions = [(pos[0] + dx, pos[1] + dy) for (dx, dy) in actionVectors]

        pacmanPos = state.getPacmanPosition()

        # Compute distances from each new position to Pacman
        distances = [manhattanDistance(p, pacmanPos) for p in newPositions]

        # Choose whether to chase or flee
        if isScared:
            bestScore = max(distances)               # maximize distance when scared
            chooseProb = self.prob_scaredFlee
        else:
            bestScore = min(distances)               # minimize distance when attacking
            chooseProb = self.prob_attack

        # Best actions (either closest or farthest)
        bestActions = [
            action for action, dist in zip(legalActions, distances)
            if dist == bestScore
        ]

        # Build a distribution over all actions
        dist = Counter()

        # Assign majority probability to best actions
        bestCount = len(bestActions)
        for a in bestActions:
            dist[a] = chooseProb / bestCount

        # Spread remaining probability uniformly across all legal actions
        remainProb = (1 - chooseProb) / len(legalActions)
        for a in legalActions:
            dist[a] += remainProb

        dist.normalize()
        return dist
