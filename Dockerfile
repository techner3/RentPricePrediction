FROM apache/airflow:2.10.2-python3.12
# USER root
# RUN apt-get update && \
#     apt-get install -y git && \
#     apt-get install -y default-jre && \
#     apt-get clean
# USER airflow
ENV PYTHONPATH="/opt/airflow/dags:/opt/airflow/src:${PYTHONPATH}"

COPY requirements.txt .
COPY setup.py .
RUN pip install --no-cache-dir -r requirements.txt 
