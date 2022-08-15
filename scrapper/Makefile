build:
	docker build -t crawler .
.PHONY: build

run:
	docker run -v '${PWD}/configs':/configs --net infra_default --rm crawler
.PHONY: run 