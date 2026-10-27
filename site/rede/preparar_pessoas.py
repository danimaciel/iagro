"""Rede iAgro: gera site/dados/pessoas.json ("quem trabalha com isso") a partir do enriquecimento do Observatório.

Lê de enriquecimento/ (release pública "enriquecimento-AAAA-MM" de danimaciel/observatorio_embrapa, desde a que
traz pessoas.csv.gz, pessoa_produto.csv.gz e evidencias.csv.gz):
  gh release download enriquecimento-AAAA-MM --repo danimaciel/observatorio_embrapa -D enriquecimento --clobber
e de site/dados/resumo.json (gerado por site/preparar_site.py) os produtos que aparecem na base da Territorial.

Para cada produto, as pessoas de toda a Embrapa com maior peso (critério e salvaguardas no Observatório:
vínculos A/B/M, ao menos 3 documentos, 1 dos últimos 10 anos). Só nome e unidade, como nas publicações.
  site/dados/pessoas.json  {"p": {id: [nome, unidade, n_docs, ano_ultimo]},
                            "pp": {produto: [[id, n_docs, n_recentes, n_projetos_lider, n_tecnologias, peso, [doc_uid]]]},
                            "ev": {doc_uid: [tipo, titulo, ano, url]}}
Rodar depois de site/preparar_site.py:  python site/rede/preparar_pessoas.py
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ENR = RAIZ / "enriquecimento"
DADOS = RAIZ / "site" / "dados"
POR_PRODUTO = 8
N_EVIDENCIAS = 3

if not (ENR / "pessoa_produto.csv.gz").exists():
    raise SystemExit("enriquecimento/ sem pessoa_produto.csv.gz: baixe uma release de enriquecimento com pessoas")

produtos = json.loads((DADOS / "resumo.json").read_text(encoding="utf-8"))["produtos"]
pp = pd.read_csv(ENR / "pessoa_produto.csv.gz", dtype={"pessoa": str, "produto_id": str, "evidencias": str})
pp = pp[pp.produto_id.isin(produtos)].sort_values(["produto_id", "peso"], ascending=[True, False])
pp = pp.groupby("produto_id").head(POR_PRODUTO)
pp["ev"] = pp.evidencias.fillna("").str.split(";").str[:N_EVIDENCIAS]

pes = pd.read_csv(ENR / "pessoas.csv.gz", dtype=str).set_index("pessoa")
ev = pd.read_csv(ENR / "evidencias.csv.gz", dtype=str).fillna("").set_index("doc_uid")
TIPO = {"publicacao": "PUB", "projeto": "PRJ", "tecnologia": "TEC"}

saida = {"p": {}, "pp": {}, "ev": {}}
for r in pp.itertuples():
    if r.pessoa not in pes.index:
        continue
    p = pes.loc[r.pessoa]
    saida["p"][r.pessoa] = [p.nome, p.unidade if isinstance(p.unidade, str) else "", int(p.n_docs), int(p.ano_ultimo)]
    uids = [u for u in r.ev if u in ev.index]
    saida["pp"].setdefault(r.produto_id, []).append(
        [r.pessoa, int(r.n_docs), int(r.n_recentes), int(r.n_projetos_lider), int(r.n_tecnologias), float(r.peso), uids])
    for u in uids:
        e = ev.loc[u]
        saida["ev"][u] = [TIPO.get(e.tipo_doc, ""), e.titulo, e.ano, e.url]

(DADOS / "pessoas.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"pessoas.json: {len(saida['p'])} pessoas em {len(saida['pp'])} produtos, {len(saida['ev'])} evidências, "
      f"{(DADOS / 'pessoas.json').stat().st_size / 1e3:.0f} kB")
