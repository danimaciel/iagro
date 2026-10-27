# Estado do iAgro (piloto Embrapa Territorial)

Atualizado em 23/10/2026.

## No ar

- https://danimaciel.github.io/iagro/ com a exportação do Redape de **outubro de 2026** (`site/dados/resumo.json`:
  2.137 documentos — 2.054 publicações, 20 soluções, 63 projetos; 516 com produto principal e 1.006 com estado).
- Mudança de setembro para outubro (23/10): +11 publicações e +1 solução (Ambitec-TICs) novas no Redape;
  −3 projetos concluídos que saíram da própria exportação do Redape (PRJ 203075, 205554, 216177). O agente local
  usa a mesma base (`agente/base/`, regenerada em 23/10).
- Filtros e etiquetas de produto e estado (camadas do Observatório), janela "Sobre o iAgro", favicon e selo do
  topo comuns aos três iAgros (19/10).

## Rede iAgro (27/10/2026, em revisão)

- Nova página em `site/rede/` (https://danimaciel.github.io/iagro/rede/ depois do merge): perfil → kit inicial
  (15 publicações, 5 projetos, 5 soluções) e mapa das cadeias; lê `site/dados/` desta mesma página.
- Registro anônimo de uso numa planilha Google (`rede/registro/`), já implantado pela usuária; falta conferir de
  ponta a ponta com a página no ar. Detalhes em `rede/README.md`.

## Agente local (Google ADK + Ollama)

Avaliado com o gabarito: Qwen 2.5 7B citou o documento esperado em 19 de 20 perguntas da Territorial e
reconheceu 7 de 7 fora do tema; 2 a 4 minutos por resposta no processador (resultado documentado em
`documentacao/`).

## Pendências

- Próximas exportações: copiar os 3 CSVs do Redape para `Dados/`, `python agente/preparar_base.py --mes AAAA-MM`
  (~10 min), baixar o enriquecimento do mês e `python site/preparar_site.py`; o mês aparece sozinho na página.
- Levar a busca v2 (só significado, em dois passos) do iagro-embrapa para esta página.
- Agente: link inventado na resposta sobre o Gado de Leite; resposta sobre mudas de eucalipto a revisar.
