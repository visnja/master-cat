

build:
	docker build -f Dockerfile -t knowledge-base .
.PHONY: build


run:
	docker run --rm -p 7001:5000 --net infra knowledge-base
.PHONY: build



test:
	curl --header "Content-Type: application/json" \
  --request POST \
  -d '{"text":"Taiwan'\''s central bank said on Sunday it had banned Deutsche Bank from trading Taiwan dollar deliverable and non-deliverable forwards and suspended it for two years from trading forex derivatives as part of a crackdown on speculation."}' \
  http://localhost:7001/label