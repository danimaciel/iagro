# Rede iAgro

Página: https://danimaciel.github.io/iagro/rede/ (código em `site/rede/index.html`).

A pessoa conta quem é e o que procura; a página monta um kit inicial com 15 publicações, 5 projetos e 5
soluções tecnológicas da Embrapa Territorial e mostra como o perfil se liga às cadeias produtivas
(produtos do Observatório de Pesquisa da Embrapa, base IBGE PAM/PPM/PEVS), ao estado e ao bioma.

- **Dados:** os mesmos arquivos da busca do iAgro (`site/dados/documentos.json` e `resumo.json`). Quando a base
  do iAgro é atualizada, a Rede iAgro acompanha sem mudança de código.
- **Recomendação (protótipo):** palavras do perfil × título, palavras-chave e resumo (com peso pela raridade da
  palavra), mais bônus para produto, bioma, estado e tipo de ator; cotas por tipo e no máximo 4 publicações por
  produto. Próxima etapa: trocar pela busca por significado (multilingual-e5) que o iAgro já usa.
- **Perfil:** fica só no navegador (`localStorage`): perfis salvos com nome, itens salvos. Os três perfis que a
  página traz são exemplos.
- **Registro de uso:** anônimo, numa planilha Google via Apps Script (`rede/registro/`). Só liga na página
  publicada (`*.github.io`), com botão "Não registrar o meu uso".
- **Desenho e decisões:** documento "Rede Agro: viabilidade e arquitetura leve" (Claude Docs, 27/10/2026).
