# iAgro: Embrapa Territorial

Protótipo de assistente de IA sobre **o que a Embrapa Territorial produziu e produz**:
suas publicações, soluções tecnológicas e projetos. Responde **somente** com essa base e sempre cita a fonte.
Não é um assistente agronômico geral: perguntas fora da produção da Territorial recebem "não encontrei".

Piloto da Embrapa Territorial; o mesmo código serve depois para as outras unidades (`--unidade`).

| Peça | O que é |
|---|---|
| Corpo | [Google ADK](https://google.github.io/adk-docs/) (Agent Development Kit) |
| Cérebro | Modelo aberto local servido pelo [Ollama](https://ollama.com): Qwen 2.5 7B (padrão) ou Gemma 3 4B. Gratuito, nada sai do computador |
| Mãos | Busca automática antes de cada resposta (modelo semântico multilingual-e5-base + palavras, fusão por posição); os 4 documentos mais próximos vão para o modelo |
| Biblioteca | `base/documentos.json` e `base/documentos_e5.npy`, gerados por `preparar_base.py` a partir das exportações do Redape em `Dados/` |

Base do piloto (exportação de setembro de 2026): 2.043 publicações, 19 soluções tecnológicas e 66 projetos,
com título e resumo (os PDFs não são usados). `Dados/AutorPessoalEmbrapa.xls` tem dado pessoal e não é lido.

## Instalação (uma vez, na pasta IAGRO)

1. Ollama instalado e os modelos baixados: `ollama pull qwen2.5:7b` e `ollama pull gemma3:4b`.
2. Ambiente Python (reaproveita o torch e o sentence-transformers já instalados):
   ```
   python -m venv --system-site-packages agente\.venv
   agente\.venv\Scripts\pip install -r agente\requirements.txt
   ```
3. Copiar `agente\iagro\.env.example` para `agente\iagro\.env`.
4. Preparar a base (cerca de 10 minutos): `python agente\preparar_base.py`

## Uso

- **Conversar**: dentro da pasta `agente`, rodar `.venv\Scripts\adk web`, abrir http://localhost:8000 e escolher `iagro`.
  A página só existe no seu computador.
- **Avaliar só a busca** (menos de 1 minuto): `agente\.venv\Scripts\python agente\avaliar.py --so-busca`
- **Avaliar o agente** com o gabarito (`avaliacao/gabarito_territorial.csv`, cerca de 40 minutos):
  `agente\.venv\Scripts\python agente\avaliar.py`. Para comparar modelos: `--modelo ollama_chat/gemma3:4b`.
  O resultado vai para `resultados/iagro_avaliacao_<modelo>.xlsx`.

## Regras do agente

Responde só com o que a busca trouxe; diz "não encontrei" quando a base não cobre; linguagem simples, até 150 palavras;
diz o tipo de documento e o ano (e se o projeto está concluído ou em execução); informa onde encontrar a solução
tecnológica; encaminha cursos, visitas e contato para o SAC da Embrapa; termina com a fonte (código e link: PUB, TEC ou PRJ).
Público: produtores rurais, extensionistas, estudantes, gestores públicos e técnicos.

## Limites

Protótipo para a equipe. Não é serviço público: precisa do computador ligado com o Ollama.
Nada é publicado sem autorização da coordenação.
