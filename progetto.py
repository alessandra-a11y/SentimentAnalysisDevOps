import pickle
import time
from pathlib import Path

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette import status
from fastapi import FastAPI, HTTPException,Response
import uvicorn
import logging

from starlette.requests import Request

from models.metrics import REQUEST_COUNT, REQUEST_LATENCY,PREDICTION_COUNT, PREDICTION_ERRORS
from models.sentiment_analisys import ProductReview, PredictionOutput

# definisco la configurazione dei log per tenere traccia delle chiamate effettuate all'endpoint, della response
# e di eventuali errori.
# Uso il livello logging.INFO in modo da tracciare anche i messaggi informativi oltre quelli che di errore
# Definisco il file dove sarà salvato il log che avrà il nome SentimentAnalysisAPI.log
LOG_FORMAT = "[%(levelname)s]%(name)s - %(asctime)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

file_handler = logging.FileHandler("SentimentAnalysisAPI.log")
file_handler.setLevel(LOG_LEVEL)

formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
file_handler.setFormatter(formatter)

# Per evitare duplicazioni se il logger è inizializzato più volte
if not logger.handlers:
    logger.addHandler(file_handler)

# Leggo e carico il file contenente il modello usato per effettuare la predizione
# che si trova nella stessa cartella del file progetto.py

BASE_DIR = Path(__file__).resolve().parent

filename = BASE_DIR / "sentiment_analysis_model.pkl"


with open(filename, 'rb') as file:
    model = pickle.load(file)

# inizializzo l'oggetto di FastAPI
app = FastAPI(title='SentimentAnalysisAPI', description='Rest API per sentiment analysis sulle recensioni',
              version='1.0.0', include_in_schema=True)


def valida_richiesta(testo: ProductReview):

    """
        Metodo valida_richiesta per validare l'input della request.
        Se il testo (text) non è stato definito (è vuoto composto solo da spazi
        lancia HTTPException con stato 400 e messaggio nel dettaglio)

    """

    if testo.review.strip() == '':
        logger.error(f"ERROR - endpoint=/predict - Testo della richiesta non definito")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Testo della richiesta non definito")





def predict(testo: ProductReview):

    """
        Metodo predict che accetta una recensione in JSON e restituisce il sentimento analizzato.
        Restuisce un oggetto PredictionOutput contenente il sentiment e il grado di confidenza
        della predizione effettuata dal modello.
        In caso di errore (che non sia gestito nella validazione della richiesta) lancia  HTTPException con codice 500
        e viene tracciato nel log
    """

    logger.info(f"REQUEST - endpoint=/predict - review={testo.review}")

    valida_richiesta(testo)

    try:
        text_to_predict = [testo.review]
        predicted_sentiment = model.predict(text_to_predict)
        predicted_sentiment_text = predicted_sentiment[0]

        if predicted_sentiment_text is None or str(predicted_sentiment_text).strip() == '':
            logger.error(f"ERROR - endpoint=/predict - text={testo.review} - Il sentiment della recensionenon può essere identificato")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Il sentiment della recensione non può essere identificato"
            )

        predicted_proba = model.predict_proba(text_to_predict)[0]
        confidence = round(float(predicted_proba.max()), 2)

        PREDICTION_COUNT.labels(
            sentiment=str(predicted_sentiment_text)
        ).inc()

        logger.info(f"RESPONSE - endpoint=/predict - language={predicted_sentiment_text}, confidence={confidence}")

        return PredictionOutput(sentiment=predicted_sentiment_text,confidence=confidence)

    except HTTPException:
        raise
    except Exception as e:

        logger.error(f"ERROR - endpoint=/predict - {str(e)}")

        PREDICTION_ERRORS.inc()

        logger.exception("Errore durante la predizione")

        raise HTTPException(status_code=500,detail="Non è possibile identificare il sentiment della recensione")


# endpoint da chiamare per l'identificazione del sentimenti di una recensione passata come input
# riceve in ingresso un oggetto Testo e restituisce in output un oggetto PredictionOutput
@app.post("/predict")
def predict_sentiment(testo: ProductReview) -> PredictionOutput:
    return predict(testo)

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(),media_type=CONTENT_TYPE_LATEST)

from fastapi import HTTPException

@app.get("/health", tags=["Monitoring"])
def health_check():
    """
       Verifica lo stato del servizio di Sentiment Analysis.
       Controlla che il modello sia disponibile, restituendo HTTP 200
       se il servizio è operativo oppure HTTP 503 in caso contrario.
       """

    if model is None:
        raise HTTPException(status_code=503,detail="Modello Sentiment Analisys non disponibile")

    return {
        "status": "healthy",
        "model": "loaded",
        "service": "sentiment-analysis"
    }

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code="500"
        ).inc()
        raise
    else:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=str(response.status_code)
        ).inc()

        return response
    finally:
        duration = time.perf_counter() - start_time

        REQUEST_LATENCY.labels(
            endpoint=request.url.path
        ).observe(duration)




# lancio dell'applicazione
if __name__ == '__main__':
    uvicorn.run(app)
