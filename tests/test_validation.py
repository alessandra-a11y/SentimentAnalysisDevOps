import pytest
from fastapi import HTTPException

from progetto import valida_richiesta
from models.sentiment_analisys import Testo


def test_recensione_valida():
    testo = Testo(review="This product is amazing!")

    valida_richiesta(testo)


def test_recensione_vuota():
    testo = Testo(review="")

    with pytest.raises(HTTPException) as exc:
        valida_richiesta(testo)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Testo della richiesta non definito"


def test_recensione_solo_spazi():
    testo = Testo(review="     ")

    with pytest.raises(HTTPException) as exc:
        valida_richiesta(testo)

    assert exc.value.status_code == 400


def test_recensione_solo_newline():
    testo = Testo(review="\n\t")

    with pytest.raises(HTTPException) as exc:
        valida_richiesta(testo)

    assert exc.value.status_code == 400