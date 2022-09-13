

build:
	docker build -f Dockerfile -t obner .


run:
	docker run --rm -p 7000:5000 --net infra obner

test:
	curl --header "Content-Type: application/json" \
  --request POST \
  -d '{"text":"Taiwan'\''s central bank said on Sunday it had banned Deutsche Bank from trading Taiwan dollar deliverable and non-deliverable forwards and suspended it for two years from trading forex derivatives as part of a crackdown on speculation."}' \
  http://localhost:7000/ner
