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
            bash_command="docker stop reuters cnbc dailyfx marketwatch marketpulse investing fxstreet forexcrunch fxempire forex || true",
        )

    t3 = DockerOperator(
            task_id='reuters',
            depends_on_past=False,
            image='crawler',
            container_name='reuters',
            command='configs/reuters.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t4 = DockerOperator(
            task_id='cnbc',
            depends_on_past=False,
            image='crawler',
            container_name='cnbc',
            command='configs/cnbc.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t5 = DockerOperator(
            task_id='dailyfx',
            depends_on_past=False,
            image='crawler',
            container_name='dailyfx',
            command='configs/dailyfx.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t6 = DockerOperator(
            task_id='marketwatch',
            depends_on_past=False,
            image='crawler',
            container_name='marketwatch',
            command='configs/marketwatch.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",

    )

    t7 = DockerOperator(
            task_id='marketpulse',
            depends_on_past=False,
            image='crawler',
            container_name='marketpulse',
            command='configs/marketpulse.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t8 = DockerOperator(
            task_id='investing',
            depends_on_past=False,
            image='crawler',
            container_name='investing',
            command='configs/investing.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t9 = DockerOperator(
            task_id='fxstreet',
            depends_on_past=False,
            image='crawler',
            container_name='fxstreet',
            command='configs/fxstreet.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t10 = DockerOperator(
            task_id='forexcrunch',
            depends_on_past=False,
            image='crawler',
            container_name='forexcrunch',
            command='configs/forexcrunch.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t11 = DockerOperator(
            task_id='fxempire',
            depends_on_past=False,
            image='crawler',
            container_name='fxempire',
            command='configs/fxempire.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t12 = DockerOperator(
            task_id='forex',
            depends_on_past=False,
            image='crawler',
            container_name='forex',
            command='configs/forex.json',
            auto_remove=True,
            mount_tmp_dir=False,
            mounts=[Mount(source="/home/visnja/Desktop/faks/master-cat/infra/airflow/dags/configs", target="/configs", type="bind")],
            network_mode="infra",
    )
    t1 >> t2 >> [t3, t4, t5, t6, t7, t8, t9, t10, t11, t12 ] 