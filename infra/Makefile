


volumes:
	docker volume create mongodata
	docker volume create mongoconf
	docker volume create zoodata
	docker volume create zooconf


clean_zookeeper:
	docker volume rm zoodata
	docker volume rm zooconf

clean: down clean_zookeeper


up:
	docker-compose -f docker-compose.yml up -d --remove-orphans

down:
	docker-compose -f docker-compose.yml down