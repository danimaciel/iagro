"""iAgro: avaliação com o gabarito (avaliacao/gabarito_territorial.csv).

Para cada pergunta do gabarito verifica:
  - se a busca trouxe algum dos documentos esperados (erro de busca) e se o agente o citou (erro do modelo);
  - nas perguntas que a base não cobre (X), se o agente reconheceu que não sabe ou respondeu assim mesmo
    (risco de inventar, a conferir na leitura).
A conferência final da qualidade é humana: a planilha traz pergunta, resposta e documentos esperados lado a lado.

Uso (na pasta IAGRO):
  agente\\.venv\\Scripts\\python agente\\avaliar.py --so-busca     só a busca, sem o modelo (menos de 1 minuto)
  agente\\.venv\\Scripts\\python agente\\avaliar.py                agente completo (com o Ollama; cerca de 40 minutos)
  agente\\.venv\\Scripts\\python agente\\avaliar.py --modelo ollama_chat/gemma3:4b
Saídas: resultados/avaliacao_<modelo>.csv (parcial, retomável) e resultados/iagro_avaliacao_<modelo>.xlsx
"""
import argparse
import asyncio
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
RES = RAIZ / "resultados"
RES.mkdir(exist_ok=True)
sys.path.insert(0, str(AQUI))

ap = argparse.ArgumentParser()
ap.add_argument("--modelo", default=None, help="ex.: ollama_chat/qwen2.5:7b")
ap.add_argument("--so-busca", action="store_true", help="avalia só a busca, sem chamar o modelo")
ap.add_argument("--k", type=int, default=None, help="documentos entregues ao modelo (padrão: IAGRO_K ou 4)")
args = ap.parse_args()
if args.modelo:
    os.environ["IAGRO_MODELO"] = args.modelo
if args.k:
    os.environ["IAGRO_K"] = str(args.k)

gab = pd.read_csv(RAIZ / "avaliacao" / "gabarito_territorial.csv", dtype=str).fillna("")
esperados = lambda r: [c.strip() for c in r.docs_esperados.split(";") if c.strip()]
CODIGO = re.compile(r"\b(PUB|TEC|PRJ)\s*(\d+)")
NAO_SEI = re.compile(r"não encontrei|nao encontrei|não há informaç|não tenho informaç|não cobre", re.I)

# ------------------------------------------------------------ só a busca
if args.so_busca:
    from iagro.busca import buscar

    linhas = []
    for r in gab.itertuples():
        res = buscar(r.pergunta, k=10)
        cods = [d["codigo"] for d in res]
        esp = esperados(r)
        pos = [cods.index(c) + 1 for c in esp if c in cods]
        linhas.append({"id": r.id, "avaliacao": r.avaliacao, "pergunta": r.pergunta,
                       "primeira_posicao_esperada": min(pos) if pos else "",
                       "top4": " | ".join(f"{d['codigo']} {d['titulo'][:60]}" for d in res[:4]),
                       "semelhanca_1o": res[0]["semelhanca"]})
    df = pd.DataFrame(linhas)
    com = df[df.avaliacao != "X"]
    p = pd.to_numeric(com.primeira_posicao_esperada, errors="coerce")
    print(df[["id", "primeira_posicao_esperada", "semelhanca_1o", "top4"]].to_string(index=False))
    print(f"\nPerguntas com resposta na base: {len(com)} | esperado no top 1: {(p <= 1).sum()}"
          f" | top 4 (vai ao modelo): {(p <= 4).sum()} | top 10: {(p <= 10).sum()}")
    sx = df[df.avaliacao == "X"].semelhanca_1o
    print(f"Semelhança do 1º resultado: com resposta {com.semelhanca_1o.mean():.3f} | sem resposta {sx.mean():.3f}")
    df.to_csv(RES / "avaliacao_busca.csv", index=False, encoding="utf-8")
    sys.exit()

# ------------------------------------------------------------ agente completo
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from iagro.agent import MODELO, root_agent

nome = re.sub(r"[^\w.-]", "_", MODELO.split("/")[-1])
parcial = RES / f"avaliacao_{nome}.csv"
feitas = pd.read_csv(parcial, dtype=str) if parcial.exists() else pd.DataFrame(columns=["id"])
falta = gab[~gab.id.isin(feitas.id)]
print(f"modelo {MODELO} | perguntas {len(gab)} | já feitas {len(gab) - len(falta)}")

svc = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="iagro", session_service=svc)


async def perguntar(texto: str, sid: str):
    await svc.create_session(app_name="iagro", user_id="avaliacao", session_id=sid)
    msg = types.Content(role="user", parts=[types.Part(text=texto)])
    final = ""
    async for ev in runner.run_async(user_id="avaliacao", session_id=sid, new_message=msg):
        if ev.is_final_response() and ev.content and ev.content.parts:
            final = "".join(p.text or "" for p in ev.content.parts)
    ses = await svc.get_session(app_name="iagro", user_id="avaliacao", session_id=sid)
    return final, ses.state.get("docs_trazidos", [])


async def main():
    for i, r in enumerate(falta.itertuples(), 1):
        t0 = time.time()
        try:
            resp, trazidos = await perguntar(r.pergunta, f"{r.id}-{int(t0)}")
            erro = ""
        except Exception as ex:  # registra e segue
            resp, trazidos, erro = "", [], f"{type(ex).__name__}: {ex}"[:300]
        citados = sorted({f"{a} {n}" for a, n in CODIGO.findall(resp)})
        linha = pd.DataFrame([{
            "id": r.id, "pergunta": r.pergunta, "avaliacao_esperada": r.avaliacao,
            "docs_esperados": r.docs_esperados, "resposta_agente": resp,
            "docs_trazidos": ";".join(trazidos), "docs_citados": ";".join(citados),
            "disse_nao_encontrei": bool(NAO_SEI.search(resp)), "segundos": round(time.time() - t0, 1), "erro": erro,
        }])
        linha.to_csv(parcial, mode="a", header=not parcial.exists(), index=False, encoding="utf-8")
        print(f"[{i}/{len(falta)}] {r.id} -> citou {citados or '-'} | {linha.segundos[0]}s {erro}", flush=True)


if len(falta):
    asyncio.run(main())

# ------------------------------------------------------------ indicadores
res = pd.read_csv(parcial, dtype=str).fillna("")
res = res[res.id.isin(gab.id)].copy()
cruza = lambda a, b: bool(set(filter(None, a.split(";"))) & set(filter(None, b.split(";"))))
res["busca_trouxe"] = [cruza(e, t) for e, t in zip(res.docs_esperados, res.docs_trazidos)]
res["citou_esperado"] = [cruza(e, c) for e, c in zip(res.docs_esperados, res.docs_citados)]
res["nao_sei"] = res.disse_nao_encontrei == "True"
ind = []
for a, rot in (("T", "Base responde"), ("P", "Base responde em parte"), ("X", "Base não responde")):
    g = res[res.avaliacao_esperada == a]
    if not len(g):
        continue
    ind.append({"Grupo": rot, "Perguntas": len(g),
                "Busca trouxe um documento esperado": int(g.busca_trouxe.sum()) if a != "X" else "",
                "Citou um documento esperado": int(g.citou_esperado.sum()) if a != "X" else "",
                "Disse que não encontrou": int(g.nao_sei.sum()),
                "Respondeu mesmo assim (conferir se inventou)": int((~g.nao_sei).sum()) if a == "X" else "",
                "Tempo médio (s)": round(pd.to_numeric(g.segundos).mean(), 1)})
ind = pd.DataFrame(ind)
print(ind.to_string(index=False))
arq = RES / f"iagro_avaliacao_{nome}.xlsx"
with pd.ExcelWriter(arq, engine="openpyxl") as xw:
    pd.DataFrame([[f"Avaliação do iAgro (Embrapa Territorial). Modelo: {MODELO}. Perguntas: {len(res)}."],
                  ["Gabarito: avaliacao/gabarito_territorial.csv (inicial, a revisar com a equipe da Territorial)."],
                  ["Conferência humana na aba Respostas."]]).to_excel(xw, sheet_name="Leiame", index=False, header=False)
    ind.to_excel(xw, sheet_name="Indicadores", index=False)
    res.drop(columns=["nao_sei"]).to_excel(xw, sheet_name="Respostas", index=False)
print("salvo:", arq)
