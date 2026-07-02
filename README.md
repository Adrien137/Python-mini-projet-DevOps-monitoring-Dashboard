Si les identifiants azure ne fonctionne pas, vous pouvez lancer et faire fonctionner l'api en local en téléchargent le repo


# DevOps Monitoring Dashboard

Système de monitoring temps réel construit en Python pour le projet final Day 5.
L'API FastAPI expose les métriques système et gère une liste de serveurs à surveiller.
Le dashboard Streamlit affiche tout ça en live.

## Architecture

```
GitHub Actions (push main)
  └── lint → tests → build Docker → push ACR → deploy Azure Container Apps

Azure Container Apps
  ├── devops-monitor-api        FastAPI  :8000
  └── devops-monitor-dashboard  Streamlit :8501
```

## Ce que ça fait

- `GET /health` : liveness probe
- `GET /metrics` : CPU, mémoire, disque via psutil
- `WS /ws/metrics` : stream JSON des métriques toutes les secondes
- `POST /servers` : enregistre un serveur (header `X-API-Key` requis)
- `GET /servers` : liste les serveurs et leur statut
- `DELETE /servers/{id}` : supprime un serveur (header `X-API-Key` requis)
- `POST /servers/{id}/check` : déclenche un health check manuel
- Dashboard Streamlit : KPIs, graphique live 60s, tableau coloré des serveurs, formulaire d'ajout

## Prérequis

- Docker Desktop (inclut Docker Compose) — https://www.docker.com/products/docker-desktop
- Python 3.11 uniquement si tu veux lancer sans Docker

## Lancement avec Docker Desktop

C'est la façon la plus simple, aucune installation Python nécessaire.

**1. Créer le fichier `.env`** à la racine du projet (copier `.env.example`) :

```
API_KEY=monmotdepasse123
API_BASE_URL=http://api:8000
```

**2. Démarrer la stack :**

```bash
docker compose up --build -d
```

**3. Accéder aux services :**

- API + Swagger UI : http://localhost:8000/docs
- Dashboard : http://localhost:8501

**4. Voir les logs :**

```bash
docker compose logs -f
```

**5. Arrêter :**

```bash
docker compose down -v
```

## Lancement sans Docker

Dans deux terminaux séparés depuis la racine du projet :

```bash
# Terminal 1 - API
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Terminal 2 - Dashboard
streamlit run dashboard/app.py
```

Pense à créer le `.env` avec `API_KEY` et `API_BASE_URL=http://localhost:8000` avant de lancer.

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=api --cov-fail-under=75
flake8 api/ dashboard/ tests/
```

## Variables d'environnement

| Variable | Description |
|---|---|
| `API_KEY` | Clé requise dans le header `X-API-Key` pour les routes protégées |
| `API_BASE_URL` | URL de l'API vue par le dashboard (`http://api:8000` en Docker) |

Le fichier `.env` ne doit jamais être commité. Seul `.env.example` est versionné.

## CI/CD

Le workflow `.github/workflows/ci-cd.yml` enchaîne trois jobs :

1. `test` : lint flake8 + pytest avec coverage ≥ 75%
2. `build` : build et push des deux images vers Azure Container Registry (main uniquement)
3. `deploy` : mise à jour des deux Container Apps (main uniquement)

Secrets GitHub à configurer :

| Secret | Contenu |
|---|---|
| `AZURE_CREDENTIALS` | JSON issu de `az ad sp create-for-rbac` |
| `ACR_NAME` | Nom du registry sans `.azurecr.io` |
| `API_KEY` | Clé injectée dans les Container Apps |

## Commandes Azure (infra initiale)

```bash
az group create --name devops-monitor-rg --location westeurope
az acr create --name <ACR_NAME> --resource-group devops-monitor-rg --sku Basic
az containerapp env create \
  --name devops-monitor-env \
  --resource-group devops-monitor-rg \
  --location westeurope
```

## URLs live

- API : `https://<api-url>/docs`
- Dashboard : `https://<dashboard-url>`
