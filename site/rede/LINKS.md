# Rede iAgro: endereços diretos para produto e tema

Outras páginas podem abrir a Rede iAgro já num produto, ou num produto e num tema:

    https://danimaciel.github.io/iagro/rede/#p=<produto>&t=<tema>
    https://danimaciel.github.io/iagro/rede/#p=<produto>,<produto>
    https://danimaciel.github.io/iagro/rede/#q=<texto livre>

- `p`: código do produto (ex.: `soja`, `cafe`, `bovinos`) ou o nome, sem acento (`Café` → `cafe` ou `Cafe`).
  Vários produtos separados por vírgula: a rede abre no primeiro e mostra os demais como botões para trocar.
- `q` (opcional): texto livre, por exemplo o nome ou a descrição de um tema de evento. A página encontra nele os
  produtos (a mesma regra do campo "quem é você") e escolhe, no primeiro produto, o tema cujo rótulo e
  palavras-chave mais se parecem com o texto. Dispensa tabela de códigos; com `p` e `t` o resultado é exato.
- `t` (opcional): código do tema (ex.: `T041`, Ferrugem-asiática da soja). Só vale se o tema estiver entre os
  temas do produto; se não estiver, a página abre só o produto.

Exemplos:

- https://danimaciel.github.io/iagro/rede/#p=soja&t=T041 (ferrugem-asiática da soja)
- https://danimaciel.github.io/iagro/rede/#p=tomate (tudo sobre tomate)
- https://danimaciel.github.io/iagro/rede/#p=soja,milho (soja e milho, começando por soja)
- https://danimaciel.github.io/iagro/rede/#q=manejo%20de%20pragas%20na%20soja%20e%20no%20milho

Uma relação de muitos para muitos (um tema de evento com vários produtos, um produto em vários temas) cabe
num link por tema: liste os produtos em `p` ou descreva o tema em `q`.

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

Para ligar um tema de outra fonte (por exemplo, uma trilha de evento) à rede com precisão, escolha nessa lista
os produtos e o tema mais próximos e monte o endereço; para algo automático, use `q`. Temas sem produto
(crédito, mercado, energia) ficam melhor na busca do iAgro Embrapa: https://danimaciel.github.io/iagro-embrapa/#q=<texto>

## Registro

Quem chega por um desses endereços gera um evento anônimo `link` (produtos, tema, texto de `q` e o domínio da
página de origem), como os demais eventos da Rede iAgro (ver `rede/registro/LEIAME.md` na raiz do repositório).
