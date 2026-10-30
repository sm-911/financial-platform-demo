"""Random Forest regressor: train and plot feature importances."""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from data.stock_data import FEATURE_COLS


def train_random_forest(X_train: np.ndarray, y_train: np.ndarray) -> RandomForestRegressor:
    """Fit and return a trained RandomForestRegressor."""
    print("  -> Training Random Forest...")
    model = RandomForestRegressor(
        n_estimators=config.RF_N_ESTIMATORS,
        max_depth=config.RF_MAX_DEPTH,
        random_state=config.RF_RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    print(f"     Done. ({config.RF_N_ESTIMATORS} trees)")
    return model


def plot_feature_importance(model: RandomForestRegressor):
    """Horizontal bar chart of feature importances.
    Returns the Figure – do NOT call plt.show().
    """
    imp  = model.feature_importances_
    idx  = np.argsort(imp)
    feats = [FEATURE_COLS[i] for i in idx]

    fig, ax = plt.subplots(figsize=(9, 5))          # a bit wider
    bars = ax.barh(feats, imp[idx], color="#1f77b4", edgecolor="white")
    for bar, val in zip(bars, imp[idx]):
        ax.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                f"{val*100:.1f}%", va="center", fontsize=9)

    ax.set_title("Random Forest – Feature Importances", fontsize=13, fontweight="bold")
    ax.set_xlabel("Importance")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    return fig           # <-- return instead of plt.show()