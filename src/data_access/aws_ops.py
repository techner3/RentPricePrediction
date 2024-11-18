import os
import sys
import boto3
import pickle
from io import BytesIO
from src import logging
from dotenv import load_dotenv
from src.exception import CustomException

load_dotenv()

class AWSAccess:

    def __init__(self):

        self.region=os.getenv('region')
        self.s3_client=boto3.client('s3',
                  aws_access_key_id=os.getenv('aws_access_key_id'),
                  aws_secret_access_key=os.getenv('aws_secret_access_key'),region_name=self.region)
        self.bucket_name=os.getenv('bucket_name')

    def check_if_bucket_exists(self):

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise CustomException(e, sys)

    def create_s3_bucket(self):

        try:
            if not self.check_if_bucket_exists():
               self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
               logging.info('Bucket Created Successfully')
            else:
               logging.info('Bucket Already Exists')
        except Exception as e:
            raise CustomException(e, sys)
        
    def upload_model_to_s3(self,model):

        try:
            
            pickle_byte_obj = BytesIO()
            pickle.dump(model, pickle_byte_obj)
            pickle_byte_obj.seek(0)
            self.s3_client.upload_fileobj(pickle_byte_obj, self.bucket_name, 'models/bestmodel.pkl')
        except Exception as e:
            raise CustomException(e, sys)