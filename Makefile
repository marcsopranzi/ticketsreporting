.PHONY: build post-data down logs

# 1. Bake the fresh Python images and start the cluster
build:
	docker compose up -d --build

# 2. Fire a test ticket into the API
post-data:
	curl -X POST http://localhost:8081/buy-ticket -H "Content-Type: application/json" -d '{"user_id": "u123", "event_name": "Candlelight"}'

# 3. Tear everything down cleanly
down:
	docker compose down -v

# 4. Watch the API logs to see if it crashes
logs:
	docker compose logs -f api