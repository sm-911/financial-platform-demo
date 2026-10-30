"""CatBoost model wrapper implementing BaseModel interface.
"""
from . import BaseModel
import catboost as cb

class CatBoostModel(BaseModel):
    def __init__(self, **params):
        self.model = cb.CatBoostRegressor(verbose=False, **params)
    def fit(self, X, y):
        self.model.fit(X, y)
    def predict(self, X):
        return self.model.predict(X)
    def name(self) -> str:
        return "CatBoost"
