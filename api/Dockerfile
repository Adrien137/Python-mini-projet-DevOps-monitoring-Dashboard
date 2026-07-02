# --- Stage 1 : builder ---------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Installe les dépendances dans un répertoire isolé pour pouvoir le copier
# tel quel dans l'image finale, sans pip ni outils de build.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2 : runtime -----------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copie uniquement les paquets installés (pas pip, pas les headers de build)
COPY --from=builder /install /usr/local

COPY api/ ./api/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
