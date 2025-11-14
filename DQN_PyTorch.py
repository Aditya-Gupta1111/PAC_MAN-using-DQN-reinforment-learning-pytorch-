# DQN_PyTorch.py
# A PyTorch implementation of the DQN model from DQN.py

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import os

class DQN(nn.Module):
    def __init__(self, params):
        super(DQN, self).__init__()
        self.params = params
        
        # --- Define the Network Architecture ---
        # The architecture is identical to the TensorFlow version.
        
        # Layer 1 (Convolutional)
        # 'padding=1' is used to replicate TensorFlow's 'padding=SAME'
        # for a 3x3 kernel.
        self.conv1 = nn.Conv2d(
            in_channels=6, 
            out_channels=16, 
            kernel_size=3, 
            stride=1, 
            padding=1
        )
        self.relu1 = nn.ReLU()

        # Layer 2 (Convolutional)
        self.conv2 = nn.Conv2d(
            in_channels=16, 
            out_channels=32, 
            kernel_size=3, 
            stride=1, 
            padding=1
        )
        self.relu2 = nn.ReLU()

        # Layer 3 (Fully connected)
        # We need to calculate the flattened size after the conv layers.
        # Original TF shape was [batch, width, height, 32]
        flat_size = 32 * params['width'] * params['height']
        self.fc3 = nn.Linear(in_features=flat_size, out_features=256)
        self.relu3 = nn.ReLU()

        # Layer 4 (Output)
        # 4 outputs, one for each action (North, East, South, West)
        self.fc4 = nn.Linear(in_features=256, out_features=4)

        # --- Optimizer and Loss Function ---
        self.optimizer = optim.Adam(self.parameters(), lr=params['lr'])
        self.loss_fn = nn.MSELoss() # MSE loss is equivalent to the TF cost function

        # --- Global Step and Model Loading ---
        self.global_step = 0
        if self.params['load_file'] is not None:
            if os.path.exists(self.params['load_file']):
                print('Loading checkpoint...')
                try:
                    # Load the saved model state
                    self.load_state_dict(torch.load(self.params['load_file']))
                    # Extract step count from the filename (e.g., 'model-smallGrid_10000_100')
                    step_str = self.params['load_file'].split('_')[-2]
                    self.global_step = int(step_str)
                    print(f"Loaded model, resuming from step {self.global_step}")
                except Exception as e:
                    print(f"Error loading model: {e}. Starting from scratch.")
            else:
                print(f"Could not find model at {self.params['load_file']}, starting from scratch.")


    def forward(self, x):
        """
        Defines the forward pass of the network.
        x is expected to be a tensor of shape [batch, 6, width, height]
        """
        # Pass through conv layers
        x = self.relu1(self.conv1(x))
        x = self.relu2(self.conv2(x))
        
        # Flatten the output for the fully connected layers
        # 'torch.flatten(x, 1)' flattens all dimensions except the batch dimension (dim 0)
        x = torch.flatten(x, 1) 
        
        # Pass through fully connected layers
        x = self.relu3(self.fc3(x))
        x = self.fc4(x) # Output raw Q-values
        return x

    def train_step(self, bat_s, bat_a, bat_t, bat_n, bat_r):
        """
        Performs a single training step.
        All inputs are numpy arrays from the replay memory.
        """
        
        # --- 1. Convert NumPy arrays to PyTorch Tensors ---
        bat_s = torch.from_numpy(bat_s).float()
        bat_a = torch.from_numpy(bat_a).float()
        bat_t = torch.from_numpy(bat_t).float()
        bat_n = torch.from_numpy(bat_n).float()
        bat_r = torch.from_numpy(bat_r).float()

        # --- 2. Permute state dimensions ---
        # The states are [batch, H, W, C]. We need [batch, C, H, W]
        # for PyTorch's Conv2d layers.
        bat_s = bat_s.permute(0, 3, 1, 2)
        bat_n = bat_n.permute(0, 3, 1, 2)

        # --- 3. Calculate Target Q-Values (yj) ---
        
        # Get Q-values for the *next* states (bat_n)
        # We use torch.no_grad() because we don't need to track gradients
        # for the target network's calculations.
        with torch.no_grad():
            q_next = self.forward(bat_n)
        
            # The target Q-value (q_t) is the maximum Q-value of the next state
            q_t = torch.max(q_next, dim=1)[0] # dim=1 is the action dimension
        
            # Calculate the Bellman equation target (yj)
            # yj = r + (1-t) * discount * q_t
            yj = bat_r + (1.0 - bat_t) * self.params['discount'] * q_t

        # --- 4. Calculate Predicted Q-Values ---
        
        # Get Q-values for the *current* states (bat_s)
        q_pred_all_actions = self.forward(bat_s)
        
        # Get the specific Q-value for the action that was *actually* taken (bat_a)
        # bat_a is one-hot, so (q_pred * bat_a) zeros out all non-taken actions.
        # torch.sum(..., dim=1) then selects the Q-value for the action we took.
        q_pred = torch.sum(q_pred_all_actions * bat_a, dim=1)

        # --- 5. Calculate Loss and Perform Update ---
        
        # Calculate the loss (MSE) between predicted and target Q-values
        loss = self.loss_fn(q_pred, yj)

        # Standard PyTorch training step
        self.optimizer.zero_grad() # Clear old gradients
        loss.backward()            # Calculate new gradients
        self.optimizer.step()      # Update network weights

        self.global_step += 1
        return self.global_step, loss.item() # .item() gets the scalar value of the loss

    def save_ckpt(self, filename):
        """Saves the model's state dictionary."""
        print(f"Saving model to {filename}")
        torch.save(self.state_dict(), filename)