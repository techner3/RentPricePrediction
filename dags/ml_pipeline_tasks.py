def data_ingestion():

    from src.components import DataIngestion
    from src.entity import DataIngestionConfig
    
    obj=DataIngestion(DataIngestionConfig())
    obj.initiate_data_ingestion()

def data_validation():

    from src.components import DataValidation
    from src.entity import DataValidationConfig

    obj=DataValidation(DataValidationConfig())
    return obj.initiate_data_validation()

def data_transformation():

    from src.components import DataTransformation
    from src.entity import DataTransformationConfig

    obj=DataTransformation(DataTransformationConfig())
    obj.initiate_data_transformation()

def model_training():

    from src.components import ModelTrainer
    from src.entity import ModelTrainerConfig

    obj=ModelTrainer(ModelTrainerConfig())
    obj.initiate_model_training()

def model_evaluation():

    from src.components import ModelEvaluation
    from src.entity import ModelEvaluationConfig

    obj=ModelEvaluation(ModelEvaluationConfig())
    return obj.initiate_model_evaluation()

def model_pusher():

    from src.components import ModelPusher
    from src.entity import ModelPusherConfig

    obj=ModelPusher(ModelPusherConfig())
    obj.initiate_model_pusher()