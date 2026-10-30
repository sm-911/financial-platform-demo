"""CNN‑LSTM model wrapper implementing BaseModel.
"""
from . import BaseModel
import torch
import torch.nn as nn
import numpy as np

class CNNLSTMModel(BaseModel):
    def __init__(self, seq_len: int = 60, n_features: int = None, cnn_channels: int = 32,
                 lstm_hidden: int = 64, lstm_layers: int = 2, epochs: int = 10, lr: float = 1e-3):
        self.seq_len = seq_len
        self.n_features = n_features
        self.cnn_channels = cnn_channels
        self.lstm_hidden = lstm_hidden
        self.lstm_layers = lstm_layers
        self.epochs = epochs
        self.lr = lr
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.criterion = nn.MSELoss()
        self.optimizer = None

    def _build_model(self, n_features):
        # 1‑D conv over time dimension, flatten and dense layers
        self.model = nn.Sequential(
            nn.Conv1d(in_channels=n_features, out_channels=self.cnn_channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(self.cnn_channels, self.cnn_channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            nn.Flatten(),
            nn.Linear(self.cnn_channels * (self.seq_len // 2), self.lstm_hidden),
            nn.ReLU(),
            nn.Linear(self.lstm_hidden, 1)
        ).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

    def fit(self, X, y):
        # X shape: (samples, seq_len, n_features)
        if self.n_features is None:
            self.n_features = X.shape[2]
        if self.model is None:
            self._build_model(self.n_features)
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        X_tensor = X_tensor.permute(0, 2, 1)
        y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(-1).to(self.device)
        self.model.train()
        for epoch in range(self.epochs):
            self.optimizer.zero_grad()
            out = self.model(X_tensor)
            loss = self.criterion(out, y_tensor)
            loss.backward()
            self.optimizer.step()

    def predict(self, X):
        self.model.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        X_tensor = X_tensor.permute(0, 2, 1)
        with torch.no_grad():
            out = self.model(X_tensor)
        return out.cpu().numpy().flatten()

    def name(self) -> str:
        return "CNN‑LSTM"
