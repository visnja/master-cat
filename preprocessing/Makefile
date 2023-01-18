
build:
	docker build -f Dockerfile.spark -t preprocess .
.PHONY: build

run:
	docker run --rm -d -e ENABLE_INIT_DAEMON=false --net infra preprocess 
.PHONY: run

logs:
	docker logs preprocess
.PHONY: logs

