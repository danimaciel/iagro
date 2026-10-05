"""iAgro: gera os dados da página de busca (GitHub Pages) a partir da base do agente.

Lê agente/base/documentos.json e documentos_e5.npy (gerados por agente/preparar_base.py) e grava:
  site/dados/documentos.json   campos que a página mostra (chaves curtas para o arquivo ficar leve)
  site/dados/vetores.bin       vetores e5 em int8 (escala única), na mesma ordem
  site/dados/resumo.json       números para o cabeçalho (totais por tipo, anos)
Rodar de novo sempre que a base mudar:  python site/preparar_site.py
"""
import json
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "agente" / "base"
SAIDA = Path(__file__).resolve().parent / "dados"
SAIDA.mkdir(exist_ok=True)

itens = json.loads((BASE / "documentos.json").read_text(encoding="utf-8"))
E = np.load(BASE / "documentos_e5.npy")

docs = []
for i in itens:
    d = {"c": i["codigo"], "t": i["titulo"], "r": i["texto"], "a": i["ano"], "d": i["detalhe"],
         "k": i["palavras"], "l": i["link"]}
    if i.get("autores"):
        d["au"] = i["autores"]
    if i.get("onde_encontrar"):
        d["o"] = i["onde_encontrar"]
    if i.get("bioma"):
        d["b"] = i["bioma"]
    docs.append(d)
(SAIDA / "documentos.json").write_text(json.dumps(docs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

escala = float(np.abs(E).max())
q = np.round(E / escala * 127).astype(np.int8)
q.tofile(SAIDA / "vetores.bin")

anos = [int(i["ano"]) for i in itens if i["codigo"].startswith("PUB") and str(i["ano"]).isdigit()]
por_ano = {a: anos.count(a) for a in range(min(anos), max(anos) + 1)}
resumo = {
    "unidade": "Embrapa Territorial",
    "exportacao": "setembro de 2026",
    "dim": int(E.shape[1]), "n": len(itens), "escala": escala,
    "publicacoes": sum(i["codigo"].startswith("PUB") for i in itens),
    "solucoes": sum(i["codigo"].startswith("TEC") for i in itens),
    "projetos": sum(i["codigo"].startswith("PRJ") for i in itens),
    "ano_min": min(anos), "ano_max": max(anos), "por_ano": por_ano,
}
(SAIDA / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False), encoding="utf-8")
tam = sum(f.stat().st_size for f in SAIDA.iterdir()) / 1e6
print(f"{len(docs)} documentos | dados da página: {tam:.1f} MB | escala {escala:.4f}")
