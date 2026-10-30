"""XGBoost model wrapper implementing BaseModel interface.
"""
from . import BaseModel
import xgboost as xgb
import numpy as np

class XGBoostModel(BaseModel):
    def __init__(self, **params):
        self.model = xgb.XGBRegressor(objective='reg:squarederror', **params)
    def fit(self, X, y):
        self.model.fit(X, y)
    def predict(self, X):
        return self.model.predict(X)
    def name(self) -> str:
        return "XGBoost"
