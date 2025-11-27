# Pacman using DQN (Reinforcement Learning)

This project implements a Deep Q-Network (DQN) agent to play Pacman, developed as a course project for **EE5531: Reinforcement Learning based Control**. The agent learns to navigate the maze, eat food, and avoid ghosts using raw state representations processed by a Convolutional Neural Network (CNN).

## Project Overview

The goal of this project is to train a Pacman agent using Deep Reinforcement Learning. The agent observes the game state (walls, food, ghosts, capsules, etc.) as a set of grid matrices and outputs the best action (North, South, East, West) to maximize its score.

### Key Features
*   **Deep Q-Network (DQN)**: Uses a CNN with 2 convolutional layers and 2 fully connected layers to approximate the Q-value function.
*   **Experience Replay**: Stores transitions (state, action, reward, next_state) in a replay memory to break correlations between consecutive samples during training.
*   **Epsilon-Greedy Exploration**: Balances exploration (random actions) and exploitation (best known actions) with a decaying epsilon value.
*   **State Representation**: The game state is converted into a multi-channel grid representation (Walls, Pacman, Ghosts, Scared Ghosts, Food, Capsules).
*   **PyTorch Implementation**: The model is built and trained using PyTorch.

## Requirements

*   Python 3.x
*   PyTorch
*   NumPy

You can install the dependencies using pip:

```bash
pip install torch numpy
```

## Usage

The main entry point for the game is `pacman.py`. You can run the Pacman agent with various command-line options.

### Training the Agent

To train the DQN agent, run the following command:

```bash
python pacman.py -p PacmanDQN -n 6000 -x 5000 -l smallGrid
```

**Arguments:**
*   `-p PacmanDQN`: Specifies the agent to use (our DQN agent).
*   `-n 6000`: Total number of games to play.
*   `-x 5000`: Number of training episodes (exploration and learning happen here). The remaining 1000 games will be for testing (exploitation).
*   `-l smallGrid`: Specifies the layout map. You can use other layouts found in the `layouts` directory (e.g., `mediumGrid`, `smallClassic`).

### Other Useful Options

*   `-g RandomGhost`: Specifies the ghost agent type (default is RandomGhost).
*   `-k 2`: Number of ghosts.
*   `-z 1.0`: Zoom level for the graphics.
*   `--frameTime 0.0`: Speed of the game (0 is fastest).

### Example: Quick Training Session

```bash
python pacman.py -p PacmanDQN -n 200 -x 150 -l smallGrid
```

## File Structure

*   `pacman.py`: The main file that runs the game. Handles game logic and command-line arguments.
*   `DQN_PyTorch.py`: Defines the PyTorch neural network architecture (`DQN` class).
*   `pacmanDQN_Agents.py`: Implements the `PacmanDQN` agent, including the training loop, experience replay, and state preprocessing.
*   `game.py`: Defines the core game logic (GameState, Agent, Grid, etc.).
*   `ghostAgents.py`: Defines ghost agents (e.g., RandomGhost, DirectionalGhost).
*   `graphicsDisplay.py` / `textDisplay.py`: Handles the game visualization.
*   `util.py`: Utility functions.

## Logs and Saves

*   **Logs**: Training logs are saved in the `logs/` directory.
*   **Models**: Checkpoints of the trained model are saved in the `saves/` directory (e.g., `model.pth`).

## Credits

*   **Course**: EE5531 Reinforcement Learning based Control
*   **Base Code**: Adapted from the UC Berkeley AI Pacman project.
