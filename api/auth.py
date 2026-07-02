"""Authentification par clé API via le header X-API-Key."""

import os

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verify_api_key(api_key: str = Security(_api_key_header)) -> str:
    """Vérifie que la clé API fournie correspond à la variable d'env API_KEY.

    Args:
        api_key: valeur du header X-API-Key, injectée par FastAPI.

    Raises:
        HTTPException 403: si la clé est absente ou invalide.

    Returns:
        La clé API validée.
    """
    expected_key = os.environ.get("API_KEY")

    if not expected_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API absente ou invalide",
        )

    return api_key
