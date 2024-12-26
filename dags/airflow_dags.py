# Import necessary libraries and modules
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.lab import load_data, data_preprocessing, build_save_model, load_model_and_send_email

from airflow import configuration as conf

# Enable pickle support for XCom, allowing data to be passed between tasks
conf.set('core', 'enable_xcom_pickling', 'True')

# Define default arguments for your DAG
default_args = {
    'owner': 'stephy',
    'start_date': datetime(2024, 11, 29),
    'retries': 0,  # Number of retries in case of task failure
    'retry_delay': timedelta(minutes=5),  # Delay before retries
}

# Create a DAG instance named 'Airflow_Lab1' with the defined default arguments
dag = DAG(
    'SP500_Airflow_Pipeline',
    default_args=default_args,
    description='Dag example for SP500 stock prediction',
   # schedule_interval='0 9 * * *',  # Run every day at 9 AM
    schedule_interval=None,  # Set the schedule interval or use None for manual triggering
    catchup=False,
)

# Task to load data, calls the 'load_data' Python function
load_data_task = PythonOperator(
    task_id='load_data_task',
    python_callable=load_data,
    dag=dag,
)

def preprocess_data(**kwargs):
    """
    Pulls data from the previous task's XCom and preprocesses it.
    """
    # Pull data from the previous task's XCom
    data = kwargs['ti'].xcom_pull(task_ids='load_data_task')
    return data_preprocessing(data)

# Task to perform data preprocessing, depends on 'load_data_task'
data_preprocessing_task = PythonOperator(
    task_id='data_preprocessing_task',
    python_callable=preprocess_data,
    provide_context=True,
    dag=dag,
)

def build_and_save_model(**kwargs):
    """
    Pulls preprocessed data from XCom, trains a model, and saves it.
    """
    # Pull preprocessed data from XCom
    data = kwargs['ti'].xcom_pull(task_ids='data_preprocessing_task')
    X_train, X_test, y_train, y_test = data
    model_filename = "sp500_model.pkl"
    build_save_model((X_train, X_test, y_train, y_test), model_filename)
    return model_filename

# Task to build and save a model, depends on 'data_preprocessing_task'
build_save_model_task = PythonOperator(
    task_id='build_save_model_task',
    python_callable=build_and_save_model,
    provide_context=True,
    dag=dag,
)

def load_and_evaluate_model(**kwargs):
    model_filename = kwargs['ti'].xcom_pull(task_ids='build_save_model_task')
    data = kwargs['ti'].xcom_pull(task_ids='data_preprocessing_task')
    X_train, X_test, y_train, y_test = data
    load_model_and_send_email((X_train, X_test, y_train, y_test), model_filename, **kwargs)


# Task to load a model using the 'load_model_and_send_email' function
load_model_send_email_task = PythonOperator(
    task_id='load_model_send_email_task',
    python_callable=load_and_evaluate_model,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
load_data_task >> data_preprocessing_task >> build_save_model_task >> load_model_send_email_task

# If this script is run directly, allow command-line interaction with the DAG
if __name__ == "__main__":
    dag.cli()
