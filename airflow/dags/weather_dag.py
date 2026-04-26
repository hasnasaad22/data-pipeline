from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import requests
import psycopg2
import logging

log = logging.getLogger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast?latitude=30.04&longitude=31.24&hourly=temperature_2m,relative_humidity_2m"

DB_CONFIG = {
    "host": "db",
    "database": "airflow_db",
    "user": "airflow",
    "password": "airflow",
    "port": 5432
}

# ------------------ Extract ------------------
def extract_weather():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    log.info("Extract success")
    return response.json()


# ------------------ Load ------------------
def load_weather(ti=None):
    data = ti.xcom_pull(task_ids="extract_weather")

    if not data:
        raise ValueError("No data from extract")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.weather_data (
            created_at TIMESTAMP,
            temperature FLOAT,
            humidity FLOAT
        );
    """)

    rows = list(zip(
        data["hourly"]["time"],
        data["hourly"]["temperature_2m"],
        data["hourly"]["relative_humidity_2m"]
    ))

    cur.executemany(
        "INSERT INTO raw.weather_data VALUES (%s, %s, %s)",
        rows
    )

    conn.commit()
    cur.close()
    conn.close()

    log.info(f"Inserted {len(rows)} rows")


# ------------------ DAG ------------------
with DAG(
    dag_id="weather_dbt_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    extract_task = PythonOperator(
        task_id="extract_weather",
        python_callable=extract_weather
    )

    load_task = PythonOperator(
        task_id="load_weather",
        python_callable=load_weather
    )

    dbt_task = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/weather_dbt && dbt run"
    )

    extract_task >> load_task >> dbt_task