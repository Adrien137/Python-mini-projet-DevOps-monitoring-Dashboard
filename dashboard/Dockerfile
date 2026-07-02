FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Le dashboard n'a besoin que de streamlit, httpx et pandas, mais on
# réutilise le même requirements.txt pour rester simple et cohérent.
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ ./dashboard/

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
