build:
	docker build -t condaenv .
.PHONY: build

run:
	docker run  -e MLFLOW_TRACKING_URI=http://tracking-server:5000 -v $$PWD:/app --net infra --entrypoint=./entrypoint.sh condaenv -c python train.py
.PHONY: run

serve:
	export MLFLOW_TRACKING_URI=http://tracking-server:5000
	MLFLOW_S3_ENDPOINT_URL=http://localhost:9900 AWS_ACCESS_KEY_ID="user" AWS_SECRET_ACCESS_KEY="password" mlflow models build-docker  -m "s3://bucket/experiments/0/5da0a39508d649428659ec6797d4daa0/artifacts/model" --env-manager conda -n "serve_model"

.PHONY: serve

conda_export:
	conda env export > environment.yaml
.PHONY: conda_export
