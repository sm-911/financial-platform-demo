"""LSTM model using PyTorch with CUDA GPU acceleration."""

import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# Auto-detect CUDA GPU (NVIDIA RTX 4050) or fallback to CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class PyTorchLSTM(nn.Module):
    def __init__(self, input_size=10, hidden_size=config.LSTM_UNITS, dropout=config.LSTM_DROPOUT):
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.dropout(out[:, -1, :])
        out = self.relu(self.fc1(out))
        return self.fc2(out)


def prepare_lstm_data(*args, **kwargs):
    """Scale data for LSTM training.
    Supports two call signatures:
    1. ``prepare_lstm_data(X_train, y_train, X_test)`` → returns ``X_tr_s, X_te_s, y_tr_s, scaler_y``
    2. ``prepare_lstm_data(close_prices)`` (legacy) → returns ``X_train, X_test, y_train, y_test, scaler, split``
    The appropriate format is chosen based on the number of positional arguments.
    """
    # New three‑argument API used by the pipeline
    if len(args) == 3:
        X_train, y_train, X_test = args
        scaler_x = StandardScaler().fit(X_train)
        X_tr_s = scaler_x.transform(X_train)[:, None, :]
        X_te_s = scaler_x.transform(X_test)[:, None, :]
        scaler_y = StandardScaler().fit(y_train.reshape(-1, 1))
        y_tr_s = scaler_y.transform(y_train.reshape(-1, 1)).flatten()
        return X_tr_s, X_te_s, y_tr_s, scaler_y

    # Legacy single‑argument API (kept for backward compatibility)
    if len(args) == 1:
        close_prices = args[0]
        test_ratio = kwargs.get('test_ratio', config.TEST_SPLIT)
        lookback = kwargs.get('lookback', config.LSTM_LOOKBACK)
        split = int(len(close_prices) * (1 - test_ratio))

        scaler = StandardScaler()
        scaler.fit(close_prices[:split].reshape(-1, 1))
        scaled = scaler.transform(close_prices.reshape(-1, 1)).flatten()

        X_train = np.array([scaled[i - lookback:i] for i in range(lookback, split)])[:, :, None]
        y_train = scaled[lookback:split]
        X_test = np.array([scaled[i - lookback:i] for i in range(split, len(scaled))])[:, :, None]
        y_test = scaled[split:]
        return X_train, X_test, y_train, y_test, scaler, split

    raise ValueError("prepare_lstm_data expects either 3 positional arguments (X_train, y_train, X_test) or 1 (close_prices)")
    


def train_lstm(X_train_s: np.ndarray, y_train_s: np.ndarray):
    """Train PyTorch LSTM with GPU acceleration if CUDA is available."""
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"  -> Training LSTM on [{DEVICE.type.upper()}: {device_name}]...")

    val_size = max(1, int(len(X_train_s) * 0.1))
    X_tr, y_tr = X_train_s[:-val_size], y_train_s[:-val_size]
    X_val, y_val = X_train_s[-val_size:], y_train_s[-val_size:]

    train_loader = DataLoader(
        TensorDataset(torch.tensor(X_tr, dtype=torch.float32), torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1)),
        batch_size=config.LSTM_BATCH_SIZE,
        shuffle=True
    )
    X_val_t = torch.tensor(X_val, dtype=torch.float32).to(DEVICE)
    y_val_t = torch.tensor(y_val, dtype=torch.float32).unsqueeze(1).to(DEVICE)

    model = PyTorchLSTM(input_size=X_train_s.shape[2]).to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.008)

    history = {"loss": [], "val_loss": []}
    best_loss = float("inf")
    best_weights = None
    patience, patience_counter = 12, 0

    for epoch in range(config.LSTM_EPOCHS):
        model.train()
        batch_losses = []
        for bx, by in train_loader:
            bx, by = bx.to(DEVICE), by.to(DEVICE)
            optimizer.zero_grad()
            pred = model(bx)
            loss = criterion(pred, by)
            loss.backward()
            optimizer.step()
            batch_losses.append(loss.item())

        model.eval()
        with torch.no_grad():
            v_loss = criterion(model(X_val_t), y_val_t).item()

        epoch_loss = float(np.mean(batch_losses))
        history["loss"].append(epoch_loss)
        history["val_loss"].append(v_loss)

        if v_loss < best_loss:
            best_loss = v_loss
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

    if best_weights:
        model.load_state_dict({k: v.to(DEVICE) for k, v in best_weights.items()})

    print(f"     Done. {len(history['loss'])} epochs | val_loss={history['val_loss'][-1]:.6f}")
    return model, history


def predict_lstm(model, X_test_s: np.ndarray, scaler) -> np.ndarray:
    """Predict and inverse-transform scaled predictions back to rupees."""
    model.eval()
    with torch.no_grad():
        x_t = torch.tensor(X_test_s, dtype=torch.float32).to(DEVICE)
        preds_s = model(x_t).cpu().numpy()
    return scaler.inverse_transform(preds_s.reshape(-1, 1)).flatten()


def plot_training_loss(history):
    """Plot training/validation loss over epochs.
    Accepts either a Keras‑style History object (with ``.history``) or a plain dict.
    Returns the Figure – the caller will encode it.
    """
    # Support both dict and History‑like objects
    if hasattr(history, "history"):
        loss = history.history.get("loss", [])
        val_loss = history.history.get("val_loss", [])
    else:
        loss = history.get("loss", [])
        val_loss = history.get("val_loss", [])
    epochs = range(1, len(loss) + 1)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(epochs, loss, "b-", label="Training loss")
    if val_loss:
        ax.plot(epochs, val_loss, "r--", label="Validation loss")
    ax.set_title("LSTM – Training Loss", fontsize=13, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    return fig  # <-- return instead of plt.show()
