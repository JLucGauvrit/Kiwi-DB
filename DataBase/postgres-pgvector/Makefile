```makefile
# Makefile to manage postgres-pgvector image and container

IMAGE_NAME=postgres-pgvector:local
CONTAINER_NAME=postgres-pgvector
NETWORK=bdd_network
VOLUME=pgdata_pgvector
PORT=5432
USER=user
PASSWORD=password
DB=dbname

.PHONY: build create start run stop rm logs status download convert import init

build:
	docker build -t $(IMAGE_NAME) .

create:
	docker network inspect $(NETWORK) >/dev/null 2>&1 || docker network create $(NETWORK)
	docker create --name $(CONTAINER_NAME) \
		--network $(NETWORK) \
		-e POSTGRES_USER=$(USER) \
		-e POSTGRES_PASSWORD=$(PASSWORD) \
		-e POSTGRES_DB=$(DB) \
		-v $(VOLUME):/var/lib/postgresql/data \
		-p $(PORT):5432 \
		--restart unless-stopped \
		$(IMAGE_NAME) || true

start:
	@if [ -z "$(shell docker ps -a -q -f name=^/$(CONTAINER_NAME)$$)" ]; then \
		$(MAKE) create; \
	else \
		docker start $(CONTAINER_NAME); \
	fi

run: build start

run-all: build
	$(MAKE) start
	docker exec -it $(CONTAINER_NAME) psql -U $(USER) -d $(DB) -f /docker-entrypoint-initdb.d/03-droit-travail-data.sql

stop:
	docker stop $(CONTAINER_NAME) || true

rm:
	docker rm -f $(CONTAINER_NAME) || true

logs:
	docker logs -f $(CONTAINER_NAME)

status:
	docker ps -a -f name=$(CONTAINER_NAME)

```
