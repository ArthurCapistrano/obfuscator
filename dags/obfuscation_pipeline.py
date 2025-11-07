from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PYTHON_PATH = "/opt/airflow/src"

SETUP_SCRIPT_PATH = "/opt/airflow/src/database/setup.py"
OBFUSCATE_SCRIPT_PATH = "/opt/airflow/src/obfuscator/obfuscate.py"

with DAG(
    dag_id='data_obfuscation_pipeline',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  
    catchup=False,
    tags=['etl', 'obfuscation', 'simple']
) as dag:

    # Tarefa 1: Executa o script setup.py
    task_1_load_raw_data = BashOperator(
        task_id='load_raw_data_to_mysql',
        bash_command=f"export PYTHONPATH={PYTHON_PATH} && python {SETUP_SCRIPT_PATH}"
    )

    # Tarefa 2: Executa o script obfuscate.py
    task_2_obfuscate_data = BashOperator(
        task_id='obfuscate_and_load_data',
        bash_command=f"export PYTHONPATH={PYTHON_PATH} && python {OBFUSCATE_SCRIPT_PATH}"
    )

    # Define a ordem de execução
    task_1_load_raw_data >> task_2_obfuscate_data