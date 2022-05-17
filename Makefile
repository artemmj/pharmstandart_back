nope:
	$(error Invalid target)

check-env-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

up:
	docker-compose -f docker-compose.yml up -d

down:
	docker-compose down

log:
	docker-compose logs -f --tail 100

restart:
	docker-compose -f docker-compose.yml restart app celery

stop:
	docker-compose stop

deploy:
	git pull && make restart
	docker-compose exec app ./manage.py migrate

shell:
	docker-compose exec app ./manage.py shell

migrate:
	docker-compose exec app make migrate

admin:
	docker-compose exec app ./manage.py createsuperuser

test:
	docker-compose exec app make test

test-nomigrations:
	docker-compose exec app pytest --disable-warnings --nomigrations

bash:
	docker-compose exec app bash
