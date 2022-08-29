build:
	docker build -t condaenv .

run:
	docker run  -e MLFLOW_TRACKING_URI=http://tracking-server:5000 -v $$PWD:/app --net infra --entrypoint=./entrypoint.sh condaenv -c python train.py