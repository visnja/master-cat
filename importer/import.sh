
docker cp ./crawler.json `docker ps -aqf "name=mongodb"`:crawler.json 
docker exec -u root mongodb mongoimport --db=crawler --collection=contents --file=crawler.json