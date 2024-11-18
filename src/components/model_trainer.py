import os
import sys
import mlflow
import dagshub
import numpy as np
from src import logging
from sklearn.svm import SVR
from dotenv import load_dotenv
from xgboost import XGBRegressor
from src.exception import CustomException
from src.utils import load_numpy_array_data,read_yaml
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV
from src.entity import ModelTrainerConfig,RegressionMetrics
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

load_dotenv()
dagshub.init(repo_owner=os.getenv('repo_owner'), repo_name=os.getenv('repo_name'), mlflow=True)

class ModelTrainer:

    def __init__(self, model_trainer_config):
        self.modeltrainer_config = model_trainer_config
        self.params=read_yaml(self.modeltrainer_config.params_path)
        self.models={
            "LinearRegression": (LinearRegression(),self.params["linear_regression"]),
            "Ridge": (Ridge(), self.params["ridge"]),
            "Lasso": (Lasso(),self.params["lasso"] ),
            "DecisionTreeRegressor": (DecisionTreeRegressor(),self.params["decision_tree_regressor"]),
            "RandomForestRegressor": (RandomForestRegressor(),self.params["random_forest_regressor"]),
            "GradientBoostingRegressor": (GradientBoostingRegressor(),self.params["gradient_boosting_regressor"]),
            "SVR": (SVR(),self.params["svr"]),
            "KNeighborsRegressor": (KNeighborsRegressor(),self.params["k_neighbors_regressor"]),
            "XGboostRegressor":(XGBRegressor(objective='reg:squarederror'),self.params["xgb_regressor"])}
        
    def track_mlflow(self,metrics,model):

        try:
            with mlflow.start_run():
                mlflow.sklearn.log_model(model,'best_model')
                mlflow.log_metric('mse',metrics.mse)
                mlflow.log_metric('mae',metrics.mae)
                mlflow.log_metric('r2',metrics.r2)
        except Exception as e:
            raise CustomException(e, sys)
        
    def finding_best_model(self,X_train, Y_train):

        try:
            best_estimators={}
            for name, (model, params) in self.models.items():
                logging.info(f"Tuning hyperparameters for {name}...")
                grid_search = GridSearchCV(estimator=model, param_grid=params, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)
                grid_search.fit(X_train, Y_train)
                best_estimators[name] = {
                            'model': grid_search.best_estimator_,
                            'best_params': grid_search.best_params_,
                            'rmse': np.sqrt(-grid_search.best_score_),
                        }
                logging.info(f"Best parameters for {name}: {grid_search.best_params_}")
                logging.info(f"Best score for {name}: {np.sqrt(-grid_search.best_score_):.4f} (RMSE)")
            best_model_name = min(best_estimators.keys(), key=lambda x: best_estimators[x]['rmse'])
            return best_estimators[best_model_name]['model']
        except Exception as e:
            raise CustomException(e, sys)
        
    def evaluate_model(self, model, X_test, Y_test):
        try:
            logging.info("Evaluating model...")
            Y_pred = model.predict(X_test)
            mse = mean_squared_error(Y_test, Y_pred)
            mae = mean_absolute_error(Y_test, Y_pred)
            r2 = r2_score(Y_test, Y_pred)
            logging.info(f"Mean Squared Error (MSE): {mse:.4f}")
            logging.info(f"Mean Absolute Error (MAE): {mae:.4f}")
            logging.info(f"R-squared (R2): {r2:.4f}")
            return RegressionMetrics(mse, mae, r2)
        except Exception as e:
            raise CustomException(e, sys)
    
    def initiate_model_training(self):

        try:
            logging.info(">>>>>>>>> Model Training Stage Started")

            train_arr = load_numpy_array_data(self.modeltrainer_config.train_path)
            logging.info("Training Data loaded successfully")
            test_arr = load_numpy_array_data(self.modeltrainer_config.test_path)
            logging.info("Testing Data loaded successfully")

            X_train, Y_train, X_test, Y_test = (train_arr[:, :-1],train_arr[:, -1],test_arr[:, :-1],test_arr[:, -1])
            best_model = self.finding_best_model(X_train, Y_train)
            logging.info(f"Model trained successfully")
            metrics=self.evaluate_model(best_model,X_test, Y_test)
            
            self.track_mlflow(metrics,best_model)
            logging.info(f"Best Model and Metrics logged successfully") 

            logging.info("Model Training Stage Completed <<<<<<<<<")

        except Exception as e:
            raise CustomException(e, sys)
        
if __name__=="__main__":
    obj=ModelTrainer(ModelTrainerConfig())
    obj.initiate_model_training()
    