"""Cenário de curadoria: antes (lista oficial) x depois (lista + candidatos apontados pelo classificador).

A lista oficial NÃO muda. Este script monta um corpus alternativo, roda as análises principais
nele e compara com a versão oficial.

Candidatos (12/11/2026, apontados por scripts/classificador.py):
  0530 Pró-Emprego e Renda          2008-2011, 2012-2015, 2016-2019 (continua o 0530 de 2004-2007)
  0101 Acelera Santa Catarina        2012-2015, 2016-2019, 2020-2023, 2024-2027
  0204 Missões, Recepções e Eventos Internacionais   2016-2019

Saídas: saidas/corpus_programas_cenario.csv, saidas/cenario_curadoria_comparacao.csv
        (+ as saídas de cada análise com sufixo _cenario / nome "cenario")
"""
import subprocess
import sys
from pathlib import Path

import pandas as pd
import spacy

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
PY = sys.executable
EXTRA = [("2008-2011", "0530"), ("2012-2015", "0530"), ("2016-2019", "0530"),
         ("2012-2015", "0101"), ("2016-2019", "0101"), ("2020-2023", "0101"), ("2024-2027", "0101"),
         ("2016-2019", "0204")]


def monta_corpus():
    oficial = pd.read_csv(SAIDAS / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str})
    todos = pd.read_csv(SAIDAS / "programas_todos.csv", encoding="utf-8", dtype={"codigo": str})
    novos = pd.concat([todos[(todos.periodo == p) & (todos.codigo == c)] for p, c in EXTRA])
    novos = novos.assign(orgao="", texto_completo=novos["objetivo"] + " " + novos["justificativa"])
    # mesma lematização do notebook (pipeline completo do spaCy)
    nlp = spacy.load("pt_core_news_lg")
    lema = lambda t: " ".join(tk.lemma_.lower() for tk in nlp(t) if not tk.is_stop and not tk.is_punct
                              and not tk.is_space and tk.is_alpha and tk.pos_ in {"NOUN", "VERB", "ADJ"})
    novos["texto_lematizado"] = novos["texto_completo"].apply(lema)
    cen = pd.concat([oficial, novos[oficial.columns]], ignore_index=True)
    cen.to_csv(SAIDAS / "corpus_programas_cenario.csv", index=False, encoding="utf-8")
    print(f"Corpus oficial: {len(oficial)} programas | cenário: {len(cen)} (+{len(novos)})")
    return oficial, cen


def roda(args):
    r = subprocess.run([PY, "-W", "ignore", *args], cwd=Path(__file__).parent, capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit(f"falhou: {args}")


def main():
    oficial, cen = monta_corpus()
    extra = ",".join(f"{p}:{c}" for p, c in EXTRA)
    print("Rodando análises no cenário (circularidade, índice por dimensão, valores orçados)...", flush=True)
    roda(["circularidade.py", "--arquivo", "corpus_programas_cenario.csv", "--sufixo", "_cenario"])
    roda(["indice_lexico.py", "--lexico", str(SAIDAS / "lexico_validado.csv"), "--corpus", "cenario"])
    roda(["valores_acoes.py", "--extra", extra, "--sufixo", "_cenario"])

    linhas = []
    # 1. programas por período
    for p in sorted(cen.periodo.unique()):
        linhas.append({"bloco": "programas", "item": p, "antes": int((oficial.periodo == p).sum()),
                       "depois": int((cen.periodo == p).sum())})
    # 2. circularidade
    a = pd.read_csv(SAIDAS / "circularidade_resumo.csv", encoding="utf-8")
    b = pd.read_csv(SAIDAS / "circularidade_resumo_cenario.csv", encoding="utf-8")
    for (_, ra), (_, rb) in zip(a.iterrows(), b.iterrows()):
        linhas.append({"bloco": "circularidade: p de permutação", "item": f"{ra.termo} ({ra.medida})",
                       "antes": ra.p_perm_amplitude, "depois": rb.p_perm_amplitude})
    # 3. índice por dimensão
    a = pd.read_csv(SAIDAS / "indice_lexico_programas_testes.csv", encoding="utf-8").set_index("dimensao")
    b = pd.read_csv(SAIDAS / "indice_lexico_cenario_testes.csv", encoding="utf-8").set_index("dimensao")
    for d in a.index:
        linhas.append({"bloco": "dimensão: p de permutação", "item": d, "antes": a.loc[d, "p_perm_amplitude"],
                       "depois": b.loc[d, "p_perm_amplitude"]})
        linhas.append({"bloco": "dimensão: % léxicos aleatórios superados", "item": d,
                       "antes": a.loc[d, "pct_lexicos_aleatorios_amplitude"], "depois": b.loc[d, "pct_lexicos_aleatorios_amplitude"]})
    ta = pd.read_csv(SAIDAS / "indice_lexico_programas.csv", encoding="utf-8")
    tb = pd.read_csv(SAIDAS / "indice_lexico_cenario.csv", encoding="utf-8")
    for d in ["competitividade e produção", "trabalho e renda", "inserção internacional"]:
        for p in sorted(ta.periodo.unique()):
            linhas.append({"bloco": f"taxa por mil lemas: {d}", "item": p,
                           "antes": ta[(ta.dimensao == d) & (ta.periodo == p)].taxa_por_mil.iloc[0],
                           "depois": tb[(tb.dimensao == d) & (tb.periodo == p)].taxa_por_mil.iloc[0]})
    # 4. valores orçados
    a = pd.read_csv(SAIDAS / "valores_instrumentos.csv", encoding="utf-8").set_index("periodo")
    b = pd.read_csv(SAIDAS / "valores_instrumentos_cenario.csv", encoding="utf-8").set_index("periodo")
    for p in a.index:
        linhas.append({"bloco": "% do PPA: programas selecionados", "item": p,
                       "antes": round(100 * a.loc[p, "total_programas_selecionados"] / a.loc[p, "total_documento"], 2),
                       "depois": round(100 * b.loc[p, "total_programas_selecionados"] / b.loc[p, "total_documento"], 2)})
        linhas.append({"bloco": "% do PPA: crédito", "item": p,
                       "antes": round(a.loc[p, "crédito / financiamento | % documento"], 2),
                       "depois": round(b.loc[p, "crédito / financiamento | % documento"], 2)})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "cenario_curadoria_comparacao.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 200)
    for bloco, g in t.groupby("bloco", sort=False):
        print(f"\n=== {bloco} ===")
        print(g[["item", "antes", "depois"]].to_string(index=False))


if __name__ == "__main__":
    main()
