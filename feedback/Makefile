

build:
	docker build -f Dockerfile -t feedback .
.PHONY: build


run:
	docker run --rm -p 6000:5000 --net infra feedback
.PHONY: run

test:
	curl --header "Content-Type: application/json" \
  --request POST \
  -d '{"url":"", "labels":["TWD"],"text":"Taiwan'\''s central bank said on Sunday it had banned Deutsche Bank from trading Taiwan dollar deliverable and non-deliverable forwards and suspended it for two years from trading forex derivatives as part of a crackdown on speculation."}' \
  http://localhost:5002/feedback
.PHONY: test

test_ner:
	curl --header "Content-Type: application/json" \
  --request POST \
  -d '{"text":"Taiwan'\''s central bank said on Sunday it had banned Deutsche Bank from trading Taiwan dollar deliverable and non-deliverable forwards and suspended it for two years from trading forex derivatives as part of a crackdown on speculation."}' \
  http://localhost:5000/ner
.PHONY: test_ner

test_model:
	curl --header "Content-Type: application/json" \
  --request POST \
  -d '{"data":"Taiwan'\''s central bank said on Sunday it had banned Deutsche Bank from trading Taiwan dollar deliverable and non-deliverable forwards and suspended it for two years from trading forex derivatives as part of a crackdown on speculation."}' \
  http://localhost:8087/invocations
.PHONY: test_model

test_kb:
	curl --header "Content-Type: application/json" \
  --request POST \
  -d '{"data":"Taiwan'\''s central bank said on Sunday it had banned Deutsche Bank from trading Taiwan dollar deliverable and non-deliverable forwards and suspended it for two years from trading forex derivatives as part of a crackdown on speculation."}' \
  http://localhost:8088/knowledge-base
.PHONY: test_kb