
build:
	docker build -t preprocess .
.PHONY: build

run:
	docker run --rm -d -e ENABLE_INIT_DAEMON=false --net infra --name preprocess preprocess 
.PHONY: run

logs:
	docker logs preprocess -f
.PHONY: logs

