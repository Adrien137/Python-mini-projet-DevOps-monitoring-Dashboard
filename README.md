# DevOps Monitoring Dashboard

Projet final Day 5 : système de monitoring temps réel en Python avec une API FastAPI, un dashboard Streamlit, des tests, une stack Docker Compose et un pipeline CI/CD GitHub Actions pour Azure Container Apps.

## Architecture

```text
GitHub Repository
  └─ GitHub Actions : lint -> tests -> build Docker -> push ACR -> deploy Azure Container Apps

Docker / Azure Container Apps
  ├─ devops-monitor-api        FastAPI, port 8000
  └─ devops-monitor-dashboard  Streamlit, port 8501
```

## Fonctionnalités

- `GET /health` : liveness probe
- `GET /metrics` : métriques CPU, mémoire et disque via `psutil`
- `WS /ws/metrics` : stream JSON des métriques toutes les secondes
- `POST /servers` : ajout d'un serveur, protégé par `X-API-Key`
- `GET /servers` : liste des serveurs avec statut
- `DELETE /servers/{id}` : suppression d'un serveur, protégé par `X-API-Key`
- `POST /servers/{id}/check` : health check manuel
- Dashboard Streamlit avec KPIs, graphique live et tableau des serveurs

## Structure

```text
devops-monitor/
├── api/
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── metrics.py
│   ├── poller.py
│   └── Dockerfile
├── dashboard/
│   ├── app.py
│   └── Dockerfile
├── tests/
├── .github/workflows/ci-cd.yml
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── Makefile
├── requirements.txt
└── README.md
```

## Prérequis

- Python 3.11
- Docker et Docker Compose
- Make
- Compte Azure + Azure CLI pour la partie déploiement

## Lancement local avec Docker

```bash
cp .env.example .env
# Modifier API_KEY dans .env
make up
```

URLs locales :

- API Swagger : http://localhost:8000/docs
- Dashboard : http://localhost:8501

Commandes utiles :

```bash
make logs
make down
```

## Lancement local sans Docker

```bash
cp .env.example .env
make install
make dev
```

Ou dans deux terminaux :

```bash
uvicorn api.main:app --reload --port 8000
streamlit run dashboard/app.py
```

## Tests et qualité

```bash
make lint
make test
```

La commande de test impose une couverture minimale de 75 % :

```bash
pytest tests/ -v --cov=api --cov-fail-under=75
```

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `API_KEY` | Clé requise dans le header `X-API-Key` pour les routes protégées | `changeme123` |
| `API_BASE_URL` | URL de l'API utilisée par le dashboard | `http://api:8000` en Docker |

Le fichier `.env` ne doit jamais être commité. Seul `.env.example` est versionné.

## Docker Compose

Le service `dashboard` communique avec l'API via le nom de service Docker :

```yaml
API_BASE_URL=http://api:8000
```

Il ne faut pas utiliser `localhost` entre deux conteneurs.

## CI/CD GitHub Actions

Le workflow `.github/workflows/ci-cd.yml` contient trois jobs :

1. `test` : installation, lint `flake8`, tests `pytest` avec coverage
2. `build` : build et push des images API et Dashboard vers Azure Container Registry
3. `deploy` : mise à jour des deux Azure Container Apps

Secrets GitHub attendus :

| Secret | Description |
|---|---|
| `AZURE_CREDENTIALS` | JSON généré pour `azure/login` |
| `ACR_NAME` | Nom de l'Azure Container Registry sans `.azurecr.io` |
| `API_KEY` | Clé injectée dans les Container Apps |

Exemple de création du secret `AZURE_CREDENTIALS` :

```bash
az ad sp create-for-rbac \
  --name devops-monitor-gha \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/devops-monitor-rg \
  --sdk-auth
```

## Commandes Azure utiles

```bash
az group create --name devops-monitor-rg --location westeurope
az acr create --name <ACR_NAME> --resource-group devops-monitor-rg --sku Basic
az containerapp env create \
  --name devops-monitor-env \
  --resource-group devops-monitor-rg \
  --location westeurope
```

Les Container Apps doivent être créées une première fois, puis le pipeline pourra les mettre à jour automatiquement.

## URLs de rendu

À compléter après déploiement Azure :

- API live : `https://<api-url>/docs`
- Dashboard live : `https://<dashboard-url>`

## Sécurité

- Pas de secret dans le code
- Pas de `.env` commité
- Authentification par header `X-API-Key` sur les routes de modification
- Variables sensibles stockées dans GitHub Secrets
