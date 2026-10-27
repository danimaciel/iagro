"""Rede iAgro: gera site/dados/rede.json (rede por produto) a partir do enriquecimento do Observatório.

Lê de enriquecimento/ (release pública "enriquecimento-AAAA-MM" de danimaciel/observatorio_embrapa, desde a que
traz rede_produto_tema.csv.gz, rede_vizinhos.csv.gz e documentos_rede.csv.gz):
  gh release download enriquecimento-AAAA-MM --repo danimaciel/observatorio_embrapa -D enriquecimento --clobber
e de site/dados/documentos.json os documentos da base da Territorial (o piloto), para destacá-los.

A rede cobre toda a Embrapa: para cada produto, os temas em que ele aparece (com palavras-chave típicas e documentos
de exemplo) e os produtos vizinhos (mais documentos em comum). Os documentos da Territorial de cada par produto × tema
vêm do próprio enriquecimento (produto principal e tema do documento).
  site/dados/rede.json  {"prod": {produto: [nome, categoria]},
                         "temas": {tema: rotulo},
                         "pt": {produto: [[tema, n_docs, n_recentes, [[palavra, n]], [doc_uid], [codigo_territorial]]]},
                         "viz": {produto: [[vizinho, n]]},
                         "docs": {doc_uid: [tipo, titulo, ano, url]}}
Rodar depois de site/preparar_site.py:  python site/rede/preparar_rede.py [pasta_com_os_arquivos_da_rede]
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ENR = RAIZ / "enriquecimento"
REDE = Path(sys.argv[1]) if len(sys.argv) > 1 else ENR
DADOS = RAIZ / "site" / "dados"
DA_UNIDADE = 6  # documentos da Territorial por par produto × tema

if not (REDE / "rede_produto_tema.csv.gz").exists():
    raise SystemExit(f"{REDE} sem rede_produto_tema.csv.gz: baixe uma release de enriquecimento com a rede")

tax = pd.read_csv(ENR / "produtos.csv", dtype=str).fillna("")
temas = pd.read_csv(ENR / "temas.csv", dtype=str).set_index("tema_id").rotulo
pt = pd.read_csv(REDE / "rede_produto_tema.csv.gz", dtype={"palavras": str, "docs": str}).fillna({"palavras": "", "docs": ""})
viz = pd.read_csv(REDE / "rede_vizinhos.csv.gz", dtype=str)
dr = pd.read_csv(REDE / "documentos_rede.csv.gz", dtype=str).fillna("")

# documentos da Territorial, ligados ao enriquecimento pelo identificador do Redape (como em site/preparar_site.py)
itens = json.loads((DADOS / "documentos.json").read_text(encoding="utf-8"))
reg = pd.read_csv(ENR / "registro_obra.csv.gz", dtype=str)
obra = dict(zip(reg.registro.str[2:], reg.obra_id))


def uid(cod):
    t, n = cod.split()
    return obra.get(n, "OB:" + n) if t == "PUB" else ("P:" if t == "PRJ" else "T:") + n


cod_uid = {d["c"]: uid(d["c"]) for d in itens}
ano = {d["c"]: str(d.get("a") or "") for d in itens}
e = pd.read_csv(ENR / "enriquecimento.csv.gz", dtype=str, usecols=["doc_uid", "produtos", "tema"]).fillna("")
e = e[e.doc_uid.isin(set(cod_uid.values())) & (e.tema != "")]
uid_cod = {}
for c, u in cod_uid.items():
    uid_cod.setdefault(u, []).append(c)
terr = {}
for r in e.itertuples():
    for p in filter(None, r.produtos.split(";")):
        terr.setdefault((p, r.tema), []).extend(uid_cod[r.doc_uid])


def sem_acento(t):
    return unicodedata.normalize("NFD", str(t)).encode("ascii", "ignore").decode().lower().strip()


# palavras-chave que só repetem o produto (nome, termos de busca, nome científico) não dizem nada no mapa dele
proprios = {}
for r in tax.itertuples():
    termos = [r.produto, r.cientifico.replace("; ", "|"), r.termos]
    proprios[r.produto_id] = [re.sub(r"\s*\(.*?\)", "", sem_acento(t)) for t in "|".join(termos).split("|") if t.strip()]


def do_produto(p, w):
    w = sem_acento(w)
    return any(w.startswith(t[:-1]) if t.endswith("*") else w == t or w.rstrip("s") == t.rstrip("s") for t in proprios.get(p, []))


GENERICAS = {"brasil", "brazil", "pesquisa", "embrapa"}


def palavras(p, s):
    ws = [[w.rsplit(":", 1)[0], int(w.rsplit(":", 1)[1])] for w in s.split(";") if ":" in w]
    return [w for w in ws if not do_produto(p, w[0]) and sem_acento(w[0]) not in GENERICAS]


# palavra presente em metade ou mais dos temas de um produto (com 4 temas ou mais) identifica o produto
# (sinônimo em inglês, outro nome científico), não o tema: sai também
pt["lista"] = [palavras(p, s) for p, s in zip(pt.produto_id, pt.palavras)]
de_produto = {}
for p, g in pt.groupby("produto_id"):
    if len(g) >= 4:
        conta = pd.Series([sem_acento(w) for ws in g.lista for w, _ in ws]).value_counts()
        de_produto[p] = set(conta[conta >= len(g) / 2].index)
pt["lista"] = [[w for w in ws if sem_acento(w[0]) not in de_produto.get(p, ())][:6] for p, ws in zip(pt.produto_id, pt.lista)]


saida = {"prod": {r.produto_id: [r.produto, r.categoria_ampla] for r in tax.itertuples()}, "temas": {}, "pt": {}, "viz": {}}
usados = set()
for r in pt.sort_values(["produto_id", "n_docs"], ascending=[True, False]).itertuples():
    if r.produto_id not in saida["prod"]:
        continue
    docs = [d for d in r.docs.split(";") if d]
    t = sorted(set(terr.get((r.produto_id, r.tema_id), [])), key=lambda c: ano[c], reverse=True)[:DA_UNIDADE]
    saida["pt"].setdefault(r.produto_id, []).append([r.tema_id, int(r.n_docs), int(r.n_recentes), r.lista, docs, t])
    saida["temas"][r.tema_id] = temas.get(r.tema_id, r.tema_id)
    usados.update(docs)
for r in viz.itertuples():
    if r.produto_id in saida["prod"] and r.vizinho in saida["prod"]:
        saida["viz"].setdefault(r.produto_id, []).append([r.vizinho, int(r.n)])
dr = dr[dr.doc_uid.isin(usados)]
saida["docs"] = {r.doc_uid: [r.tipo_doc, r.titulo, int(float(r.ano)) if r.ano else None, r.url] for r in dr.itertuples()}

(DADOS / "rede.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
n_terr = sum(len(x[5]) for v in saida["pt"].values() for x in v)
print(f"rede.json: {len(saida['pt'])} produtos com temas, {sum(map(len, saida['pt'].values()))} pares produto × tema, "
      f"{len(saida['docs'])} documentos de exemplo, {n_terr} ligações a documentos da Territorial, "
      f"{(DADOS / 'rede.json').stat().st_size / 1024:.0f} kB")
