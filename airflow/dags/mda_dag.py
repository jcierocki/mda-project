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
    bash_command="01_environment_setup.sh",
    dag=dag,
    cwd=dag.folder
)

activate_env = BashOperator(
    task_id = 'activate_environment',
    bash_command="mda_project_activate",
    dag=dag,
    cwd=dag.folder
)

pull_cdc = BashOperator(
    task_id = 'pull_cdc_data',
    bash_command="python scripts/02A_cdc_script.py",
    dag=dag,
    cwd=dag.folder,
)

pull_nyt = BashOperator(
    task_id = 'pull_nyt_data',
    bash_command='python scripts/02B_nyt_script.py',
    dag=dag,
    cwd=dag.folder
)

pull_variants = BashOperator(
    task_id = 'pull_variants',
    bash_command='python scripts/02C_covid_variants.py',
    dag=dag,
    cwd=dag.folder
)


clean_cdc = BashOperator(
    task_id = 'process_cdc',
    bash_command='python scripts/03A_process_cdc.py',
    dag=dag,
    cwd=dag.folder
)

clean_non_epidemic = BashOperator(
    task_id = 'process_non_epidemic',
    bash_command='python scripts/03B_process_non_epidemic.py',
    dag=dag,
    cwd=dag.folder
)

data_complete= BashOperator(
    task_id = 'data_complete',
    bash_command='echo Data Collection and Processing Complete',
    dag=dag,
    cwd=dag.folder
)

run_time_series_model = BashOperator(
    task_id = 'run_time_series_model',
    bash_command='python scripts/04A_time_series_model.py',
    dag=dag,
    cwd=dag.folder
)

run_random_effects_model= BashOperator(
    task_id = 'run_random_effects_model',
    bash_command='python scripts/04B_random_effects_model.py',
    dag=dag,
    cwd=dag.folder
)

run_counterfactuals_model= BashOperator(
    task_id = 'run_counterfactuals_model',
    bash_command='python scripts/04C_counterfactuals_model.py',
    dag=dag,
    cwd=dag.folder
)

upload_model_results= BashOperator(
    task_id = 'upload_data_to_mongodb',
    bash_command='python scripts/05_upload_to_mongo.py',
    dag=dag,
    cwd=dag.folder
)

build_app= BashOperator(
    task_id = 'build_app',
    bash_command='echo goodbye',
    dag=dag,
    cwd=dag.folder
)

build_env >> activate_env
activate_env >> pull_cdc
activate_env >> pull_nyt 
activate_env >> pull_variants
activate_env >> clean_non_epidemic
pull_nyt >> clean_cdc
pull_cdc >> clean_cdc
clean_non_epidemic >> clean_cdc
clean_cdc >> data_complete
pull_variants >> data_complete
data_complete >> run_time_series_model
data_complete >> run_random_effects_model
data_complete >> run_counterfactuals_model
run_time_series_model >> upload_model_results
run_random_effects_model >> upload_model_results
run_counterfactuals_model >> upload_model_results
upload_model_results >> build_app