import os
import psycopg2
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

datetime.now()

load_dotenv()


def extract_data_from_mongodb():

    try:
        keys=["Rent", "Parking","Direction facing","Property on","Brokerage terms","Bachelors Allowed",
                "Security Deposit","Pet Allowed","Non Vegetarian","Super Built-Up Area","Carpet Area","Bedrooms",
                "Bathrooms","City","State","Flooring type","Furnishing State","Servant Accomation",
                "Year of Construction"]
        mongodb_client=MongoClient(os.getenv("connection_string"))
        logging.info("Connected to MongoDB successfully")
        reference_df=pd.DataFrame(list(mongodb_client['real_estate']['training_data'].find()))
        current_df=pd.DataFrame(list(mongodb_client['real_estate']['commonfloor'].find()))
        logging.info('Retrieved Data')
        logging.info("Data Extraction Completed")
        return reference_df[keys], current_df[keys]
        
    except Exception as e:
        raise Exception(e)
    
    finally:
        mongodb_client.close()
        logging.info("Closed MongoDB successfully")
    
def push_data_to_postgresql(metrics):

    try:
        postgresql_client=psycopg2.connect(
                host=os.getenv('host'),
                database=os.getenv('database'),
                user=os.getenv('user'),
                password=os.getenv('password')
            )
        cur = postgresql_client.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS metrics_data (
                drift_share FLOAT,
                number_of_columns INT,
                number_of_drifted_columns INT,
                share_of_drifted_columns FLOAT,
                dataset_drift BOOLEAN,
                timestamp TIMESTAMP
            )
        """)

        sql = "INSERT INTO metrics_data (drift_share, number_of_columns, number_of_drifted_columns, share_of_drifted_columns, dataset_drift,timestamp) VALUES (%s,%s, %s, %s, %s, %s)"
        cur.executemany(sql, metrics)
        logging.info("Data Pushing to PostgreSQL Completed")

    except Exception as e:
        raise Exception(e)
    
    finally:
        postgresql_client.commit()
        postgresql_client.close()
    
def metrics_calculation(reference_df, current_df):

    try:
        data_drift_report = Report(metrics=[DataDriftPreset()])
        data_drift_report.run(reference_data=reference_df, current_data=current_df)
        data_drift_results = data_drift_report.as_dict()
        data_drift_results=data_drift_results["metrics"][0]['result']
        data_drift_results['timestamp']=datetime.now()
        logging.info("Metrics Calculation Completed")
        return [tuple(data_drift_results.values())]
    
    except Exception as e:
        raise Exception(e)