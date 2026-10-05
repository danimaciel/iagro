# -*- coding: utf-8 -*-
"""Gera o documento de objetivo e método do iAgro (Embrapa Territorial).

Atualize este arquivo a cada nova decisão ou etapa concluída e rode (na pasta IAGRO):
    python documentacao/gerar_documentacao.py
Os resultados da avaliação são lidos de resultados/ quando existem.
"""
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

VERSAO = "0.1"
DATA = "05/10/2026"
RAIZ = Path(__file__).resolve().parents[1]
SAIDA = Path(__file__).parent / "iAgro_Territorial_metodo_e_objetivo.docx"

VERDE = RGBColor(0x2E, 0x6B, 0x3A)
FUNDO_CABECALHO = "DCE9DD"

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
for m in ("left_margin", "right_margin"):
    setattr(sec, m, Cm(2.5))
sec.top_margin = sec.bottom_margin = Cm(2.2)

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(6)
for nome, tam in (("Heading 1", 15), ("Heading 2", 12.5), ("Title", 22)):
    st = doc.styles[nome]
    st.font.name = "Calibri"
    st.font.size = Pt(tam)
    st.font.color.rgb = VERDE
    st.font.bold = True


def h1(t):
    doc.add_heading(t, level=1)


def h2(t):
    doc.add_heading(t, level=2)


def p(t, negrito_ini=None, italico=False):
    par = doc.add_paragraph()
    if negrito_ini:
        par.add_run(negrito_ini).bold = True
    r = par.add_run(t)
    r.italic = italico
    return par


def bullets(itens, estilo="List Bullet"):
    for it in itens:
        if isinstance(it, tuple):
            par = doc.add_paragraph(style=estilo)
            par.add_run(it[0]).bold = True
            par.add_run(it[1])
        else:
            doc.add_paragraph(it, style=estilo)


def sombrear(celula, cor):
    tcPr = celula._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    tcPr.append(shd)


def tabela(cabecalho, linhas, larguras):
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, txt in enumerate(cabecalho):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(txt))
        r.bold = True
        r.font.size = Pt(10)
        sombrear(c, FUNDO_CABECALHO)
    for linha in linhas:
        cells = t.add_row().cells
        for i, txt in enumerate(linha):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(txt)).font.size = Pt(10)
    for row in t.rows:
        for i, w in enumerate(larguras):
            row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


# ---------------------------------------------------------------- capa
doc.add_paragraph(style="Title").add_run("iAgro: assistente sobre a produção da Embrapa Territorial")
p("Documento de objetivo e método", italico=True)
p(f"Versão {VERSAO} · {DATA}", italico=True)
p("Análise de dados e desenvolvimento: Daniela Maciel.")
p("Documento vivo: é atualizado a cada decisão ou etapa concluída. As mudanças ficam no "
  "Registro de decisões (seção 9).", italico=True)

# ---------------------------------------------------------------- 1
h1("1. Objetivo e escopo")
p("O iAgro é um assistente de inteligência artificial que responde dúvidas sobre o que a Embrapa Territorial "
  "produziu e produz: suas publicações, soluções tecnológicas e projetos. Ele responde somente com essa base "
  "e sempre indica a fonte, com link para o Portal Embrapa.")
p("Escopo: ", negrito_ini=None)
bullets([
    ("O tema é a produção da Embrapa Territorial. ", "O iAgro não é um assistente agronômico geral. "
     "Perguntas fora dessa produção (por exemplo, dose de vermífugo ou enxertia) recebem \"não encontrei\" "
     "e são encaminhadas à busca de publicações da Embrapa ou ao SAC."),
    ("Piloto na Embrapa Territorial (CNPM). ", "O mesmo código depois se aplica às demais unidades. "
     "Atenção: CNPM é a Embrapa Territorial; a Embrapa Meio Ambiente é o CNPMA."),
    ("Público: ", "produtores rurais, extensionistas, estudantes, gestores públicos e técnicos."),
    ("Sem custo de manutenção: ", "modelo de linguagem aberto, rodando no próprio computador (Ollama). "
     "Nada depende de conta paga e nenhuma pergunta sai da máquina."),
])

# ---------------------------------------------------------------- 2
h1("2. Fontes de dados")
tabela(
    ["Fonte", "Conteúdo usado", "Embrapa Territorial"],
    [
        ["Publicações da Embrapa (Redape, set/2026)", "Título, resumo, ano, tipo, autores, palavras-chave, página no Portal",
         "2.043 publicações (1980–2026); 1.696 com resumo"],
        ["Soluções tecnológicas (Redape, set/2026)", "Nome, descrição, tipo, bioma, onde encontrar, página no Portal",
         "19 soluções"],
        ["Projetos (Redape, set/2026)", "Título, resumo, período, situação, página no Portal", "66 projetos (60 concluídos, 6 em execução)"],
    ],
    [4.6, 6.4, 5.0],
)
p("A unidade é identificada pelas colunas Unidade, Unidade responsável e Unidade líder. Só o título e o resumo "
  "são usados; o texto dos PDFs não é baixado.")

# ---------------------------------------------------------------- 3
h1("3. Cuidados com dados pessoais (LGPD)")
bullets([
    "O arquivo AutorPessoalEmbrapa.xls tem nomes e matrículas. Ele não é lido pelo agente e não entra em nada público.",
    "Autores e líderes de projeto aparecem apenas como já constam nas páginas públicas do Portal Embrapa.",
    "Nada é publicado sem autorização da coordenação.",
])

# ---------------------------------------------------------------- 4
h1("4. Método")
h2("4.1 Base de conhecimento")
bullets([
    "Os três tipos de documento são reunidos num formato único, cada um com um código: PUB (publicação), "
    "TEC (solução tecnológica) e PRJ (projeto), seguido do ID do Portal. É esse código que o agente cita.",
    "Cada documento é representado por um vetor do modelo multilingual-e5-base (título + início do resumo). "
    "É o mesmo modelo usado no Observatório de P&D da Embrapa.",
])
h2("4.2 Busca")
bullets([
    "Busca híbrida: similaridade semântica (e5) combinada com busca por palavras (TF-IDF), "
    "com fusão pela posição de cada documento nas duas listas (Reciprocal Rank Fusion).",
    "A busca roda automaticamente antes de cada resposta. Os 4 documentos mais próximos, com o resumo cortado "
    "em cerca de 900 caracteres, são entregues ao modelo. Modelos pequenos às vezes deixam de chamar ferramentas; "
    "por isso a busca não depende da decisão do modelo.",
])
h2("4.3 Página de busca online (GitHub Pages)")
bullets([
    "Endereço: https://danimaciel.github.io/iagro/ (código em https://github.com/danimaciel/iagro).",
    "Página estática: os documentos e os vetores (int8) vão junto com a página; a pergunta é transformada em vetor "
    "no próprio navegador (transformers.js, multilingual-e5-base quantizado, cerca de 110 MB na primeira visita) e "
    "combinada com busca por palavras (BM25) pela mesma fusão por posição. Nenhuma pergunta vai para servidor; custo zero.",
    "Mostra os documentos mais próximos com tipo, ano, resumo e link para o Portal Embrapa. Quando a semelhança do "
    "primeiro resultado é baixa, avisa que talvez a Territorial não tenha trabalho sobre o assunto.",
    "Teste com o gabarito na página publicada localmente: documento esperado em 1º lugar em 21 de 23 perguntas com "
    "resposta (2º lugar nas outras duas); aviso de relação fraca em 6 das 7 perguntas fora do tema e em nenhuma das 23.",
    "Atualizar: rodar agente/preparar_base.py e site/preparar_site.py e enviar ao GitHub; a publicação é automática.",
])
h2("4.4 Agente")
bullets([
    "Corpo: Google ADK (Agent Development Kit). Cérebro: Qwen 2.5 7B pelo Ollama (alternativa: Gemma 3 4B).",
    "Regras principais: responder só com os resultados da busca; verificar se eles tratam mesmo do assunto; "
    "dizer \"não encontrei\" quando não cobrem; linguagem simples, até 150 palavras; informar tipo de documento e ano "
    "(e avisar quando for antigo); dizer se o projeto está concluído ou em execução; indicar onde encontrar a solução "
    "tecnológica; encaminhar cursos, visitas e contatos ao SAC; terminar com a linha \"Fonte:\" (código e link).",
    "O agente sabe que Embrapa Monitoramento por Satélite e Embrapa Gestão Territorial são nomes antigos da unidade.",
])

# ---------------------------------------------------------------- 5
h1("5. Avaliação")
p("Gabarito inicial com 30 perguntas, escrito a partir da leitura da base (avaliacao/gabarito_territorial.csv), "
  "a ser revisado e completado pela equipe da Embrapa Territorial:")
bullets([
    "20 perguntas que a base responde, cada uma com os documentos aceitos como resposta certa;",
    "3 perguntas que a base responde só em parte (por exemplo, pede dose ou custo que os documentos não trazem);",
    "7 perguntas fora da produção da Territorial, para verificar se o agente reconhece que não sabe "
    "(inclui uma armadilha: broca-do-café, quando a base só tem café no tema carbono).",
])
p("Indicadores: a busca trouxe um documento esperado? O agente o citou? Nas perguntas sem resposta, disse que "
  "não encontrou ou respondeu assim mesmo? A conferência final é humana, na planilha de respostas.")

# ---------------------------------------------------------------- 6
h1("6. Resultados")
busca = RAIZ / "resultados" / "avaliacao_busca.csv"
if busca.exists():
    b = pd.read_csv(busca)
    com = b[b.avaliacao != "X"]
    pos = pd.to_numeric(com.primeira_posicao_esperada, errors="coerce")
    h2("6.1 Busca")
    tabela(["Indicador", "Resultado"], [
        ["Perguntas com resposta na base (total ou em parte)", len(com)],
        ["Documento esperado em 1º lugar", int((pos <= 1).sum())],
        ["Documento esperado entre os 4 entregues ao modelo", int((pos <= 4).sum())],
        ["Semelhança média do 1º resultado: com resposta × sem resposta",
         f"{com.semelhanca_1o.mean():.3f} × {b[b.avaliacao == 'X'].semelhanca_1o.mean():.3f}"],
    ], [10.0, 6.0])
    p("A diferença de semelhança entre perguntas com e sem resposta é pequena; por isso não se usa um limite de "
      "semelhança para decidir que a base não responde. Essa decisão fica com o modelo (regra 2).")
    p("Na primeira rodada, várias \"falhas\" eram documentos certos que o gabarito não listava (por exemplo, "
      "publicações sobre o MonitoraOeste e o Atlas Escolar). Eles foram conferidos e acrescentados ao gabarito.")
for xlsx in sorted((RAIZ / "resultados").glob("iagro_avaliacao_*.xlsx")):
    ind = pd.read_excel(xlsx, sheet_name="Indicadores").fillna("")
    h2(f"6.2 Agente: {xlsx.stem.replace('iagro_avaliacao_', '')}")
    tabela(list(ind.columns), ind.values.tolist(), [3.0] + [13.0 / (len(ind.columns) - 1)] * (len(ind.columns) - 1))

# ---------------------------------------------------------------- 7
h1("7. Estrutura de arquivos")
tabela(
    ["Pasta / arquivo", "Conteúdo", "Acesso"],
    [
        ["Dados/", "Exportações do Redape, IBGE e AutorPessoalEmbrapa.xls", "Uso interno (o .xls tem dado pessoal)"],
        ["agente/preparar_base.py", "Monta a base da unidade (documentos.json e vetores)", "—"],
        ["agente/iagro/", "Agente (agent.py), busca (busca.py), configuração (.env)", "—"],
        ["agente/avaliar.py", "Avaliação da busca e do agente com o gabarito", "—"],
        ["avaliacao/gabarito_territorial.csv", "Perguntas de teste e documentos esperados", "—"],
        ["resultados/", "Resultados da avaliação", "Uso interno"],
        ["documentacao/", "Este documento e seu gerador", "—"],
    ],
    [5.0, 7.4, 3.6],
)

# ---------------------------------------------------------------- 8
h1("8. Próximos passos")
bullets([
    "Revisão do gabarito e das respostas pela equipe da Embrapa Territorial.",
    "Ajustar a instrução do agente conforme os erros encontrados na avaliação.",
    "Comparar Qwen 2.5 7B e Gemma 3 4B (qualidade e tempo de resposta).",
    "Expandir para outras unidades com o mesmo código (preparar_base.py --unidade).",
    "Definir, com a coordenação, se e como o assistente será oferecido fora da equipe.",
])

# ---------------------------------------------------------------- 9
h1("9. Registro de decisões")
tabela(
    ["Data", "Decisão"],
    [
        ["05/10/2026", "iAgro é projeto separado do SAF/SAC. Do SAF/SAC vem só o método técnico (ADK, busca híbrida, avaliação com gabarito), não o conteúdo."],
        ["05/10/2026", "Escopo: somente o que a Embrapa Territorial produziu e produz (publicações, soluções tecnológicas e projetos). Não é assistente agronômico geral."],
        ["05/10/2026", "Piloto na Embrapa Territorial; depois todas as unidades com o mesmo código."],
        ["05/10/2026", "Sem custo de manutenção: modelo aberto e local via Ollama."],
        ["05/10/2026", "Público: produtores rurais, extensionistas, estudantes, gestores públicos e técnicos."],
        ["05/10/2026", "Base única com soluções, projetos e publicações desde o início."],
        ["05/10/2026", "Usar só título e resumo; os PDFs não são baixados."],
        ["05/10/2026", "Gabarito inicial escrito a partir da base, a ser revisado pela equipe da Territorial."],
        ["05/10/2026", "AutorPessoalEmbrapa.xls (dado pessoal) não entra no agente nem em nada público. Nada é publicado sem autorização da coordenação."],
        ["05/10/2026", "Versão online: página estática de busca por significado no GitHub Pages (https://danimaciel.github.io/iagro/), sem modelo generativo; tudo roda no navegador. Liberada porque todo o conjunto é público. Propósito: demonstrar como bases como a BDPA e a Infoteca podem ser reposicionadas; a página diz que não é serviço oficial da Embrapa."],
    ],
    [2.6, 13.4],
)

doc.save(SAIDA)
print("salvo:", SAIDA)
