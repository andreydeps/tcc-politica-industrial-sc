"""Valores orçados das subações ligadas a instrumentos de política (crédito, APL, incubadoras
e parques, polos) nos programas selecionados, por período.

Entrada : PDFs (via cache de texto do blocos_programas.py) e definições do notebook.
Saídas  : saidas/valores_subacoes.csv (uma linha por subação dos programas selecionados)
          saidas/valores_instrumentos.csv (resumo por período e instrumento)

O que significa cada coluna de valor (conferido nos cabeçalhos dos PDFs):
- 2004-2007 e 2008-2011: colunas "OGE" e "OF" sob o cabeçalho "2007/2007" e "2011/2011":
  valores de UM ano (o último do plano). Somamos as duas colunas.
- 2012-2015: "META FINANCEIRA 2015 | 2012-2015": usamos o total do quadriênio (última coluna).
- 2016-2019 em diante: "META FINANCEIRA <quadriênio>: TESOURO | OUTRAS FONTES": somamos as duas.
Como 2004 e 2008 são anuais e os demais são quadrienais, a comparação entre todos os períodos
é feita pela PARTICIPAÇÃO no total do próprio documento, não pelo valor absoluto.
Valores nominais (sem correção pela inflação).
"""
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocos_programas import definicoes_do_notebook, texto_pdf  # noqa: E402
from mencoes import sem_acento  # noqa: E402

INSTRUMENTOS = {
    "crédito / financiamento": r"credit|financiament|emprestimo|microcredito|fundo de aval",
    "APL / arranjo produtivo": r"\bapls?\b|arranjos? produtivos?",
    "incubadora / parque / centro de inovação": r"incubadora|parques? tecnologic|centros? de inovacao|sapiens|base tecnologica",
    "polo": r"\bp[oó]los?\b",
}
NUM = r"-?\d{1,3}(?:\.\d{3})*(?:,\d+)?"
SUBACAO = re.compile(rf"^\s*(?:[AP]\s+)?(?P<cod>\d{{6}})\s+(?P<txt>.*?)\s+(?P<nums>(?:{NUM}\s+){{1,2}}{NUM})\s*$")
ACAO = re.compile(r"^\s*(?P<cod>\d{4})\s+(?P<txt>\D.*)$")


def num(s):
    return float(s.replace(".", "").replace(",", "."))


def valor_da_linha(per, nums):
    v = [num(x) for x in nums.split()]
    if per == "2012-2015":
        return v[-1]                       # total 2012-2015
    return v[-1] + v[-2] if len(v) >= 2 else v[-1]   # OGE+OF ou tesouro+outras fontes


def subacoes(texto, per):
    """Percorre o texto e devolve (posição, código, texto da ação + subação, valor) de cada subação."""
    # Só 2004 e 2008 têm linha de AÇÃO (4 dígitos) acima das subações. De 2012 em diante, linhas de
    # 4 dígitos são INDICADORES (ex.: "0201 Prazo médio de concessão de crédito") e não podem
    # contaminar a classificação das subações seguintes.
    usa_acao = per in ("2004-2007", "2008-2011")
    out, acao_atual, pos = [], "", 0
    for linha in texto.splitlines(keepends=True):
        m = SUBACAO.match(linha)
        if m:
            nums = m["nums"].split()
            v = valor_da_linha(per, " ".join(nums[-2:]))
            out.append((pos, m["cod"], (acao_atual + " | " if usa_acao else "") + m["txt"], v))
        elif usa_acao:
            a = ACAO.match(linha)
            if a and not re.search(r"\d{1,3}\.\d{3}", linha):
                acao_atual = a["txt"].strip()
        pos += len(linha)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", default="", help='programas a acrescentar, ex.: "2008-2011:0530,2016-2019:0204"')
    ap.add_argument("--sufixo", default="", help="sufixo dos arquivos de saída")
    a = ap.parse_args()
    ns = definicoes_do_notebook()
    caminhos = ns["caminhos"]
    codigos = {p: list(c) for p, c in ns["codigos_industria"].items()}
    for item in filter(None, a.extra.split(",")):
        per, cod = item.split(":")
        codigos.setdefault(per, []).append(cod)
    regex = {"2004-2007": ns["padrao_2004"], "2008-2011": ns["padrao_2008"]}
    limpar = {"2004-2007": ns["rodape_2004"], "2008-2011": ns["rodape_2008"]}
    det, resumo = [], []
    for per, cam in caminhos.items():
        t = texto_pdf(cam)
        if per in limpar:
            t = limpar[per].sub(" ", t)
        progs = list(regex.get(per, ns["padrao"]).finditer(t))
        inicios = [(m.start(), m["codigo"]) for m in progs]
        todas = subacoes(t, per)
        total_doc = sum(v for *_, v in todas)
        sel = set(codigos.get(per, []))
        # cada subação pertence ao último programa iniciado antes dela
        j, prog_atual = 0, None
        for pos, cod, txt, v in todas:
            while j < len(inicios) and inicios[j][0] <= pos:
                prog_atual = inicios[j][1]
                j += 1
            if prog_atual in sel:
                tn = sem_acento(txt)
                cats = [c for c, p in INSTRUMENTOS.items() if re.search(p, tn)]
                det.append({"periodo": per, "programa": prog_atual, "subacao": cod, "texto": txt[:200],
                            "valor": v, "instrumento": cats[0] if cats else ""})
        d = pd.DataFrame([x for x in det if x["periodo"] == per])
        total_sel = d["valor"].sum()
        linha = {"periodo": per, "base": "1 ano" if per in ("2004-2007", "2008-2011") else "quadriênio",
                 "total_documento": total_doc, "total_programas_selecionados": total_sel,
                 "subacoes_documento": len(todas), "subacoes_selecionadas": len(d)}
        for c in INSTRUMENTOS:
            vc = d.loc[d.instrumento == c, "valor"].sum()
            linha[f"{c} | valor"] = vc
            linha[f"{c} | % selecionados"] = 100 * vc / total_sel if total_sel else 0
            linha[f"{c} | % documento"] = 100 * vc / total_doc if total_doc else 0
        resumo.append(linha)
        print(f"{per}: subações no documento {len(todas)} (soma {total_doc/1e9:,.2f} bi) | "
              f"nos selecionados {len(d)} (soma {total_sel/1e6:,.1f} mi)", flush=True)

    pd.DataFrame(det).to_csv(SAIDAS / f"valores_subacoes{a.sufixo}.csv", index=False, encoding="utf-8")
    r = pd.DataFrame(resumo)
    r.to_csv(SAIDAS / f"valores_instrumentos{a.sufixo}.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 230)
    print("\n=== Participação de cada instrumento no valor dos PROGRAMAS SELECIONADOS (%) ===")
    print(r.set_index("periodo")[[f"{c} | % selecionados" for c in INSTRUMENTOS]].round(1)
          .rename(columns=lambda c: c.split(" |")[0]).to_string())
    print("\n=== Participação no valor TOTAL DO DOCUMENTO (%) ===")
    print(r.set_index("periodo")[[f"{c} | % documento" for c in INSTRUMENTOS] + ["total_programas_selecionados"]]
          .assign(total_programas_selecionados=lambda x: 100 * x["total_programas_selecionados"] / r.set_index("periodo")["total_documento"])
          .round(2).rename(columns=lambda c: c.split(" |")[0].replace("total_programas_selecionados", "todos os selecionados")).to_string())
    print("\n=== Valores nominais (R$ milhões; 2004 e 2008 = um ano, demais = quadriênio) ===")
    print((r.set_index("periodo")[[f"{c} | valor" for c in INSTRUMENTOS] + ["total_programas_selecionados"]] / 1e6)
          .round(1).rename(columns=lambda c: c.split(" |")[0]).to_string())


if __name__ == "__main__":
    main()
