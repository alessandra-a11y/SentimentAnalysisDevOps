import pickle
from starlette import status
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

# definisco la configurazione dei log per tenere traccia delle chiamate effettuate all'endpoint, della response
# e di eventuali errori.
# Uso il livello logging.INFO in modo da tracciare anche i messaggi informativi oltre quelli che di errore
# Definisco il file dove sarà salvato il log che avrà il nome MuseumLangAPI.log

LOG_FORMAT = "[%(levelname)s]%(name)s - %(asctime)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

file_handler = logging.FileHandler("MuseumLangAPI.log")
file_handler.setLevel(LOG_LEVEL)

formatter = logging.Formatter(LOG_FORMAT,datefmt=DATE_FORMAT)
file_handler.setFormatter(formatter)

# Per evitare duplicazioni se il logger è inizializzato più volte
if not logger.handlers:
    logger.addHandler(file_handler)

# Leggo e carico il file contenente il modello usato per effettuare la predizione
# che si trova nella stessa cartella del file progetto.py

model_filename  = 'language_detection_pipeline.pkl'

with open(model_filename, 'rb') as file:
    model = pickle.load(file)

# definisco le classi che serviranno per effettuare la request  (Testo) e per restituire la response (PredictionOutput)
# con i dati richiesti dalle specifiche

class Testo(BaseModel):
    text: str

class PredictionOutput(BaseModel):
    confidence: float
    language_code: str

# inizializzo l'oggetto di FastAPI
app = FastAPI(title='MuseumLangAPI',description='Rest API per il riconoscimento della lingua di testi di un museo',version='1.0.0',include_in_schema=True)

"""
    Metodo valida_richiesta per validare l'input della request. 
    Se il testo (text) non è stato definito (è vuoto composto solo da spazi
    lancia HTTPException con stato 400 e messaggio nel dettaglio)

"""
def valida_richiesta(testo:Testo):
    if testo.text.strip() == '':

        logger.error(f"ERROR - endpoint=/identify-language - Testo della richiesta non definito")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Testo della richiesta non definito")

"""
    Metodo predict_language per effettuare la predizione della lingua del testo passato nella richiesta. 
    Restuisce un oggetto PredictionOutput contenente il codice della lingua predetta e il grado di confidenza
    della predizione effettuata dal modello.
    In caso di errore (che non sia gestito nella validazione della richiesta) lancia  HTTPException con codice 500
    e viene tracciato nel log
"""
def predict_language(testo: Testo):

    logger.info(f"REQUEST - endpoint=/identify-language - text={testo.text}")

    valida_richiesta(testo)

    try:
        text_to_predict = [testo.text]
        predicted_language = model.predict(text_to_predict)
        predicted_language_text = predicted_language[0]

        if predicted_language_text is None or str(predicted_language_text).strip() == '':

            logger.error(f"ERROR - endpoint=/identify-language - text={testo.text} - La lingua non può essere identificata")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La lingua non può essere identificata"
            )

        predicted_proba = model.predict_proba(text_to_predict)[0]
        confidence = round(float(predicted_proba.max()), 2)

        logger.info(f"RESPONSE - endpoint=/identify-language - language={predicted_language_text}, confidence={confidence}")


        return PredictionOutput(
            confidence=confidence,
            language_code=predicted_language_text
        )

    except HTTPException:
        raise
    except Exception as e:

        logger.error(f"ERROR - endpoint=/identify-language - {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Non è possibile identificare la lingua della frase"
        )


# endpoint da chiamare per l'identificazione del testo passato come input
#riceve in ingresso un oggetto Testo e restituisce in output un oggetto PredictionOutput
@app.post("/identify-language")
def identify_language(testo:Testo) -> PredictionOutput:
    return predict_language(testo)

# lancio dell'applicazione
if __name__ == '__main__':
    uvicorn.run(app)


