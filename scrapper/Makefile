build:
	docker build -t crawler .
.PHONY: build

run:
	docker run -v '${PWD}/configs':/configs --net infra --rm crawler
.PHONY: run 