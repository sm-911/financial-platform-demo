"""LightGBM model wrapper implementing BaseModel interface.
"""
from . import BaseModel
import lightgbm as lgb

class LightGBMModel(BaseModel):
    def __init__(self, **params):
        self.model = lgb.LGBMRegressor(**params)
    def fit(self, X, y):
        self.model.fit(X, y)
    def predict(self, X):
        return self.model.predict(X)
    def name(self) -> str:
        return "LightGBM"
