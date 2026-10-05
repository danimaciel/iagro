"""iAgro: prepara a base de conhecimento do agente.

Lê as exportações do Redape em Dados/ (publicações, soluções tecnológicas e projetos),
filtra a unidade escolhida e grava:
  agente/base/documentos.json    um item por documento, com código (PUB/TEC/PRJ + ID), texto e link
  agente/base/documentos_e5.npy  vetores do modelo multilingual-e5-base (mesma ordem)
Usa só título + resumo/descrição (decisão de 05/10/2026). Dados/AutorPessoalEmbrapa.xls não é lido (dado pessoal).

Uso:  python agente/preparar_base.py                      (piloto: Embrapa Territorial)
      python agente/preparar_base.py --unidade "Embrapa Solos"
      python agente/preparar_base.py --mes 2026-10         (outra exportação)
No processador leva cerca de 10 minutos para a Territorial (cerca de 3 documentos por segundo).
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
BASE = AQUI / "base"
BASE.mkdir(exist_ok=True)

ap = argparse.ArgumentParser()
ap.add_argument("--unidade", default="Embrapa Territorial")
ap.add_argument("--mes", default="2026-09")
args = ap.parse_args()


def ler(nome):
    return pd.read_csv(RAIZ / "Dados" / f"{nome}-da-embrapa-{args.mes}.csv", dtype=str).fillna("")


def limpo(t):
    return " ".join(str(t).split())


def da_unidade(df, col):
    return df[df[col].str.contains(args.unidade, regex=False)]


itens = []
for _, r in da_unidade(ler("solucoes-tecnologicas"), "Unidade responsável").iterrows():
    itens.append({
        "codigo": f"TEC {r['ID']}", "tipo_doc": "solução tecnológica",
        "titulo": limpo(r["Nome"]), "texto": limpo(r["Descrição"]),
        "detalhe": limpo(" - ".join(x for x in (r["Tipo"], r["Subtipo"]) if x)),
        "ano": r["Ano de lançamento"], "bioma": limpo(r["Bioma"]), "onde_encontrar": limpo(r["Onde encontrar"]),
        "palavras": limpo(r["Palavras-chave"]), "link": r["Página da tecnologia no Portal Embrapa"],
    })
for _, r in da_unidade(ler("projetos"), "Unidade líder").iterrows():
    itens.append({
        "codigo": f"PRJ {r['ID']}", "tipo_doc": "projeto",
        "titulo": limpo(r["Título"]), "texto": limpo(r["Resumo"]),
        "detalhe": f"{r['Situação']}; {r['mês/ano de início']} a {r['mês/ano de finalização']}",
        "ano": r["mês/ano de início"][-4:], "lider": limpo(r["Líder do projeto"]),
        "palavras": limpo(r["Palavras-chave"]), "link": r["Página do projeto no Portal Embrapa"],
    })
for _, r in da_unidade(ler("publicacoes"), "Unidade").iterrows():
    itens.append({
        "codigo": f"PUB {r['ID']}", "tipo_doc": "publicação",
        "titulo": limpo(r["Título"]), "texto": limpo(r["Resumo"]),
        "detalhe": limpo(r["Tipo de publicação"]), "ano": r["Ano de publicação"],
        "autores": limpo(r["Autores"]), "palavras": limpo(r["Palavras-chave"]),
        "link": r["Página da publicação no Portal Embrapa"], "arquivo": r["URL do arquivo"],
    })

tipos = pd.Series([i["tipo_doc"] for i in itens]).value_counts()
print(args.unidade, "|", len(itens), "documentos |", tipos.to_dict())
print("sem resumo/descrição:", sum(not i["texto"] for i in itens))
(BASE / "documentos.json").write_text(json.dumps(itens, ensure_ascii=False, indent=1), encoding="utf-8")

from sentence_transformers import SentenceTransformer

m = SentenceTransformer("intfloat/multilingual-e5-base")
textos = ["passage: " + i["titulo"] + ". " + (i["texto"] or i["palavras"])[:1200] for i in itens]
E = m.encode(textos, normalize_embeddings=True, batch_size=16, show_progress_bar=True)
np.save(BASE / "documentos_e5.npy", E.astype("float32"))
print("vetores:", E.shape)
