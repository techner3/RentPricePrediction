import os
import re
import ast
import sys
import numpy as np
from typing import List
from src import logging
from src.exception import CustomException
from src.entity import DataValidationConfig
from src.utils import load_csv, read_yaml,save_csv
from pandas.api.types import is_float_dtype, is_integer_dtype, is_string_dtype

class DataValidation:

    def __init__(self,data_validation_config):

        self.datavalidation_config = data_validation_config
        self.schema=read_yaml(self.datavalidation_config.yaml_file_path)
        self.columns=self.schema['target'] | self.schema['features']

    def property_preprocessing(self,x):
        if bool(re.search(r'\d', x)):
            return str(re.search(r'\d', x).group())
        elif "Ground" in x:
            return '0'
        else:
            return x

    def data_cleaning(self,data):

        try:
            data['Amenities']=data['Amenities'].apply(ast.literal_eval)
            data.drop(["ID","Address","Listed by","Listed On","Available from"],axis=1,inplace=True)
            data['Amenities'] = data['Amenities'].apply(lambda x: "No" if len(x)==0 else "Yes")
            data['Property on'] = data['Property on'].apply(lambda x:self.property_preprocessing(x))
            data['Brokerage terms'] = data['Brokerage terms'].apply(lambda x: "Yes" if bool(re.search(r'\d', x)) else x)
            return data
        except Exception as e:
            raise CustomException(e,sys)
    
    def validate_columns(self, data):

        try:
            data_columns=list(data.columns)
            assert len(self.columns.keys())==len(data_columns), "Number of Columns doesn't match"
            logging.info("Columns count validation completed")

            for column, properties in self.columns.items():
                expected_type = properties['type']
                if expected_type == 'float':
                    assert is_float_dtype(data[column]), f"{column} should be float"
                elif expected_type == 'integer':
                    assert is_integer_dtype(data[column]), f"{column} should be integer"
                elif expected_type == 'string':
                    assert is_string_dtype(data[column]), f"{column} should be string"

            return True
        
        except AssertionError:
            return False

        except Exception as e:
            raise CustomException(e,sys)
        
    def initiate_data_validation(self):

        try:
            logging.info(">>>>>>>>> Data Validation Stage Started")
            
            df=load_csv(self.datavalidation_config.ingested_path)
            logging.info("Ingested Data loaded successfully")

            status=self.validate_columns(df)
            logging.info("Data Column validation completed")

            if status:
                df=self.data_cleaning(df)
                logging.info("Data Cleaning completed")

                save_csv(df,self.datavalidation_config.validated_path)
                logging.info(f"File saved at {self.datavalidation_config.validated_path}")

            logging.info(f"Data Validated Status: {status}")
            logging.info(" Data Validation Completed <<<<<<<<<")
            return status

        except Exception as e:
            raise CustomException(e,sys)

if __name__ == "__main__":

    obj=DataValidation(DataValidationConfig())
    obj.initiate_data_validation()