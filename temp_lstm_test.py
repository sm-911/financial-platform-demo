import numpy as np
from models.lstm_model import prepare_lstm_data

# ---------- 3‑arg usage (pipeline style) ----------
X_tr = np.random.rand(10, 5)      # dummy features
y_tr = np.random.rand(10)        # dummy target
X_te = np.random.rand(4, 5)      # dummy test set

# unpack the four return values
X_tr_s, X_te_s, y_tr_s, scaler_y = prepare_lstm_data(X_tr, y_tr, X_te)

print('3‑arg output shapes:',
      [arr.shape for arr in (X_tr_s, X_te_s, y_tr_s)])  # ignore scaler_y

# ---------- legacy 1‑arg usage ----------
close = np.arange(100).astype(float)

# unpack the six return values
X_train, X_test, y_train, y_test, scaler, split = prepare_lstm_data(close)

print('legacy output shapes:',
      [arr.shape for arr in (X_train, X_test, y_train, y_test)])  # ignore scaler & split
