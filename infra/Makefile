


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
	AIRFLOW_UID=1000 docker-compose  up -d 

down:
	docker-compose down