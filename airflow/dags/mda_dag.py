from datetime import timedelta
from airflow import DAG 
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner' : 'jobs',
    'depends_on_past' : False,
    'start_date': days_ago(2),
    'email' : 'achilleasghinis@gmail.com',
    'email_on_failure': False,
    'email_on_retry' : False
}

dag = DAG(
    'mda_pipeline',
    default_args=default_args,
    description = 'simple example',
    schedule_interval=timedelta(days=1)
)

build_env = BashOperator(
    task_id = 'build_environment',
    bash_command="pwd",
    dag=dag,
    cwd=dag.folder
)

pull_cdc = BashOperator(
    task_id = 'pull_cdc_data',
    bash_command="python scripts/cdc_script.py",
    dag=dag,
    cwd=dag.folder,
)

pull_nyt = BashOperator(
    task_id = 'pull_nyt_data',
    bash_command='python scripts/nyt_script.py',
    dag=dag,
    cwd=dag.folder
)

clean_data = BashOperator(
    task_id = 'process_all_data',
    bash_command='python scripts/clean_data.py',
    dag=dag,
    cwd=dag.folder
)

upload_data= BashOperator(
    task_id = 'upload_data',
    bash_command='python scripts/load_data.py',
    dag=dag,
    cwd=dag.folder
)

run_ts_model= BashOperator(
    task_id = 'run_ts_model',
    bash_command='python scripts/ts_model.py',
    dag=dag,
    cwd=dag.folder
)

run_tristan_model= BashOperator(
    task_id = 'run_tristan_model',
    bash_command='python scripts/renf_model.py',
    dag=dag,
    cwd=dag.folder
)

run_achilles_model= BashOperator(
    task_id = 'run_achilles_model',
    bash_command='python scripts/counterfactuals_model.py',
    dag=dag,
    cwd=dag.folder
)

upload_model_results= BashOperator(
    task_id = 'upload_model_results',
    bash_command='echo goodbye',
    dag=dag,
    cwd=dag.folder
)

build_app= BashOperator(
    task_id = 'build_app',
    bash_command='echo goodbye',
    dag=dag,
    cwd=dag.folder
)


build_env >> pull_cdc
build_env >> pull_nyt 
pull_nyt >> clean_data
pull_cdc >> clean_data
clean_data >> upload_data
upload_data >> run_ts_model
upload_data >> run_tristan_model
upload_data >> run_achilles_model
run_ts_model >> upload_model_results
run_tristan_model >> upload_model_results
run_achilles_model >> upload_model_results
upload_model_results >> build_app