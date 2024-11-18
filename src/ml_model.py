class RentModel:

    def __init__(self, feature_transformer, model, inverse_transformer):
        self.feature_transformer = feature_transformer
        self.model = model
        self.inverse_transformer = inverse_transformer
        
    def predict(self, X):

        X_transformed = self.feature_transformer.transform(X)
        y_pred = self.model.predict(X_transformed)
        y_inverse = self.inverse_transformer.inverse_transform([y_pred])
        return y_inverse.flatten()