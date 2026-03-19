from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default settings for all tasks in this DAG
default_args = {
    'owner': 'data_engineering',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# The actual DAG definition
with DAG(
    'fever_partner_reporting_elt',
    default_args=default_args,
    description='Transforms raw Postgres ticket sales into clean reporting tables',
    schedule_interval='@hourly',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['fever', 'dbt', 'batch'],
) as dag:

    # The absolute paths inside the Docker container (mapped via volumes)
    DBT_DIR = "/opt/airflow/tickets_dbt"
    
# 1. Test the raw API data FIRST (Data Quality check)
    dbt_test_sources = BashOperator(
        task_id='dbt_test_sources',
        bash_command=f"dbt test --select source:* --project-dir {DBT_DIR} --profiles-dir {DBT_DIR}"
    )

    # 2. Capture history (SCD Type 2)
    dbt_snapshot = BashOperator(
        task_id='dbt_snapshot',
        bash_command=f"dbt snapshot --project-dir {DBT_DIR} --profiles-dir {DBT_DIR}"
    )

    # 3. Build and Test models in one go (The --build flag is faster!)
    dbt_build = BashOperator(
        task_id='dbt_build_marts',
        bash_command=f"dbt build --exclude source:* --project-dir {DBT_DIR} --profiles-dir {DBT_DIR}"
    )

    # Faster Execution Graph
    dbt_test_sources >> dbt_snapshot >> dbt_build