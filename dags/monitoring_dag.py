import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def data_extraction(**context):

    from monitoring_tasks import extract_data_from_mongodb
    
    reference_df, current_df=extract_data_from_mongodb()
    reference_file="reference.csv"
    current_file="current.csv"
    reference_df.to_csv(reference_file, index=False)
    current_df.to_csv(current_file, index=False)
    context['ti'].xcom_push(key='reference', value=reference_file)
    context['ti'].xcom_push(key='current', value=current_file)
    

def metrics_calculation(**context):
    from monitoring_tasks import metrics_calculation
    reference_file=context['ti'].xcom_pull(key='reference')
    current_file=context['ti'].xcom_pull(key='current')
    reference_df = pd.read_csv(reference_file)
    current_df = pd.read_csv(current_file)
    metrics=metrics_calculation(reference_df, current_df)
    context['ti'].xcom_push(key='metrics', value=metrics)

def push_data_to_postgres(**context):
    from monitoring_tasks import push_data_to_postgresql
    data=context['ti'].xcom_pull(key='metrics')
    push_data_to_postgresql(data)


with DAG('monitoring_dag', start_date=datetime(2023, 1, 1), schedule_interval=None) as dag:

    data_extraction_task = PythonOperator(
        task_id='data_extraction',
        python_callable=data_extraction,
        do_xcom_push=True
    )

    metrics_calculation_task = PythonOperator(
        task_id='metrics_calculation',
        python_callable=metrics_calculation,
        provide_context=True,
        do_xcom_push=True
    )

    data_insertion_task = PythonOperator(
        task_id='data_insertion',
        python_callable=push_data_to_postgres,
        provide_context=True,
    )

    data_extraction_task >> metrics_calculation_task >> data_insertion_task