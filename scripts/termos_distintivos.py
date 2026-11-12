"""Termos distintivos entre o início e o fim da série (log-odds com prior de Dirichlet informativo).

Método de Monroe, Colaresi e Quinn (2008), "Fightin' Words": compara a frequência de cada lema em
dois grupos de textos, encolhendo palavras raras em direção à frequência do corpus todo (prior), e
devolve um escore z. |z| > 1,96 indica diferença improvável ao acaso. Diferente do TF-IDF, não
depende de escolher termos antes: o corpus inteiro diz o que mudou.

Grupos: início = 2004-2007 + 2008-2011; fim = 2020-2023 + 2024-2027. Textos idênticos dentro de um
grupo são contados uma vez (herança literal não deve inflar o resultado).

Entrada : saidas/corpus_programas.csv
Saídas  : saidas/termos_distintivos.csv, saidas/termos_distintivos_inicio_fim.png
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from estilo import CINZA, SERIES, TINTA, TINTA2, eixo_limpo, plt, salvar, titulo

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
INICIO = ["2004-2007", "2008-2011"]
FIM = ["2020-2023", "2024-2027"]


def logodds_z(y_i, y_j, fundo, a0):
    """z do log-odds de i contra j com prior proporcional ao corpus de fundo (soma do prior = a0)."""
    alfa = fundo * (a0 / fundo.sum())
    n_i, n_j = y_i.sum(), y_j.sum()
    l_i = np.log((y_i + alfa) / (n_i + a0 - y_i - alfa))
    l_j = np.log((y_j + alfa) / (n_j + a0 - y_j - alfa))
    return (l_i - l_j) / np.sqrt(1 / (y_i + alfa) + 1 / (y_j + alfa))


def main():
    df = pd.read_csv(SAIDAS / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str})
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    cv = CountVectorizer(token_pattern=r"\S+", lowercase=False)
    X = cv.fit_transform(df["texto_lematizado"]).toarray()
    vocab = np.array(cv.get_feature_names_out())
    fundo = X.sum(axis=0).astype(float)

    def grupo(pers):
        sub = df[df.periodo.isin(pers)].drop_duplicates("texto_lematizado")
        return X[sub.index].sum(axis=0).astype(float), len(sub)

    y_fim, n_fim = grupo(FIM)
    y_ini, n_ini = grupo(INICIO)
    print(f"Textos distintos: início {n_ini} ({int(y_ini.sum())} lemas) | fim {n_fim} ({int(y_fim.sum())} lemas)")

    res = {}
    for a0 in (100, 500, 2000):          # sensibilidade à força do prior
        res[a0] = logodds_z(y_fim, y_ini, fundo, a0)
    z = res[500]
    t = pd.DataFrame({"termo": vocab, "z": z.round(2), "n_inicio": y_ini.astype(int), "n_fim": y_fim.astype(int),
                      "z_prior_100": res[100].round(2), "z_prior_2000": res[2000].round(2)})
    t = t[(t.n_inicio + t.n_fim) >= 3].sort_values("z")
    t.to_csv(SAIDAS / "termos_distintivos.csv", index=False, encoding="utf-8")

    sig = t[t.z.abs() > 1.96]
    print(f"Termos com |z| > 1,96: {len(sig)} ({(sig.z > 0).sum()} do fim, {(sig.z < 0).sum()} do início)")
    pd.set_option("display.width", 200)
    print("\n=== Mais típicos do FIM (2020-2027) ===")
    print(t.tail(15).iloc[::-1].to_string(index=False))
    print("\n=== Mais típicos do INÍCIO (2004-2011) ===")
    print(t.head(15).to_string(index=False))
    for a0 in (100, 2000):
        col = f"z_prior_{a0}"
        top_a = set(t.nlargest(15, "z").termo) | set(t.nsmallest(15, "z").termo)
        top_b = set(t.nlargest(15, col).termo) | set(t.nsmallest(15, col).termo)
        print(f"\nSensibilidade: top 15 de cada lado com prior {a0} coincide em {len(top_a & top_b)} de 30 termos")

    # figura: barras divergentes
    top = pd.concat([t.head(12), t.tail(12)])
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    cores = [SERIES[1] if v < 0 else SERIES[0] for v in top.z]
    ax.barh(range(len(top)), top.z, color=cores, height=0.72)
    for i, (termo, v, a, b) in enumerate(zip(top.termo, top.z, top.n_inicio, top.n_fim)):
        ax.text(v + (0.08 if v > 0 else -0.08), i, f"{termo} ({a}→{b})", va="center",
                ha="left" if v > 0 else "right", fontsize=8.5, color=TINTA)
    ax.axvline(0, color=TINTA2, lw=0.8)
    for s in (-1.96, 1.96):
        ax.axvline(s, color=CINZA, lw=0.8, ls="--")
    ax.set_yticks([])
    lim = max(abs(top.z)) + 1.6
    ax.set_xlim(-lim, lim)
    ax.set_xlabel("escore z do log-odds (linhas tracejadas: |z| = 1,96)", fontsize=9)
    eixo_limpo(ax, grade="x")
    titulo(ax, "Termos mais típicos do início e do fim da série",
           "laranja: 2004-2011; azul: 2020-2027; entre parênteses, ocorrências início→fim")
    salvar(fig, "termos_distintivos_inicio_fim.png")


if __name__ == "__main__":
    main()
