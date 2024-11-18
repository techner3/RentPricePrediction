import os
import sys
import json
import mlflow
import dagshub
from src import logging
from dotenv import load_dotenv
from src.exception import CustomException
from src.utils import load_numpy_array_data
from src.entity import ModelEvaluationConfig
from sklearn.metrics import mean_squared_error

load_dotenv()
dagshub.init(repo_owner=os.getenv('repo_owner'), repo_name=os.getenv('repo_name'), mlflow=True)

class ModelEvaluation:

    def __init__(self, model_evaluation_config):

        self.modelevaluation_config = model_evaluation_config
        self.mlflow_client=mlflow.tracking.MlflowClient()

    def get_latest_run_details(self):

        try:
            latest_run=json.loads(mlflow.search_runs(order_by=["start_time DESC"],max_results=1).to_json())
            latest_run_details=json.loads(latest_run['tags.mlflow.log-model.history']['0'])[0]
            return  latest_run_details['run_id'],latest_run_details['artifact_path']
        except Exception as e:
            raise CustomException(e, sys)
        
    def get_latest_run_metric(self):
        try:
            latest_run=json.loads(mlflow.search_runs(order_by=["start_time DESC"],max_results=1).to_json())
            return  latest_run['metrics.mse']['0']
        except Exception as e:
            raise CustomException(e, sys)
    
    def get_latest_registered_model(self):

        try:
            if len(self.mlflow_client.search_registered_models(filter_string=f"name ='best_model'"))!=0:
                latest_version=self.mlflow_client.get_latest_versions('best_model')[0]
                return mlflow.sklearn.load_model(f"models:/best_model/{latest_version.version}")
            else:
                return None
        except Exception as e:
            raise CustomException(e, sys)
        
    def register_model(self,model,run_id,artifact_path):

        try:
            new_version = self.mlflow_client.create_model_version(
                name="best_model",
                source=f"runs:/{run_id}/{artifact_path}",
                run_id=run_id
                )
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_evaluation(self):
        try:
            logging.info(">>>>>>>>> Model Evaluation Stage Started")
            
            test_arr = load_numpy_array_data(self.modelevaluation_config.test_path)
            X_test, Y_test=(test_arr[:, :-1],test_arr[:, -1])
            logging.info("Testing Data loaded successfully")

            run_id,artifact_path=self.get_latest_run_details()
            logging.info("Latest Run Model loaded successfully")

            latest_model=mlflow.sklearn.load_model(f"runs:/{run_id}/{artifact_path}")

            latest_model_metric=round(self.get_latest_run_metric(),3)
            logging.info("Latest Run Model's Metric retrieved successfully")

            assert latest_model_metric<self.modelevaluation_config.threshold, "Threshold Value better than the metric"
            logging.info("Threshold Value verified successfully")

            registered_model=self.get_latest_registered_model()

            if registered_model!=None:
                predicted=registered_model.predict(X_test)
                mse=round(mean_squared_error(predicted,Y_test),3)
                logging.info(f"MSE Calculated:{mse}")
                logging.info(f"Latest MSE Calculated:{latest_model_metric}")
                if latest_model_metric<mse:
                    logging.info("Registered Model's performance worse than the latest run model's performance")
                    self.register_model(latest_model,run_id,artifact_path)
                    status=True
                else:
                    logging.info("Registered Model's performance better than or equal to the latest run model's performance")
                    status=False
            else:
                self.mlflow_client.create_registered_model("best_model")
                self.register_model(latest_model,run_id,artifact_path)
                status=True
                
            logging.info(f"Model Evaluation Status : {status}")
            logging.info("Model Evaluation Stage Completed <<<<<<<<<")
            return status

        except Exception as e:
            raise CustomException(e, sys)
        

if __name__=="__main__":

    obj=ModelEvaluation(ModelEvaluationConfig())
    obj.initiate_model_evaluation()