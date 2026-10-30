"""Transformer model wrapper implementing BaseModel.

Uses a simple PyTorch TransformerEncoder for time‑series regression.
"""
from . import BaseModel
import torch
import torch.nn as nn
import numpy as np

class TransformerModel(BaseModel):
    def __init__(self, d_model: int = 64, nhead: int = 8, num_layers: int = 3,
                 dim_feedforward: int = 128, dropout: float = 0.1,
                 epochs: int = 10, lr: float = 1e-3):
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.dim_feedforward = dim_feedforward
        self.dropout = dropout
        self.epochs = epochs
        self.lr = lr
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.criterion = nn.MSELoss()
        self.optimizer = None

    def _build_model(self, input_dim):
        # Linear projection to d_model
        self.input_proj = nn.Linear(input_dim, self.d_model).to(self.device)
        encoder_layer = nn.TransformerEncoderLayer(d_model=self.d_model, nhead=self.nhead,
                                                   dim_feedforward=self.dim_feedforward,
                                                   dropout=self.dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=self.num_layers).to(self.device)
        self.fc_out = nn.Linear(self.d_model, 1).to(self.device)
        self.optimizer = torch.optim.Adam(list(self.input_proj.parameters()) +
                                          list(self.transformer_encoder.parameters()) +
                                          list(self.fc_out.parameters()), lr=self.lr)

    def fit(self, X, y):
        # X shape: (samples, seq_len, features)
        if self.model is None:
            self._build_model(X.shape[2])
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(-1).to(self.device)
        self.transformer_encoder.train()
        self.input_proj.train()
        self.fc_out.train()
        for epoch in range(self.epochs):
            self.optimizer.zero_grad()
            proj = self.input_proj(X_tensor)  # (batch, seq, d_model)
            enc = self.transformer_encoder(proj)  # (batch, seq, d_model)
            # Use the representation of the last time step
            out = self.fc_out(enc[:, -1, :])
            loss = self.criterion(out, y_tensor)
            loss.backward()
            self.optimizer.step()

    def predict(self, X):
        self.transformer_encoder.eval()
        self.input_proj.eval()
        self.fc_out.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            proj = self.input_proj(X_tensor)
            enc = self.transformer_encoder(proj)
            out = self.fc_out(enc[:, -1, :])
        return out.cpu().numpy().flatten()

    def name(self) -> str:
        return "Transformer"
