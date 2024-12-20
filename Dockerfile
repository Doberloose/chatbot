FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copie du fichier de lancement
WORKDIR /app
RUN git clone https://github.com/Doberloose/chatbot.git .

# Mise à jour de pip3
RUN pip3 install --upgrade pip
#installation des requirements
RUN pip3 install -r requirements.txt

# On ouvre et expose le port 8501
EXPOSE 5000

ENTRYPOINT ["streamlit", "run", "/app/chatbot.py", "--server.port=5000", "--server.address=0.0.0.0"]