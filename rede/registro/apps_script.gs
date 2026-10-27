/**
 * Rede iAgro: registro anônimo de uso numa planilha Google.
 * Adaptado do registro do iAgro Conversa (danimaciel/iagro-conversa, registro/apps_script.gs).
 *
 * Como instalar: rede/registro/LEIAME.md. Resumo: crie uma planilha, abra Extensões > Apps Script, cole este
 * arquivo, implante como "App da Web" (executar como: eu; acesso: qualquer pessoa) e coloque o endereço
 * "…/exec" em REGISTRO_URL, no início do script da página.
 *
 * A página envia quatro tipos de evento, sem IP, cookie ou identificador de pessoa:
 *   perfil  — tipo de ator, bioma, estado, cadeias encontradas e texto do perfil (já sem e-mail, CPF e telefone)
 *   abrir   — documento aberto no kit, posição em que estava, aba e filtro em uso
 *   salvar  — documento salvo ou retirado dos salvos
 *   filtro  — cadeia ou produto escolhido no mapa
 * O campo visita é um código aleatório criado a cada visita, só para ligar os eventos da mesma visita.
 */

const ABA = "registro";
const COLUNAS = ["quando", "evento", "visita", "perfil_salvo", "ator", "bioma", "uf", "cadeias", "texto",
  "documento", "posicao", "aba", "tipo_filtro", "filtro", "salvo", "versao"];
const EVENTOS = ["perfil", "abrir", "salvar", "filtro"];
const LIMITE_POR_MINUTO = 300;   // proteção simples contra envio em massa
const MESES_GUARDA = 12;

function doPost(e) {
  try {
    if (!e || !e.postData || e.postData.contents.length > 5000) return texto("ignorado");
    const d = JSON.parse(e.postData.contents);
    if (EVENTOS.indexOf(d.ev) < 0) return texto("ignorado");
    if (!dentroDoLimite()) return texto("limite");
    const linha = [new Date(), d.ev, d.visita, d.lente, d.ator, d.bioma, d.uf, d.cadeias, d.texto,
      d.c, d.pos, d.aba, d.k, d.filtro, d.salvo, d.v].map((v, k) => k === 0 ? v : celula(v));
    const trava = LockService.getScriptLock();
    trava.waitLock(5000);
    try { aba().appendRow(linha); } finally { trava.releaseLock(); }
    return texto("ok");
  } catch (err) {
    return texto("erro");
  }
}

// texto curto e nunca interpretado como fórmula (=, +, -, @ no início viram texto)
function celula(v) {
  if (v === undefined || v === null) return "";
  let s = String(v).slice(0, 500);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function aba() {
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  let a = planilha.getSheetByName(ABA);
  if (!a) {
    a = planilha.insertSheet(ABA);
    a.appendRow(COLUNAS);
    a.setFrozenRows(1);
  }
  return a;
}

function dentroDoLimite() {
  const cache = CacheService.getScriptCache();
  const chave = "n" + Math.floor(Date.now() / 60000);
  const n = Number(cache.get(chave) || 0) + 1;
  cache.put(chave, String(n), 120);
  return n <= LIMITE_POR_MINUTO;
}

function texto(t) {
  return ContentService.createTextOutput(t);
}

/** Apaga registros com mais de 12 meses. Programe um acionador mensal para esta função (LEIAME.md). */
function apagarAntigos() {
  const a = aba();
  const limite = new Date();
  limite.setMonth(limite.getMonth() - MESES_GUARDA);
  const datas = a.getRange(2, 1, Math.max(a.getLastRow() - 1, 0), 1).getValues();
  let n = 0;
  while (n < datas.length && datas[n][0] instanceof Date && datas[n][0] < limite) n++;
  if (n > 0) a.deleteRows(2, n);
}

/** Teste rápido pelo editor: grava uma linha de exemplo. */
function testar() {
  doPost({postData: {contents: JSON.stringify({ev: "perfil", v: 1, visita: "teste", lente: "teste",
    ator: "Produtor", bioma: "Cerrado", uf: "BA", cadeias: "soja", texto: "teste do registro"})}});
}
