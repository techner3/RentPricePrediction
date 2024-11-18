from datetime import datetime
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from ml_pipeline_tasks import (data_ingestion,
                               data_validation,
                               data_transformation,
                               model_training,
                               model_evaluation,
                               model_pusher)

@dag(
    'dag_ml_pipeline_tasks',
    start_date=datetime(2024, 11, 4),
    schedule_interval='@daily',
    catchup=False
)
def generate_dag():
    
    @task(task_id='data_ingestion')
    def data_ingestion_task():
        data_ingestion()

    @task(task_id='data_validation')
    def data_validation_task():
        if not data_validation():
            raise AirflowException("Data validation Failed")
    
    @task(task_id='data_transformation')
    def data_transformation_task():
        data_transformation()

    @task(task_id='model_training')
    def model_training_task():
        model_training()

    @task(task_id='model_evaluation')
    def model_evaluation_task():
        if not model_evaluation():
            raise AirflowException("Model evaluation Failed")

    @task(task_id='model_pusher')
    def model_pusher_task():
        model_pusher()
    
    # Define the task dependencies
    task_data_ingestion=data_ingestion_task()
    task_data_validation=data_validation_task()
    task_data_transformation=data_transformation_task()
    task_model_training=model_training_task()
    task_model_evaluation=model_evaluation_task()
    task_model_pusher=model_pusher_task()

    task_data_ingestion >> task_data_validation >> task_data_transformation >> task_model_training >> task_model_evaluation >> task_model_pusher
 
dag_instance = generate_dag()