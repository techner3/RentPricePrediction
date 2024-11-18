import os
import sys
from src import logging
from src.exception import CustomException
from src.entity import DataIngestionConfig
from src.data_access import MongodbAccess


class DataIngestion:

    def __init__(self,data_ingestion_config):
        self.mongodb=MongodbAccess()
        self.dataingestion_config=data_ingestion_config

    def initiate_data_ingestion(self):

        try:
            logging.info(">>>>>>>>> Data Ingestion Stage Started")

            df=self.mongodb.extract_data()
            
            os.makedirs(os.path.dirname(self.dataingestion_config.ingestion_path),exist_ok=True)
            logging.info(f"Ingestion folder created successfully")

            df.to_csv(self.dataingestion_config.ingestion_path,index=False)
            logging.info(f"File saved at {self.dataingestion_config.ingestion_path}")
            
            self.mongodb.delete_collections()
            self.mongodb.write_data(df)
            self.mongodb.close_mongdb_connection()

            logging.info("Data Ingestion Stage Completed <<<<<<<<<")
            
        except Exception as e:
            raise CustomException(e,sys)

if __name__=="__main__":
    obj=DataIngestion(DataIngestionConfig())
    obj.initiate_data_ingestion()

