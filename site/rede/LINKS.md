# Rede iAgro: endereços diretos para produto e tema

Outras páginas podem abrir a Rede iAgro já num produto, ou num produto e num tema:

    https://danimaciel.github.io/iagro/rede/#p=<produto>&t=<tema>

- `p`: código do produto (ex.: `soja`, `cafe`, `bovinos`) ou o nome, sem acento (`Café` → `cafe` ou `Cafe`).
- `t` (opcional): código do tema (ex.: `T041`, Ferrugem-asiática da soja). Só vale se o tema estiver entre os
  temas do produto; se não estiver, a página abre só o produto.

Exemplos:

- https://danimaciel.github.io/iagro/rede/#p=soja&t=T041 (ferrugem-asiática da soja)
- https://danimaciel.github.io/iagro/rede/#p=tomate (tudo sobre tomate)

A página abre com o produto no centro da constelação, o tema escolhido destacado com as palavras-chave dele, a
lista de documentos (primeiro os da Embrapa Territorial, depois exemplos de toda a Embrapa, com link para todos
na busca do iAgro Embrapa) e as unidades que mais trabalham com o tema.

## Onde estão os códigos

Arquivo público, atualizado com a release mensal do Observatório de Pesquisa da Embrapa:
https://danimaciel.github.io/iagro/dados/rede.json

- `prod`: `{codigo_do_produto: [nome, categoria]}` (104 produtos, base IBGE PAM/PPM/PEVS)
- `temas`: `{codigo_do_tema: rótulo}` (temas do Observatório, BERTopic)
- `pt`: `{codigo_do_produto: [[tema, n_documentos, n_recentes, palavras-chave, exemplos, territorial], ...]}`,
  os até 12 temas de cada produto, do maior para o menor

Para ligar um tema de outra fonte (por exemplo, uma trilha de evento) à rede, basta escolher o produto e o
tema mais próximos nessa lista e montar o endereço.

## Registro

Quem chega por um desses endereços gera um evento anônimo `link` (produto, tema e o domínio da página de
origem), como os demais eventos da Rede iAgro (ver `rede/registro/LEIAME.md` na raiz do repositório).
