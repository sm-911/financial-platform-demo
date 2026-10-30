"""ARIMA / SARIMAX model wrapper implementing BaseModel.

Uses statsmodels.tsa.statespace.SARIMAX for multi‑step forecasting.
"""
from . import BaseModel
import pandas as pd
import numpy as np
import statsmodels.api as sm

class ARIMAModel(BaseModel):
    def __init__(self, order=(5,1,0), seasonal_order=(0,0,0,0), trend='c'):
        self.order = order
        self.seasonal_order = seasonal_order
        self.trend = trend
        self.model = None

    def fit(self, X, y=None):
        # X is a 1‑D array of the target series (close price).
        # statsmodels expects a pandas Series.
        if X.ndim > 1:
            X = X.ravel()
        series = pd.Series(X)
        self.model = sm.tsa.statespace.SARIMAX(series,
                                             order=self.order,
                                             seasonal_order=self.seasonal_order,
                                             trend=self.trend,
                                             enforce_stationarity=False,
                                             enforce_invertibility=False)
        self.results = self.model.fit(disp=False)
        return self

    def predict(self, X, steps=None):
        # X is ignored – we predict forward from the fitted series.
        if steps is None:
            steps = len(X)  # fallback: predict same length as input
        forecast = self.results.get_forecast(steps=steps)
        return np.array(forecast.predicted_mean)

    def name(self) -> str:
        return "ARIMA"
