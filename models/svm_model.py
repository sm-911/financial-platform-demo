"""SVM model wrapper implementing BaseModel.
"""
from . import BaseModel
from sklearn.svm import SVR
import numpy as np

class SVMModel(BaseModel):
    def __init__(self, C: float = 1.0, epsilon: float = 0.1, kernel: str = 'rbf'):
        self.C = C
        self.epsilon = epsilon
        self.kernel = kernel
        self.model = SVR(C=self.C, epsilon=self.epsilon, kernel=self.kernel)

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def name(self) -> str:
        return "SVM"
