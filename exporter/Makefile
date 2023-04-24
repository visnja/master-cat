
build:
	docker build -t exporter .
.PHONY: build

run:
	docker run --rm  -e ENABLE_INIT_DAEMON=false --net infra exporter 
.PHONY: run

logs:
	docker logs exporter
.PHONY: logs

