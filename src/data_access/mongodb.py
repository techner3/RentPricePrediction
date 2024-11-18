import os
import sys
import pandas as pd
from src import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from src.exception import CustomException

load_dotenv()

class MongodbAccess:

    def __init__(self):

        self.connectionstring=os.getenv("connection_string")

        try:
            self.client = MongoClient(self.connectionstring)
        except Exception as e:
            raise CustomException(e,sys)

        logging.info(f"Connected with MongoDB Client Successfully")
        self.database = self.client[os.getenv("database_name")]
        self.collection = self.database[os.getenv("collection_name")]

    def delete_collections(self,collection_name='training_data'):

        try:
            if collection_name in self.database.list_collection_names():
                logging.info("Collection exists in database")
                self.database[collection_name].drop()
                logging.info("Collections Dropped Successfully")
            else:
                logging.info("Collection Not Found")
        except Exception as e:
            raise CustomException(e,sys)

    def write_data(self, data,collection_name='training_data'):
        
        try:
            self.database[collection_name].insert_many(data.to_dict('records'))
            logging.info(f"Data Written to MongoDB Successfully")
        except Exception as e:
            raise CustomException(e,sys)

    def extract_data(self):

        try:

            df=pd.DataFrame(list(self.collection.find()))
            logging.info("Data Retrival Completed")
            logging.info(f"Number of Retrieved Rows: {len(df)}")
            df.drop('_id',axis=1,inplace=True)
            return df

        except Exception as e:
            raise CustomException(e,sys) 

    def close_mongdb_connection(self):

        try:
            self.client.close()
            logging.info("MongoDB Client Closed Successfully")
        except Exception as e:
            raise CustomException(e,sys) 