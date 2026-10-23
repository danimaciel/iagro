# iAgro (piloto Embrapa Territorial): instruções para o Claude

Demonstração de como bases da Embrapa (BDPA, Infoteca) podem ser reposicionadas: a pessoa pergunta do seu
jeito e chega ao documento certo. Piloto: **o que a Embrapa Territorial produziu e produz** (publicações,
soluções tecnológicas, projetos). Página: https://danimaciel.github.io/iagro/ · repo público danimaciel/iagro.

**Comece lendo `estado.md`** e atualize-o ao fim de cada sessão. Contexto inicial e decisões de 05/10/2026 em
`PONTO_DE_PARTIDA.md` (local, fora do git).

## Família iAgro

Este é o piloto. Irmãos: `../iagro-embrapa` (busca em toda a Embrapa) e `../iagro-conversa` (conversa/RAG da
Territorial, com modo incorporado ao portal). Visão geral da família em `../iagro-conversa/CLAUDE.md`.
Produtos e localização vêm do Observatório de Pesquisa da Embrapa (release pública `enriquecimento-AAAA-MM`
em danimaciel/observatorio_embrapa); regras mudam lá.

## Partes

- `site/`: busca no navegador (híbrida antiga: BM25 + e5 com RRF; o iagro-embrapa já usa a busca v2 só por
  significado). Dados em `site/dados/` **versionados** (gerados por `site/preparar_site.py`, que lê
  `enriquecimento/`: `gh release download enriquecimento-AAAA-MM --repo danimaciel/observatorio_embrapa -D enriquecimento --clobber`).
  Push em `site/**` publica pelo `.github/workflows/pages.yml`.
- `agente/`: agente local com Google ADK + `LiteLlm(ollama_chat/qwen2.5:7b)`; a busca entra por
  `before_model_callback`. Base gerada por `agente/preparar_base.py` a partir de `Dados/`. Ver `agente/README.md`.
- `avaliacao/`: gabarito de 30 perguntas (20 da Territorial, 3 parciais, 7 fora do tema); `agente/avaliar.py`.
- `documentacao/`: objetivo e método em docx (`documentacao/gerar_documentacao.py`).

## Dados

`Dados/` é **local e privado** (fora do git): CSVs do Redape e `AutorPessoalEmbrapa.xls`, que tem dado pessoal
(nomes, matrículas) — uso interno ou ignorar; **nunca** entra na base do agente nem em nada público. Em outro
computador, baixe as exportações públicas do Redape para `Dados/` (o `pipeline/redape.py` do iagro-embrapa faz isso).

## Regras da usuária

- Escopo só da Embrapa Territorial; nada de SAF (do SAF/SAC veio só o método). Gestores públicos e técnicos
  também são público.
- Demonstração com dados públicos; não é serviço oficial e não usa a marca oficial da Embrapa.
- Sem custo de manutenção: nada que dependa de conta paga; modelos abertos.
- Números sempre com fonte e etapa; documentar sempre (`.md` + `.docx` para outras pessoas).
- Avaliações com Ollama: `--threads 6`, para o PC seguir usável. Nunca testar WebLLM no painel do Claude.
- Português do Brasil em textos, código e commits. Publicar (push) depois do OK da usuária.
