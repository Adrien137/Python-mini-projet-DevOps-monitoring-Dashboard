"""Application FastAPI : monitoring temps réel sans Docker ni Azure."""

import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import run_poll_loop

# État en mémoire partagé (pas de base de données pour ce projet).
servers: Dict[str, Server] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Démarre la boucle de polling en tâche de fond au démarrage de l'app."""
    poll_task = asyncio.create_task(run_poll_loop(servers))
    yield
    poll_task.cancel()
    try:
        await poll_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="DevOps Monitoring API", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    """Liveness probe simple."""
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> dict:
    """Retourne les métriques système courantes (CPU, mémoire, disque)."""
    return get_system_metrics()


@app.post("/servers", response_model=ServerOut, status_code=201)
def create_server(
    payload: ServerIn, _api_key: str = Depends(verify_api_key)
) -> ServerOut:
    """Enregistre un nouveau serveur à surveiller (protégé par API key)."""
    server_id = str(uuid.uuid4())
    server = Server(
        id=server_id,
        name=payload.name,
        host=payload.host,
        port=payload.port,
    )
    servers[server_id] = server
    return ServerOut(**server.__dict__)


@app.get("/servers", response_model=List[ServerOut])
def list_servers() -> List[ServerOut]:
    """Liste tous les serveurs enregistrés avec leur statut courant."""
    return [ServerOut(**s.__dict__) for s in servers.values()]


@app.delete("/servers/{server_id}", status_code=204)
def delete_server(server_id: str, _api_key: str = Depends(verify_api_key)) -> None:
    """Supprime un serveur enregistré (protégé par API key)."""
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Serveur introuvable")
    del servers[server_id]


@app.post("/servers/{server_id}/check", response_model=ServerOut)
async def check_server(server_id: str) -> ServerOut:
    """Déclenche un health check manuel et immédiat pour un serveur."""
    import httpx
    from api.poller import poll_server

    server = servers.get(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Serveur introuvable")

    async with httpx.AsyncClient() as client:
        await poll_server(server, client)

    return ServerOut(**server.__dict__)


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket) -> None:
    """Stream les métriques système au format JSON, une fois par seconde."""
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(get_system_metrics())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
