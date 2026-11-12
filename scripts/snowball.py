"""Snowballing do léxico por coocorrência (rodada de candidatos).

Entrada : saidas/corpus_programas.csv (gerado pelo notebook; um programa por linha)
Saída   : saidas/snowball_rodada<N>_candidatos.csv + resumo no terminal

Uso:
    python scripts/snowball.py --rodada 1 --sementes inovação competitividade digital internacional emprego
    python scripts/snowball.py --rodada 2 --sementes <sementes aprovadas na rodada 1>

A ideia, em uma frase: para cada termo semente, olhar quais outros termos aparecem
perto dele (janela de palavras) MAIS do que o acaso explicaria (PMI), e propor esses
como candidatos a entrar no léxico. Quem decide o que entra é o pesquisador.
"""
import argparse
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ARQ_CORPUS = RAIZ / "saidas" / "corpus_programas.csv"


def carrega_corpus():
    df = pd.read_csv(ARQ_CORPUS, encoding="utf-8", dtype={"codigo": str})
    df["tokens"] = df["texto_lematizado"].fillna("").str.split()

    # Reaproveitamento textual: vários programas repetem o texto entre períodos.
    # Se contássemos todos, termos que só coocorrem porque o texto foi COPIADO
    # ganhariam peso falso. Mantemos uma cópia de cada texto lematizado idêntico.
    n_antes = len(df)
    df_unico = df.drop_duplicates(subset="texto_lematizado", keep="first").copy()
    print(f"Programas no corpus: {n_antes} | textos distintos usados: {len(df_unico)} "
          f"(removidos {n_antes - len(df_unico)} idênticos)")
    return df, df_unico


def conta_coocorrencias(df_unico, sementes, janela):
    """Para cada semente, conta os termos vizinhos (até `janela` palavras de cada lado)."""
    freq_termo = Counter()                 # quantas vezes cada termo aparece no corpus
    docs_termo = defaultdict(set)          # em quantos textos distintos aparece
    vizinhos = {s: Counter() for s in sementes}
    docs_par = {s: defaultdict(set) for s in sementes}   # textos onde (semente, termo) coocorrem
    total_tokens = 0

    for i, toks in enumerate(df_unico["tokens"]):
        total_tokens += len(toks)
        for t in toks:
            freq_termo[t] += 1
            docs_termo[t].add(i)
        for pos, t in enumerate(toks):
            if t in vizinhos:
                ini, fim = max(0, pos - janela), min(len(toks), pos + janela + 1)
                for j in range(ini, fim):
                    if j != pos:
                        v = toks[j]
                        vizinhos[t][v] += 1
                        docs_par[t][v].add(i)
    return freq_termo, docs_termo, vizinhos, docs_par, total_tokens


def pmi_candidatos(sementes, freq_termo, vizinhos, docs_par, total_tokens,
                   min_co, min_docs, min_freq):
    """PMI = log2( P(termo perto da semente) / P(termo no corpus) ).

    > 0: aparece perto da semente mais do que o esperado ao acaso.
    Filtros contra ruído (corpus pequeno): coocorrência mínima, nº mínimo de textos
    distintos e frequência mínima do termo.
    """
    linhas = []
    for s in sementes:
        total_viz = sum(vizinhos[s].values())
        if total_viz == 0:
            print(f"AVISO: semente '{s}' não aparece no corpus (confira o lema).")
            continue
        for t, c in vizinhos[s].items():
            if t in sementes:
                continue
            nd = len(docs_par[s][t])
            if c < min_co or nd < min_docs or freq_termo[t] < min_freq:
                continue
            p_cond = c / total_viz
            p_base = freq_termo[t] / total_tokens
            linhas.append({
                "semente": s, "candidato": t,
                "pmi": round(math.log2(p_cond / p_base), 2),
                "coocorrencias": c, "textos_com_o_par": nd,
                "freq_no_corpus": freq_termo[t],
            })
    return pd.DataFrame(linhas)


def trechos(df_unico, semente, candidato, n=2, tam=160):
    """Trechos do texto ORIGINAL em que semente e candidato aparecem na mesma frase.
    Busca pelo radical (5 primeiras letras do lema), então é aproximado."""
    rs, rc = semente[:5], candidato[:5]
    achados = []
    for _, linha in df_unico.iterrows():
        texto = str(linha["texto_completo"])
        for frase in re.split(r"(?<=[.;!?])\s+", texto):
            f = frase.lower()
            if rs in f and rc in f:
                achados.append(f"[{linha['periodo']} / {linha['codigo']}] " +
                               " ".join(frase.split())[:tam])
                break
        if len(achados) >= n:
            break
    return achados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodada", type=int, default=1)
    ap.add_argument("--sementes", nargs="+", required=True)
    ap.add_argument("--janela", type=int, default=5)
    ap.add_argument("--min-co", type=int, default=3)
    ap.add_argument("--min-docs", type=int, default=3)
    ap.add_argument("--min-freq", type=int, default=5)
    ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()

    df, df_unico = carrega_corpus()
    sementes = list(dict.fromkeys(a.sementes))
    freq, docs, viz, docs_par, tot = conta_coocorrencias(df_unico, sementes, a.janela)

    print(f"\nSementes e frequência no corpus: " +
          ", ".join(f"{s}={freq[s]}" for s in sementes))
    cand = pmi_candidatos(sementes, freq, viz, docs_par, tot, a.min_co, a.min_docs, a.min_freq)
    if cand.empty:
        print("Nenhum candidato passou nos filtros.")
        return

    # Ranking geral: candidatos ligados a mais sementes e com PMI maior sobem.
    geral = (cand.groupby("candidato")
             .agg(n_sementes=("semente", "nunique"),
                  pmi_max=("pmi", "max"),
                  pmi_medio=("pmi", "mean"),
                  coocorrencias=("coocorrencias", "sum"),
                  freq_no_corpus=("freq_no_corpus", "first"),
                  sementes=("semente", lambda x: ", ".join(sorted(x))))
             .reset_index()
             .sort_values(["n_sementes", "pmi_max"], ascending=False))
    geral["pmi_medio"] = geral["pmi_medio"].round(2)
    saida = RAIZ / "saidas" / f"snowball_rodada{a.rodada}_candidatos.csv"
    geral.to_csv(saida, index=False, encoding="utf-8")
    cand.sort_values(["semente", "pmi"], ascending=[True, False]).to_csv(
        RAIZ / "saidas" / f"snowball_rodada{a.rodada}_por_semente.csv", index=False, encoding="utf-8")

    print(f"\n=== Candidatos por semente (top {a.top}, janela ±{a.janela}) ===")
    for s in sementes:
        sub = cand[cand["semente"] == s].sort_values("pmi", ascending=False).head(a.top)
        print(f"\n[{s}]")
        for _, r in sub.iterrows():
            print(f"  {r['candidato']:<18} PMI={r['pmi']:<5} coocorr={r['coocorrencias']:<3} "
                  f"textos={r['textos_com_o_par']:<2} freq={r['freq_no_corpus']}")

    print(f"\n=== Ranking geral (ligados a mais sementes primeiro), top 25 ===")
    print(geral.head(25).to_string(index=False))
    print(f"\nSalvo em {saida}")

    print("\n=== Trechos de contexto dos 10 primeiros candidatos do ranking geral ===")
    for _, r in geral.head(10).iterrows():
        s0 = r["sementes"].split(", ")[0]
        print(f"\n* {r['candidato']} (perto de: {r['sementes']})")
        for t in trechos(df_unico, s0, r["candidato"]):
            print("   -", t)


if __name__ == "__main__":
    main()
