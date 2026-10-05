# iAgro

Demonstração de como uma base de dados da Embrapa (como a BDPA ou a Infoteca) pode ser reposicionada:
em vez de buscar por palavras do título, a pessoa pergunta do seu jeito e chega ao documento certo.

Piloto: **o que a Embrapa Territorial produziu e produz** (publicações, soluções tecnológicas e projetos),
com dados públicos do Redape. Não é um serviço oficial da Embrapa.

| Parte | O que é |
|---|---|
| `site/` | Página de busca por significado (GitHub Pages). Tudo roda no navegador: modelo multilingual-e5 + palavras (BM25). Dados gerados por `site/preparar_site.py` |
| `agente/` | Agente conversacional (Google ADK + modelo aberto local via Ollama) que responde só com a base e cita a fonte. Ver `agente/README.md` |
| `avaliacao/` | Gabarito de perguntas de teste |
| `documentacao/` | Documento de objetivo e método (docx) e seu gerador |

Para gerar a base: colocar as exportações do Redape em `Dados/` e rodar
`python agente/preparar_base.py` e depois `python site/preparar_site.py`.
