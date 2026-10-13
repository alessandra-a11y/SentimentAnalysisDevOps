from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Numero totale di richieste HTTP",
    ["method", "endpoint", "status_code"]
)

# Tempo di risposta delle richieste
REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "Tempo di risposta delle richieste HTTP",
    ["endpoint"]
)

# Numero di predizioni effettuate
PREDICTION_COUNT = Counter(
    "sentiment_predictions_total",
    "Numero di predizioni per sentiment",
    ["sentiment"]
)

PREDICTION_ERRORS = Counter(
    "sentiment_prediction_errors_total",
    "Numero totale di errori durante la predizione"
)
