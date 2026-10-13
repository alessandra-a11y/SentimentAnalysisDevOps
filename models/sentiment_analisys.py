from pydantic import BaseModel

# definisco le classi che serviranno per effettuare la request  (Testo) e per restituire la response (PredictionOutput)
# con i dati richiesti dalle specifiche

class ProductReview(BaseModel):
    review: str


class PredictionOutput(BaseModel):
    sentiment: str
    confidence: float