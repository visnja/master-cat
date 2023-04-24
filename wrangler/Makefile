
build:
	docker build -t wrangler .
.PHONY: build

run:
	docker run --rm  -e ENABLE_INIT_DAEMON=false --net infra --name wrangler wrangler 
.PHONY: run

logs:
	docker logs wrangler
.PHONY: logs

