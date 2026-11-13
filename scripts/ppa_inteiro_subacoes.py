"""Todas as subações dos 6 PPAs (não só dos programas selecionados), com a meta financeira.

Entradas: PDFs (cache de texto), regex do notebook, leitura de subações de valores_acoes.py.
Saída   : saidas/ppa_inteiro_subacoes.csv
          colunas: periodo, programa, selecionado, subacao, texto, unidade, valor, pct_ppa,
                   pessoal, emenda

Mesma leitura de valores de valores_acoes.py (2004-2007 e 2008-2011: um ano, OGE + OF;
2012-2015: total do quadriênio; 2016-2027: tesouro + outras fontes). Por isso a comparação
entre PPAs é sempre em % do total do próprio PPA (pct_ppa). Valores nominais.
unidade: sigla no fim do nome da subação ("... - EPAGRI", "... - FAPESC"), quando existe
(2012 em diante); é a unidade orçamentária que executa a subação.
pessoal / emenda: mesmos padrões de orcamento_ajustado.py.
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
from orcamento_ajustado import EMENDA, PESSOAL  # noqa: E402
from valores_acoes import subacoes  # noqa: E402

UNIDADE = re.compile(r"\s-\s([A-ZÀ-Ú]{2,}[A-ZÀ-Ú0-9/]*)(?=\s|$)")   # a última sigla depois de " - "


def main():
    ns = definicoes_do_notebook()
    regex = {"2004-2007": ns["padrao_2004"], "2008-2011": ns["padrao_2008"]}
    limpar = {"2004-2007": ns["rodape_2004"], "2008-2011": ns["rodape_2008"]}
    regs = []
    for per, cam in ns["caminhos"].items():
        t = texto_pdf(cam)
        if per in limpar:
            t = limpar[per].sub(" ", t)
        inicios = [(m.start(), m["codigo"]) for m in regex.get(per, ns["padrao"]).finditer(t)]
        sel = set(ns["codigos_industria"][per])
        j, prog = 0, None
        linhas = []
        for pos, cod, txt, v in subacoes(t, per):
            while j < len(inicios) and inicios[j][0] <= pos:
                prog = inicios[j][1]
                j += 1
            if prog is None:
                continue
            tn = sem_acento(txt).lower()
            u = UNIDADE.findall(txt.split(" | ")[-1])
            linhas.append({"periodo": per, "programa": prog, "selecionado": int(prog in sel), "subacao": cod,
                           "texto": " ".join(txt.split()), "unidade": u[-1] if u else "", "valor": v,
                           "pessoal": int(bool(re.search(PESSOAL, tn))),
                           "emenda": int(bool(re.search(EMENDA, tn)))})
        d = pd.DataFrame(linhas)
        d["pct_ppa"] = 100 * d["valor"] / d["valor"].sum()
        regs.append(d)
        print(f"{per}: {len(d)} subações, {d.programa.nunique()} programas, total {d.valor.sum()/1e9:,.1f} bi")
    out = pd.concat(regs, ignore_index=True)
    out.to_csv(SAIDAS / "ppa_inteiro_subacoes.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
