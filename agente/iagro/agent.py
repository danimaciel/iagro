"""iAgro: assistente sobre publicações, soluções tecnológicas e projetos da Embrapa.

Piloto: Embrapa Territorial. Corpo: Google ADK. Cérebro: modelo aberto local via Ollama (Qwen ou Gemma), sem custo.
O modelo é definido em agente/iagro/.env (IAGRO_MODELO); ver .env.example.

A busca roda sempre, antes do modelo responder (callback), em vez de ser uma ferramenta que o
modelo decide chamar: modelos pequenos às vezes pulam a ferramenta, e assim a resposta sai numa
única etapa, mais rápida. Os códigos trazidos ficam no estado da sessão ("docs_trazidos").
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .busca import buscar

load_dotenv(Path(__file__).with_name(".env"))
MODELO = os.getenv("IAGRO_MODELO", "ollama_chat/qwen2.5:7b")
K = int(os.getenv("IAGRO_K", "4"))
MAX_TEXTO = 900  # caracteres de cada resumo enviados ao modelo


def _ultima_pergunta(llm_request) -> str:
    for c in reversed(llm_request.contents or []):
        if c.role == "user" and c.parts:
            texto = " ".join(p.text for p in c.parts if getattr(p, "text", None))
            if texto.strip():
                return texto.strip()
    return ""


def _cortar(t: str) -> str:
    return t if len(t) <= MAX_TEXTO else t[:MAX_TEXTO].rsplit(" ", 1)[0] + "…"


def _formatar(res: list[dict]) -> str:
    blocos = []
    for r in res:
        linhas = [f"[{r['codigo']}] {r['tipo_doc']} ({r['detalhe']}; ano {r['ano'] or 'não informado'})",
                  f"Título: {r['titulo']}",
                  f"Resumo: {_cortar(r['texto'])}" if r["texto"] else "Resumo: não disponível (só o título)"]
        if r.get("onde_encontrar"):
            linhas.append(f"Onde encontrar: {r['onde_encontrar']}")
        if r.get("bioma"):
            linhas.append(f"Bioma: {r['bioma']}")
        linhas.append(f"Link: {r['link']}")
        blocos.append("\n".join(linhas))
    return "\n\n".join(blocos)


def injetar_busca(callback_context, llm_request):
    """Antes de cada resposta, busca os documentos mais próximos da última pergunta e os entrega ao modelo."""
    pergunta = _ultima_pergunta(llm_request)
    if not pergunta:
        return None
    res = buscar(pergunta, k=K)
    callback_context.state["docs_trazidos"] = [r["codigo"] for r in res]
    llm_request.append_instructions([
        "RESULTADOS DA BUSCA NA BASE (use somente estes para responder):\n\n" + _formatar(res)])
    return None


INSTRUCAO = """Você é o iAgro, assistente sobre o que a Embrapa Territorial produziu e produz: suas publicações,
soluções tecnológicas e projetos. A Embrapa Territorial é a unidade da Embrapa em Campinas/SP que trabalha com mapas,
satélites, geotecnologias e inteligência territorial (nomes antigos: Embrapa Monitoramento por Satélite e
Embrapa Gestão Territorial). Seu tema é somente essa produção; não é um assistente agronômico geral.
Atende produtores rurais, extensionistas, estudantes, gestores públicos e técnicos.
A cada pergunta você recebe, no fim destas instruções, os RESULTADOS DA BUSCA nessa base.

Regras:
1. Responda SOMENTE com o que está nos resultados da busca. Não use conhecimento próprio para números,
   datas, locais, nomes de sistemas ou recomendações.
2. Antes de responder, verifique se algum resultado trata do assunto da pergunta. Semelhança de palavras não basta:
   se a pessoa pergunta sobre uma cultura, região, praga ou ferramenta e nenhum resultado fala dela, a base não responde.
3. Se nenhum resultado responde, diga: "Não encontrei esse assunto nas publicações, soluções tecnológicas e projetos
   da Embrapa Territorial." Depois sugira a busca de publicações da Embrapa (https://www.embrapa.br/busca-de-publicacoes)
   ou o SAC da Embrapa (https://www.embrapa.br/fale-conosco/sac). Não indique outras instituições.
4. Se os resultados respondem só em parte, diga o que a base explica e o que ela não cobre.
5. Use linguagem simples e frases curtas, em até 150 palavras. Explique qualquer termo técnico
   (por exemplo: sensoriamento remoto, WebGIS, geotecnologia).
6. Diga que tipo de documento é (publicação, solução tecnológica ou projeto) e o ano. Se o documento for antigo,
   avise que a informação pode estar desatualizada. Se for projeto, diga se está concluído ou em execução.
7. Se a pessoa quer usar uma solução tecnológica, informe o "Onde encontrar" quando ele vier nos resultados.
8. Pedidos de cursos, visitas, consultoria ou contato com pesquisadores não são temas da base: indique o SAC da Embrapa.
9. Termine sempre com uma linha "Fonte:" com o código e o link de cada documento que você usou,
   no formato "PUB 123 - link" (ou TEC, PRJ). Se não usou nenhum, escreva "Fonte: nenhuma".
Responda sempre em português do Brasil."""

root_agent = Agent(
    name="iagro",
    model=LiteLlm(model=MODELO),
    description="Responde dúvidas usando publicações, soluções tecnológicas e projetos da Embrapa Territorial.",
    instruction=INSTRUCAO,
    before_model_callback=injetar_busca,
)
