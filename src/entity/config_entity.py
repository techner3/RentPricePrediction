import os 
from src.constants import *
from datetime import datetime
from dataclasses import dataclass

TIMESTAMP=datetime.now().strftime("%m_%d_%Y")

@dataclass(frozen=True)
class DataIngestionConfig:
    ingestion_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,INGESTION_PATH,INGESTION_FILE_NAME)

@dataclass(frozen=True)
class DataValidationConfig:
    yaml_file_path:str=YAML_PATH
    ingested_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,INGESTION_PATH,INGESTION_FILE_NAME)
    validated_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,VALIDATION_PATH,VALIDATED_FILE_NAME)

@dataclass(frozen=True)
class DataTransformationConfig:
    validated_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,VALIDATION_PATH,VALIDATED_FILE_NAME)
    train_test_split_ratio:float=TRAIN_TEST_SPLIT_RATIO
    yaml_file_path:str=YAML_PATH
    train_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,TRAIN_PATH)
    test_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,TEST_PATH)
    target_transformer_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,TARGET_PATH)
    feature_transformer_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,FEATURE_PATH)

@dataclass(frozen=True)
class ModelTrainerConfig:
    train_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,TRAIN_PATH)
    test_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,TEST_PATH)
    params_path:str=PARAMS_YAML_PATH

@dataclass()
class RegressionMetrics:
    mse:float 
    mae:float
    r2:float


@dataclass(frozen=True)
class ModelEvaluationConfig:
    test_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,TEST_PATH)
    threshold:float=THRESHOLD_VALUE

@dataclass(frozen=True)
class ModelPusherConfig:
    target_transformer_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,TARGET_PATH)
    feature_transformer_path:str=os.path.join(ARTIFACTS_DIR,TIMESTAMP,TRANSFORMATION_PATH,FEATURE_PATH)
    model_dir:str=MODEL_NAME


