FROM python:3.11-slim

# Evita la generazione dei .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Log immediati
ENV PYTHONUNBUFFERED=1

WORKDIR /app

###########################################################
# Dipendenze di sistema
###########################################################

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

###########################################################
# Installazione librerie Python
###########################################################

COPY streamlit/requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

###########################################################
# Copia del progetto
###########################################################

COPY . .

###########################################################
# Streamlit
###########################################################

EXPOSE 8501

CMD streamlit run agente_ai.py --server.address=0.0.0.0 --server.port=8501
