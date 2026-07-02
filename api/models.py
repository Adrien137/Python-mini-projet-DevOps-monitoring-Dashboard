"""Modèles de données pour les serveurs surveillés."""

from dataclasses import dataclass, field
from typing import Literal, Optional

from pydantic import BaseModel, Field

Status = Literal["UP", "DEGRADED", "DOWN"]


@dataclass
class Server:
    """Représente un serveur enregistré pour le monitoring."""

    id: str
    name: str
    host: str
    port: int
    status: Status = "DOWN"
    last_checked: Optional[str] = field(default=None)

    def base_url(self) -> str:
        """Construit l'URL de base HTTP du serveur (ex: http://host:port)."""
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    """Schéma de validation pour la création d'un serveur."""

    name: str = Field(..., min_length=1)
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)


class ServerOut(BaseModel):
    """Schéma de sortie représentant l'état d'un serveur."""

    id: str
    name: str
    host: str
    port: int
    status: Status
    last_checked: Optional[str] = None
