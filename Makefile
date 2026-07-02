.PHONY: install api dashboard dev test lint up down logs

install:
	pip install -r requirements.txt

api:
	uvicorn api.main:app --reload --port 8000

dashboard:
	streamlit run dashboard/app.py

dev:
	@echo "Lancement de l'API et du dashboard en parallèle (Ctrl+C pour arrêter)"
	@trap 'kill 0' SIGINT; \
	uvicorn api.main:app --reload --port 8000 & \
	streamlit run dashboard/app.py & \
	wait

test:
	pytest tests/ -v --cov=api --cov-fail-under=75

lint:
	flake8 api/ dashboard/ tests/

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f
