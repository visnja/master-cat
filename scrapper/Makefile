build:
	docker build -t crawler .
.PHONY: build

run:
	docker run -v '${PWD}/configs':/configs --net infra --rm crawler
.PHONY: run 

clean_containers:
	docker ps -f 'ancestor=crawler' -aq | xargs docker stop
.PHONY: clean_containers