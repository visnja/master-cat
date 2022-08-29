from datetime import datetime, timedelta
from email.mime import image
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.docker_operator import DockerOperator
from docker.types import Mount

with DAG(
  'scrapper',
  default_args={

  },
  description='scrape index urls from the web',
  schedule_interval=timedelta(minutes=10),
  start_date=datetime(2021, 1, 1),
  catchup=False,
  tags=['example'],
) as dag:

    t1 = BashOperator(
            task_id='print_date',
            bash_command='pwd',
        )
    t2 = BashOperator(
            task_id='docker',
            depends_on_past=False,
            bash_command="docker ps ",
        )

    # t3 = DockerOperator(
    #         task_id='reuters',
    #         depends_on_past=False,
    #         image='crawler',
    #         command='configs/reuters.json',
    #         auto_remove=True,
    #         mount_tmp_dir=False,
    #         mounts=[Mount(source="/home/visnja/Desktop/faks/infra/dags/configs", target="/configs", type="bind")],
    #         network_mode="infra_default",
    # )
    # t4 = DockerOperator(
    #         task_id='cnbc',
    #         depends_on_past=False,
    #         image='crawler',
    #         command='configs/cnbc.json',
    #         auto_remove=True,
    #         mount_tmp_dir=False,
    #         mounts=[Mount(source="/home/visnja/Desktop/faks/infra/dags/configs", target="/configs", type="bind")],
    #         network_mode="infra_default",
    # )
    # t5 = DockerOperator(
    #         task_id='dailyfx',
    #         depends_on_past=False,
    #         image='crawler',
    #         command='configs/dailyfx.json',
    #         auto_remove=True,
    #         mount_tmp_dir=False,
    #         mounts=[Mount(source="/home/visnja/Desktop/faks/infra/dags/configs", target="/configs", type="bind")],
    #         network_mode="infra_default",
    # )
    # t6 = DockerOperator(
    #         task_id='marketwatch',
    #         depends_on_past=False,
    #         image='crawler',
    #         command='configs/marketwatch.json',
    #         auto_remove=True,
    #         mount_tmp_dir=False,
    #         mounts=[Mount(source="/home/visnja/Desktop/faks/infra/dags/configs", target="/configs", type="bind")],
    #         network_mode="infra_default",

    # )

    # t7 = DockerOperator(
    #         task_id='marketpulse',
    #         depends_on_past=False,
    #         image='crawler',
    #         command='configs/marketpulse.json',
    #         auto_remove=True,
    #         mount_tmp_dir=False,
    #         mounts=[Mount(source="/home/visnja/Desktop/faks/infra/dags/configs", target="/configs", type="bind")],
    #         network_mode="infra_default",
    # )
    # t8 = DockerOperator(
    #         task_id='investing',
    #         depends_on_past=False,
    #         image='crawler',
    #         command='configs/investing.json',
    #         auto_remove=True,
    #         mount_tmp_dir=False,
    #         mounts=[Mount(source="/home/visnja/Desktop/faks/infra/dags/configs", target="/configs", type="bind")],
    #         network_mode="infra_default",
    # )
    t1 >> t2 