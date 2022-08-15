

build:
	docker build -f Dockerfile.spark -t preprocess .


run:
	docker run --rm -e ENABLE_INIT_DAEMON=false --net infra preprocess

