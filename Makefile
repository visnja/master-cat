services:
	docker-compose up -d
.PHONY: services

stop-services:
	docker-compose down
.PHONY: stop-services

infra:
	cd infra && docker-compose up -d
	sleep 5
	cd infra && sh helper.sh
.PHONY: infra

stop-infra:
	cd infra && docker-compose down
.PHONY: stop-infra

hive:
	cd infra && docker-compose -f hive.yml up -d
.PHONY: hive


stop-hive:
	cd infra && docker-compose -f hive.yml down
.PHONY: stop-hive

status:
	docker ps
.PHONY: status

airflow:
	cd infra/airflow && docker-compose up -d
.PHONY: airflow

stop-airflow:
	cd infra/airflow && docker-compose down
.PHONY: stop-airflow

mlflow:
	cd infra/minio && docker-compose up -d
.PHONY: mlflow

stop-mlflow:
	cd infra/minio && docker-compose down
.PHONY: stop-mlflow

import:
	cd importer && make run
.PHONY: import

crawl-local:
	cd scrapper && sh start.sh
.PHONY: crawl-local

metabase:
	cd metabase && UID=$$UID GID=$$GID docker-compose up -d
.PHONY: metabase

stop-metabase:
	cd metabase && UID=$$UID GID=$$GID docker-compose down
.PHONY: stop-metabase

preprocess:
	cd preprocessing && make run
.PHONY: preprocess

preprocess-logs:
	cd preprocessing && make logs
.PHONY: preprocess-logs

urls:
	@echo 'metabase http://localhost:3000'
	@echo 'hive http://localhost:8888'
	@echo 'spark-master http://localhost:8080'
	@echo 'airflow http://localhost:8085'
	@echo 'mlflow http://localhost:5000'
	@echo 'hadoop http://localhost:9870'
.PHONY: urls
