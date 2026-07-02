"""Dashboard Streamlit : visualisation des métriques et gestion des serveurs."""

import os
import time
from datetime import datetime

import httpx
import pandas as pd
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "")

st.set_page_config(page_title="DevOps Monitoring Dashboard", layout="wide")
st.title("DevOps Monitoring Dashboard")

tab_metrics, tab_servers = st.tabs(["Métriques", "Serveurs"])


# ---------------------------------------------------------------------------
# Onglet Métriques
# ---------------------------------------------------------------------------
@st.cache_data(ttl=1)
def fetch_metrics() -> dict:
    """Récupère les métriques courantes depuis l'API (cache 1s)."""
    response = httpx.get(f"{API_BASE_URL}/metrics", timeout=5.0)
    response.raise_for_status()
    return response.json()


with tab_metrics:
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(
            columns=["time", "cpu_percent", "memory_percent", "disk_percent"]
        )

    try:
        data = fetch_metrics()
        col1, col2, col3 = st.columns(3)
        col1.metric("CPU", f"{data['cpu_percent']:.1f} %")
        col2.metric("Mémoire", f"{data['memory_percent']:.1f} %")
        col3.metric("Disque", f"{data['disk_percent']:.1f} %")

        new_row = pd.DataFrame(
            [
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "cpu_percent": data["cpu_percent"],
                    "memory_percent": data["memory_percent"],
                    "disk_percent": data["disk_percent"],
                }
            ]
        )
        st.session_state.history = pd.concat(
            [st.session_state.history, new_row], ignore_index=True
        ).tail(60)  # fenêtre glissante de 60 points (~60s)

        st.line_chart(
            st.session_state.history.set_index("time")[
                ["cpu_percent", "memory_percent", "disk_percent"]
            ]
        )
    except httpx.RequestError:
        st.error(f"Impossible de joindre l'API sur {API_BASE_URL}")


# ---------------------------------------------------------------------------
# Onglet Serveurs
# ---------------------------------------------------------------------------
def status_color(status: str) -> str:
    return {"UP": "🟢", "DEGRADED": "🟠", "DOWN": "🔴"}.get(status, "⚪")


with tab_servers:
    st.subheader("Serveurs enregistrés")

    try:
        response = httpx.get(f"{API_BASE_URL}/servers", timeout=5.0)
        response.raise_for_status()
        servers_data = response.json()

        if servers_data:
            df = pd.DataFrame(servers_data)
            df["état"] = df["status"].apply(status_color) + " " + df["status"]
            st.dataframe(
                df[["name", "host", "port", "état", "last_checked"]],
                use_container_width=True,
            )
        else:
            st.info("Aucun serveur enregistré pour le moment.")
    except httpx.RequestError:
        st.error(f"Impossible de joindre l'API sur {API_BASE_URL}")

    st.divider()
    st.subheader("Enregistrer un nouveau serveur")

    with st.form("add_server_form", clear_on_submit=True):
        name = st.text_input("Nom")
        host = st.text_input("Host")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8000)
        submitted = st.form_submit_button("Ajouter")

        if submitted:
            try:
                resp = httpx.post(
                    f"{API_BASE_URL}/servers",
                    json={"name": name, "host": host, "port": int(port)},
                    headers={"X-API-Key": API_KEY},
                    timeout=5.0,
                )
                if resp.status_code == 201:
                    st.success(f"Serveur '{name}' enregistré.")
                elif resp.status_code == 403:
                    st.error("Clé API invalide ou absente.")
                else:
                    st.error(f"Erreur API ({resp.status_code}) : {resp.text}")
            except httpx.RequestError:
                st.error(f"Impossible de joindre l'API sur {API_BASE_URL}")


# Rafraîchissement live après rendu complet des deux onglets.
# Placé à la fin pour éviter de bloquer l'affichage de l'onglet Serveurs.
time.sleep(1)
st.rerun()
