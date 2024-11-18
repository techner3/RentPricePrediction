import os
import sys
import yaml
import dill
import numpy as np
import pandas as pd
from src.exception import CustomException


def read_yaml(filepath:str):

    try:
        with open(filepath,"rb") as file:
            return yaml.safe_load(file)

    except Exception as e:
        raise CustomException(e, sys) 
    
def load_csv(file_path):

    try:
        return pd.read_csv(file_path)

    except Exception as e:
            raise CustomException(e, sys) 
    
def save_csv(data,file_path):

    try:
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        data.to_csv(file_path,index=False)

    except Exception as e:
        raise CustomException(e, sys) 
    
def load_numpy_array_data(file_path):

    try:
         with open(file_path, "rb") as file_obj:
            return np.load(file_obj)

    except Exception as e:
        raise CustomException(e, sys) from e

def save_numpy_array_data(array: np.array,file_path):

    try:
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)

    except Exception as e:
        raise CustomException(e, sys) from e
    
def load_object(file_path):

    try:
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)

    except Exception as e:
        raise CustomException(e, sys)

def save_object(obj,file_path):

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)

    except Exception as e:
        raise CustomException(e, sys)