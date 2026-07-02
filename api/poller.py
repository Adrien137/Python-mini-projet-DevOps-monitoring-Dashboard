"""Polling périodique de l'état de santé des serveurs enregistrés."""

import asyncio
from datetime import datetime, timezone
from typing import Dict

import httpx

from api.models import Server

POLL_INTERVAL_SECONDS = 10
HEALTH_TIMEOUT_SECONDS = 3.0


async def poll_server(server: Server, client: httpx.AsyncClient) -> None:
    """Teste GET /health d'un serveur et met à jour son statut en place.

    - UP : réponse 200 reçue dans le délai imparti
    - DEGRADED : réponse reçue mais code HTTP différent de 200
    - DOWN : timeout, erreur de connexion, ou toute exception réseau

    Args:
        server: instance Server à vérifier (modifiée en place).
        client: client httpx asynchrone partagé entre les appels.
    """
    url = f"{server.base_url()}/health"

    try:
        response = await client.get(url, timeout=HEALTH_TIMEOUT_SECONDS)
        server.status = "UP" if response.status_code == 200 else "DEGRADED"
    except httpx.RequestError:
        server.status = "DOWN"
    finally:
        server.last_checked = datetime.now(timezone.utc).isoformat()


async def run_poll_loop(servers: Dict[str, Server]) -> None:
    """Boucle infinie : vérifie tous les serveurs toutes les 10 secondes.

    Args:
        servers: dictionnaire partagé {id: Server}, modifié en place.
            Pensé pour tourner en tâche de fond depuis le lifespan FastAPI.
    """
    async with httpx.AsyncClient() as client:
        while True:
            if servers:
                await asyncio.gather(
                    *(poll_server(server, client) for server in servers.values())
                )
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
