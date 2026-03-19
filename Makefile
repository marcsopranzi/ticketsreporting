.PHONY: build post-data down logs

# 1. Bake the fresh Python images, start the cluster, and handle the Postgres race condition
build:
	# Start the base infra and the init container
	docker compose up -d --build postgres redis redpanda clickhouse airflow-init api
	@echo "Waiting for Airflow database migrations to finish..."
	sleep 15
	# Now start the 'muscle' of Airflow once the metadata DB is ready
	docker compose up -d airflow-webserver airflow-scheduler airflow-worker
	docker compose up -d api
	@echo "All systems GO. Access Airflow at http://localhost:8085"

# 2. Fire a test ticket into the API
post-data:
	curl -X POST http://localhost:8081/buy-ticket -H "Content-Type: application/json" -d '{"user_id": "u123", "event_name": "Candlelight"}'

# 3. Tear everything down cleanly
down:
	docker compose down -v

# 4. Watch the API logs to see if it crashes
logs:
	docker compose logs -f api