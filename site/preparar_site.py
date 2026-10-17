"""iAgro: gera os dados da página de busca (GitHub Pages) a partir da base do agente.

Lê agente/base/documentos.json e documentos_e5.npy (gerados por agente/preparar_base.py) e grava:
  site/dados/documentos.json   campos que a página mostra (chaves curtas para o arquivo ficar leve)
  site/dados/vetores.bin       vetores e5 em int8 (escala única), na mesma ordem
  site/dados/resumo.json       números para o cabeçalho (totais por tipo, anos) e nomes dos produtos

Produtos e localização (desde 17/10/2026): do Observatório de Pesquisa da Embrapa. Antes de rodar, baixe a
release pública mais recente para enriquecimento/ (fora do git):
  gh release download enriquecimento-AAAA-MM --repo danimaciel/observatorio_embrapa -D enriquecimento --clobber
Só produtos de força "principal" (título ou palavras-chave). Em documentos.json: pp, uf, bi.

Rodar de novo sempre que a base ou o enriquecimento mudarem:  python site/preparar_site.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "agente" / "base"
ENR = RAIZ / "enriquecimento"
SAIDA = Path(__file__).resolve().parent / "dados"
SAIDA.mkdir(exist_ok=True)

itens = json.loads((BASE / "documentos.json").read_text(encoding="utf-8"))
E = np.load(BASE / "documentos_e5.npy")

# produtos e localização do Observatório, ligados pelo identificador do Redape
enr, produtos = {}, {}
if (ENR / "enriquecimento.csv.gz").exists():
    e = pd.read_csv(ENR / "enriquecimento.csv.gz", dtype=str).fillna("").set_index("doc_uid")
    reg = pd.read_csv(ENR / "registro_obra.csv.gz", dtype=str)
    obra = dict(zip(reg.registro.str[2:], reg.obra_id))
    tax = pd.read_csv(ENR / "produtos.csv", dtype=str).fillna("").set_index("produto_id")

    def uid(cod):
        t, n = cod.split()
        return obra.get(n, "OB:" + n) if t == "PUB" else ("P:" if t == "PRJ" else "T:") + n
    for i in itens:
        u = uid(i["codigo"])
        if u in e.index:
            enr[i["codigo"]] = e.loc[u]
    usados = {x for r in enr.values() for x in r.produtos.split(";") if x}
    produtos = {pid: {"nome": tax.loc[pid, "produto"], "cat": tax.loc[pid, "categoria_ampla"]} for pid in usados if pid in tax.index}
else:
    print("sem enriquecimento/: página sem produtos e localização")

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
    r = enr.get(i["codigo"])
    if r is not None:
        for chave, col in (("pp", "produtos"), ("uf", "ufs"), ("bi", "biomas")):
            v = [y for y in r[col].split(";") if y]
            if v:
                d[chave] = v
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
    "produtos": produtos,
}
(SAIDA / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False), encoding="utf-8")
tam = sum(f.stat().st_size for f in SAIDA.iterdir()) / 1e6
print(f"{len(docs)} documentos | com produto {sum('pp' in d for d in docs)} | com estado {sum('uf' in d for d in docs)} | "
      f"dados da página: {tam:.1f} MB | escala {escala:.4f}")
