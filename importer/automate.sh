docker exec -u root mongodb rm -f crawler.json
docker exec -u root mongodb mongoexport --db=crawler --collection=contents --out=crawler.json
docker cp  `docker ps -aqf "name=mongodb"`:crawler.json ./crawler.json


# docker cp /home/visnja/Downloads/mongodump-2020-07-20 `docker ps -aqf "name=mongodb"`:mongodump-2020-07-20
# docker exec -u root mongodb mongorestore mongodump-2020-07-20/dump-2020-07-20