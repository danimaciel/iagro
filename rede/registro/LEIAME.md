# Registro de uso da Rede iAgro

Versão de 27/10/2026. Registro mínimo e anônimo para saber quem chega (tipo de ator, bioma, estado, cadeias),
o que procura e se o kit acerta (itens abertos e salvos, e em que posição estavam). Adaptado do registro do
iAgro Conversa (`danimaciel/iagro-conversa`, `docs/REGISTRO.md`); o mesmo molde serve para os outros iAgro.

## Como funciona

A página é estática e não grava nada no servidor. Cada evento vai, por `fetch`, para um script do Google
(Apps Script), que acrescenta uma linha numa planilha da responsável pelo projeto. Se o envio falhar, a página
segue normalmente.

| Evento | Quando | O que vai |
|---|---|---|
| `perfil` | ao clicar em "Montar meu kit" | tipo de ator, bioma, estado, cadeias encontradas, texto do perfil (sem e-mail, CPF e telefone, até 500 caracteres) |
| `abrir` | ao abrir um item do kit | código do documento, posição na lista, aba e filtro em uso |
| `salvar` | ao salvar ou tirar dos salvos | código do documento, sim ou não, aba |
| `filtro` | ao escolher uma cadeia ou produto no mapa | cadeia ou produto |

Toda linha leva também `visita` (código aleatório criado a cada visita, só para ligar os eventos dela) e o
nome interno do perfil salvo em uso.

**Não vai:** endereço IP (o Apps Script não o entrega ao script), cookies, identificador de pessoa ou aparelho.

**Para quem usa:** um aviso sob o formulário com o botão **Não registrar o meu uso** (a escolha fica no
navegador). O aviso só aparece quando o registro está ligado.

**Importante:** o registro só funciona com a página publicada num endereço próprio (por exemplo GitHub Pages).
Dentro de um Artifact do Claude, a página não consegue enviar nada para fora.

## Guarda e uso (LGPD)

- A planilha é dado bruto e restrito: fica na conta da responsável, sem compartilhamento público.
- Prazo: 12 meses; a função `apagarAntigos` apaga o que passar disso (acionador mensal).
- Podem ser divulgados resumos agregados (perfis mais comuns, cadeias mais procuradas, posição média dos itens
  abertos), nunca os textos de perfil um a um.
- Base legal sugerida (a referendar com o encarregado de dados se o projeto virar serviço): legítimo interesse,
  para melhoria do serviço, com aviso e opção de recusa na própria página.

## Instalação (uma vez, cerca de 10 minutos)

1. Em https://sheets.new, crie uma planilha, por exemplo **Rede iAgro · registro**.
2. Menu **Extensões > Apps Script**. Apague o conteúdo de `Código.gs` e cole `apps_script.gs` desta pasta. Salve.
3. Teste: escolha a função `testar` e clique em **Executar**. Na primeira vez o Google pede autorização
   (**Revisar permissões** > sua conta > **Avançado** > **Acessar (não seguro)** > **Permitir**; o aviso aparece
   porque o script é seu e não foi verificado pelo Google). Na planilha deve surgir a aba `registro` com uma linha
   "teste do registro". Pode apagá-la.
4. **Implantar > Nova implantação** > engrenagem > **App da Web**. Executar como: **Eu**. Quem pode acessar:
   **Qualquer pessoa**. **Implantar** e copie o **URL do app da Web** (termina em `/exec`).
5. Acionador de limpeza: ícone de relógio (**Acionadores**) > **Adicionar acionador** > função `apagarAntigos`,
   **Baseado no tempo**, **Contador de meses**, dia 1 > **Salvar**.
6. Envie o endereço `/exec` para o Claude (ou cole em `REGISTRO_URL`, no início do script da página).

O endereço `/exec` não dá acesso à planilha: só aceita gravar linhas novas. Quem o conhecer pode enviar linhas
falsas; o limite por minuto reduz o dano. Se acontecer, faça uma nova implantação e troque o endereço.
