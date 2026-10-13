
# Immagine base Python
FROM python:3.12-slim

# Evita la generazione di file .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Disabilita il buffering dei log Python
ENV PYTHONUNBUFFERED=1

# Directory di lavoro
WORKDIR /app

# Copia le dipendenze
COPY requirements.txt .

# Installa le librerie Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione e il modello
COPY . .

# Crea un utente senza privilegi amministrativi
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Porta del servizio FastAPI
EXPOSE 8000

# Avvio del servizio
CMD ["uvicorn", "progetto:app", "--host", "0.0.0.0", "--port", "8000"]
