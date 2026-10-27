"""Rede iAgro: gera site/dados/pessoas.json ("quem trabalha com isso") a partir do enriquecimento do Observatório.

Lê de enriquecimento/ (release pública "enriquecimento-AAAA-MM" de danimaciel/observatorio_embrapa, desde a que
traz pessoas.csv.gz, pessoa_produto.csv.gz e evidencias.csv.gz):
  gh release download enriquecimento-AAAA-MM --repo danimaciel/observatorio_embrapa -D enriquecimento --clobber
Cobre todos os produtos da taxonomia (a rede por produto vai além da base da Territorial).

Para cada produto, as 8 pessoas de toda a Embrapa com maior peso e as 3 de maior peso da Territorial (critério e salvaguardas no Observatório:
vínculos A/B/M, ao menos 3 documentos, 1 dos últimos 10 anos). Só nome e unidade, como nas publicações.
  site/dados/pessoas.json  {"p": {id: [nome, unidade, n_docs, ano_ultimo, da_territorial]},
                            "pp": {produto: [[id, n_docs, n_recentes, n_projetos_lider, n_tecnologias, peso, [doc_uid]]]},
                            "ev": {doc_uid: [tipo, titulo, ano, url]},
                            "t": {id: [tema]}}  (temas da pessoa, do maior peso para o menor, se houver pessoa_tema.csv.gz)
Rodar:  python site/rede/preparar_pessoas.py
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ENR = RAIZ / "enriquecimento"
DADOS = RAIZ / "site" / "dados"
POR_PRODUTO = 8
DA_UNIDADE = 3
UNIDADE = "territorial"
N_EVIDENCIAS = 3
TEMAS_POR_PESSOA = 10

if not (ENR / "pessoa_produto.csv.gz").exists():
    raise SystemExit("enriquecimento/ sem pessoa_produto.csv.gz: baixe uma release de enriquecimento com pessoas")

produtos = set(pd.read_csv(ENR / "produtos.csv", dtype=str).produto_id)
pp = pd.read_csv(ENR / "pessoa_produto.csv.gz", dtype={"pessoa": str, "produto_id": str, "evidencias": str})
pes = pd.read_csv(ENR / "pessoas.csv.gz", dtype=str).set_index("pessoa")
pp = pp[pp.produto_id.isin(produtos)].sort_values(["produto_id", "peso"], ascending=[True, False])
# as de maior peso em toda a Embrapa e, como o piloto é da Territorial, também as da unidade
da_unidade = pp.pessoa.map(pes.unidade_id) == UNIDADE
pp = pd.concat([pp.groupby("produto_id").head(POR_PRODUTO),
                pp[da_unidade].groupby("produto_id").head(DA_UNIDADE)]).drop_duplicates(["pessoa", "produto_id"])
pp["ev"] = pp.evidencias.fillna("").str.split(";").str[:N_EVIDENCIAS]

ev = pd.read_csv(ENR / "evidencias.csv.gz", dtype=str).fillna("").set_index("doc_uid")
TIPO = {"publicacao": "PUB", "projeto": "PRJ", "tecnologia": "TEC"}

saida = {"p": {}, "pp": {}, "ev": {}, "t": {}}
for r in pp.itertuples():
    if r.pessoa not in pes.index:
        continue
    p = pes.loc[r.pessoa]
    saida["p"][r.pessoa] = [p.nome, p.unidade if isinstance(p.unidade, str) else "", int(p.n_docs), int(p.ano_ultimo),
                            int(p.unidade_id == UNIDADE)]
    uids = [u for u in r.ev if u in ev.index]
    saida["pp"].setdefault(r.produto_id, []).append(
        [r.pessoa, int(r.n_docs), int(r.n_recentes), int(r.n_projetos_lider), int(r.n_tecnologias), float(r.peso), uids])
    for u in uids:
        e = ev.loc[u]
        saida["ev"][u] = [TIPO.get(e.tipo_doc, ""), e.titulo, e.ano, e.url]

if (ENR / "pessoa_tema.csv.gz").exists():
    pt = pd.read_csv(ENR / "pessoa_tema.csv.gz", usecols=["pessoa", "tema_id", "peso"], dtype={"pessoa": str, "tema_id": str})
    pt = pt[pt.pessoa.isin(saida["p"])].sort_values(["pessoa", "peso"], ascending=[True, False])
    saida["t"] = pt.groupby("pessoa").tema_id.apply(lambda s: list(s.head(TEMAS_POR_PESSOA))).to_dict()

(DADOS / "pessoas.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"pessoas.json: {len(saida['p'])} pessoas em {len(saida['pp'])} produtos, {len(saida['ev'])} evidências, "
      f"{(DADOS / 'pessoas.json').stat().st_size / 1e3:.0f} kB")
