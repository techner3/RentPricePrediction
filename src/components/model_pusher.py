import os
import sys
import mlflow
import dagshub
from src import logging
from dotenv import load_dotenv
from src.ml_model import RentModel
from src.data_access import AWSAccess
from src.entity import ModelPusherConfig
from src.exception import CustomException
from src.utils import load_object, save_object


load_dotenv()
dagshub.init(repo_owner=os.getenv('repo_owner'), repo_name=os.getenv('repo_name'), mlflow=True)

class ModelPusher:

    def __init__(self,model_pusher_config):

        self.modelpusher_config = model_pusher_config
        self.mlflow_client=mlflow.tracking.MlflowClient()
        self.aws_access=AWSAccess()

    def get_latest_model(self):

        try:
            return mlflow.sklearn.load_model(self.mlflow_client.get_latest_versions('best_model')[0].source)
        except Exception as e:
            raise CustomException(e, sys)
        
    def save_local(self,model):

        try:
            os.makedirs(os.path.dirname(self.modelpusher_config.model_dir),exist_ok=True)
            save_object(model,self.modelpusher_config.model_dir)
            logging.info("Model Saved Locally")
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_pusher(self):
        
        try:
            logging.info(">>>>>>>>> Model Pusher Stage Started")
            
            model=self.get_latest_model()
            logging.info("Latest Model Retrieved")

            target_transformer=load_object(self.modelpusher_config.target_transformer_path)
            feature_transformer=load_object(self.modelpusher_config.feature_transformer_path)
            logging.info("Target and Feature Transformer Retrieved")

            final_model=RentModel(feature_transformer,model,target_transformer)
            logging.info("Final Model Created")

            self.save_local(final_model)

            self.aws_access.create_s3_bucket()
            self.aws_access.upload_model_to_s3(final_model)

            logging.info("Model Pusher Stage Completed <<<<<<<<<")

        except Exception as e:
            raise CustomException(e, sys)
        
if __name__=="__main__":

    obj=ModelPusher(ModelPusherConfig())
    obj.initiate_model_pusher()

