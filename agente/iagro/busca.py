"""Busca na base do iAgro: modelo semântico e5 + palavras (TF-IDF), fusão por posição (RRF).

Busca sobre o que a Embrapa Territorial produziu e produz: publicações, soluções tecnológicas
e projetos (agente/base/documentos.json, gerado por preparar_base.py).
"""
import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
BASE = Path(__file__).resolve().parents[1] / "base"


@lru_cache(maxsize=1)
def _carregar():
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer

    itens = json.loads((BASE / "documentos.json").read_text(encoding="utf-8"))
    E = np.load(BASE / "documentos_e5.npy")
    modelo = SentenceTransformer("intfloat/multilingual-e5-base")
    tf = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1, 2), sublinear_tf=True)
    A = tf.fit_transform([f"{i['titulo']} {i['texto']} {i['palavras']}" for i in itens])
    return itens, E, modelo, tf, A


def buscar(pergunta: str, k: int = 4) -> list[dict]:
    itens, E, modelo, tf, A = _carregar()
    q = modelo.encode(["query: " + pergunta], normalize_embeddings=True)[0]
    s_e5 = E @ q
    s_tf = (A @ tf.transform([pergunta]).T).toarray().ravel()
    pos = lambda s: np.argsort(np.argsort(-s))
    rrf = 1 / (60 + pos(s_e5)) + 1 / (60 + pos(s_tf))
    return [dict(itens[j], semelhanca=round(float(s_e5[j]), 3)) for j in np.argsort(-rrf)[:k]]
