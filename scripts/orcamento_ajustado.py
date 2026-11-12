"""Orçamento dos programas selecionados sem itens que não são instrumento de política industrial.

Responde a três dúvidas sobre os valores de valores_acoes.py:
1. Folha da EPAGRI: em 2020-2027 a subação "Administração de pessoal e encargos sociais - EPAGRI" está
   dentro do 0310. Onde ela estava antes? Se estava em outro programa, o salto da parcela é contábil.
2. Parcela ajustada: parcela dos programas selecionados no PPA tirando pessoal/encargos e emendas
   parlamentares (do numerador e, numa segunda versão, também do denominador).
3. Crédito: separa crédito a EMPRESAS de crédito a MUNICÍPIOS (o "Apoio creditício ao desenvolvimento
   dos municípios" do BADESC é a maior linha de crédito e não é política industrial).

Saídas: saidas/orcamento_ajustado.csv, saidas/orcamento_pessoal_epagri.csv
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
from valores_acoes import INSTRUMENTOS, subacoes  # noqa: E402

PESSOAL = r"pessoal|encargos sociais|folha de pagamento|servidor remunerado"
EMENDA = r"emendas? parlamentar"
MUNICIPIO = r"municipi|infra-?estrutura municipal"


def main():
    ns = definicoes_do_notebook()
    regex = {"2004-2007": ns["padrao_2004"], "2008-2011": ns["padrao_2008"]}
    limpar = {"2004-2007": ns["rodape_2004"], "2008-2011": ns["rodape_2008"]}
    linhas, epagri = [], []
    for per, cam in ns["caminhos"].items():
        t = texto_pdf(cam)
        if per in limpar:
            t = limpar[per].sub(" ", t)
        inicios = [(m.start(), m["codigo"]) for m in regex.get(per, ns["padrao"]).finditer(t)]
        sel = set(ns["codigos_industria"][per])
        regs, j, prog = [], 0, None
        for pos, cod, txt, v in subacoes(t, per):
            while j < len(inicios) and inicios[j][0] <= pos:
                prog = inicios[j][1]
                j += 1
            tn = sem_acento(txt).lower()
            regs.append({"programa": prog, "texto": txt, "valor": v, "sel": prog in sel,
                         "pessoal": bool(re.search(PESSOAL, tn)), "emenda": bool(re.search(EMENDA, tn)),
                         "credito": bool(re.search(INSTRUMENTOS["crédito / financiamento"], tn)),
                         "municipio": bool(re.search(MUNICIPIO, tn)), "epagri": "epagri" in tn})
        d = pd.DataFrame(regs)
        for _, r in d[d.pessoal & d.epagri].iterrows():
            epagri.append({"periodo": per, "programa": r.programa, "selecionado": r.sel,
                           "texto": r.texto[:120], "valor": r.valor})
        excl = d.pessoal | d.emenda
        tot, tot_aj = d.valor.sum(), d.loc[~excl, "valor"].sum()
        s = d[d.sel]
        cred = s[s.credito]
        linhas.append({
            "periodo": per,
            "total_ppa": tot,
            "selecionados": s.valor.sum(),
            "selecionados_pessoal": s.loc[s.pessoal, "valor"].sum(),
            "selecionados_emendas": s.loc[s.emenda, "valor"].sum(),
            "pct_selecionados": 100 * s.valor.sum() / tot,
            "pct_selecionados_sem_pessoal_emendas": 100 * s.loc[~excl[s.index], "valor"].sum() / tot,
            "pct_idem_denominador_ajustado": 100 * s.loc[~excl[s.index], "valor"].sum() / tot_aj,
            "credito_total": cred.valor.sum(),
            "credito_empresas": cred.loc[~cred.municipio, "valor"].sum(),
            "credito_municipios": cred.loc[cred.municipio, "valor"].sum(),
            "pct_credito_total": 100 * cred.valor.sum() / tot,
            "pct_credito_empresas": 100 * cred.loc[~cred.municipio, "valor"].sum() / tot,
        })
        print(per, "ok", flush=True)

    r = pd.DataFrame(linhas)
    r.to_csv(SAIDAS / "orcamento_ajustado.csv", index=False, encoding="utf-8")
    e = pd.DataFrame(epagri)
    e.to_csv(SAIDAS / "orcamento_pessoal_epagri.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 90)
    print("\n=== Pessoal da EPAGRI: em que programa está, por PPA ===")
    print(e.assign(valor_mi=(e.valor / 1e6).round(1)).drop(columns="valor").to_string(index=False))
    print("\n=== Parcela no PPA (%) ===")
    print(r.set_index("periodo")[["pct_selecionados", "pct_selecionados_sem_pessoal_emendas",
                                  "pct_idem_denominador_ajustado", "pct_credito_total",
                                  "pct_credito_empresas"]].round(2).to_string())
    print("\n=== R$ milhões ===")
    print((r.set_index("periodo")[["selecionados", "selecionados_pessoal", "selecionados_emendas",
                                   "credito_total", "credito_empresas", "credito_municipios"]] / 1e6)
          .round(1).to_string())


if __name__ == "__main__":
    main()
