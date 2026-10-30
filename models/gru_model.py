"""GRU model wrapper implementing the BaseModel interface.
"""
from . import BaseModel
import torch
import torch.nn as nn
import numpy as np

class GRUModel(BaseModel):
    def __init__(self, input_dim: int = None, hidden_dim: int = 64, num_layers: int = 2, epochs: int = 10, lr: float = 1e-3):
        # If input_dim is not known at init, we will infer it on first fit.
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.epochs = epochs
        self.lr = lr
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.criterion = nn.MSELoss()
        self.optimizer = None

    def _build_model(self, input_dim):
        self.model = nn.GRU(input_dim, self.hidden_dim, self.num_layers, batch_first=True).to(self.device)
        self.fc = nn.Linear(self.hidden_dim, 1).to(self.device)
        self.optimizer = torch.optim.Adam(list(self.model.parameters()) + list(self.fc.parameters()), lr=self.lr)

    def fit(self, X, y):
        # X: (n_samples, n_features) numpy array
        # Convert to 3‑D tensor (batch, seq_len=1, features)
        X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1).to(self.device)
        y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1).to(self.device)
        if self.model is None:
            self._build_model(X.shape[1])
        self.model.train()
        self.fc.train()
        for epoch in range(self.epochs):
            self.optimizer.zero_grad()
            out, _ = self.model(X_tensor)
            pred = self.fc(out[:, -1, :])
            loss = self.criterion(pred, y_tensor)
            loss.backward()
            self.optimizer.step()
        # No return

    def predict(self, X):
        self.model.eval()
        self.fc.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1).to(self.device)
        with torch.no_grad():
            out, _ = self.model(X_tensor)
            pred = self.fc(out[:, -1, :])
        return pred.cpu().numpy().flatten()

    def name(self) -> str:
        return "GRU"
