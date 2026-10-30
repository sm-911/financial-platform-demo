"""Model package exposing a unified BaseModel interface for all forecasting algorithms."""

class BaseModel:
    """Simple interface all models implement.
    
    Methods
    -------
    fit(self, X, y):
        Train the model.
    predict(self, X):
        Return predictions.
    name(self) -> str:
        Human readable name.
    """
    def fit(self, X, y):
        raise NotImplementedError
    def predict(self, X):
        raise NotImplementedError
    def name(self) -> str:
        return self.__class__.__name__
