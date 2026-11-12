"""Mudança de discurso x mudança de composição.

Pergunta: quando o vocabulário de um período muda em relação ao anterior, quanto disso vem de
programas que ENTRARAM ou SAÍRAM da lista (composição) e quanto vem de programas que continuam
e REESCREVERAM o texto (discurso)?

Entrada : saidas/corpus_programas.csv + tabela de equivalência do notebook (série de cada programa)
Saídas  : saidas/composicao_transicoes.csv, saidas/composicao_series.csv,
          saidas/composicao_termos_chave.csv, saidas/composicao_vs_reescrita.png

Método (vetores TF-IDF dos lemas, ajustados nos textos dos programas):
- V_antes  = texto de todos os programas do período anterior
- V_depois = texto de todos os programas do período seguinte
- V_contra = contrafactual: programas que continuam com o texto ANTIGO + programas que entraram
  distância(V_antes, V_contra)  -> efeito de composição (só troca de programas)
  distância(V_contra, V_depois) -> efeito de reescrita (só mudança de texto de quem continuou)
  distância(V_antes, V_depois)  -> mudança total
As duas parcelas não somam exatamente a total (distâncias de cosseno não são aditivas), mas
mostram qual das duas forças domina em cada transição.
"""
import ast
import re
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from estilo import CINZA, SERIES, TINTA, TINTA2, eixo_limpo, plt, salvar, titulo

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
CHAVE = ["inovação", "competitividade", "digital", "internacional", "emprego"]


def equivalencia():
    nb = nbformat.read(RAIZ / "notebooks" / "TCC.ipynb", as_version=4)
    src = next(c.source for c in nb.cells if c.cell_type == "code" and "equivalencia_2004 = {" in c.source)
    return ast.literal_eval(re.search(r"equivalencia_2004 = (\{.*?\n\})", src, re.S).group(1))


def carrega():
    df = pd.read_csv(SAIDAS / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str})
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    eq = equivalencia()
    df["serie"] = [eq.get(c, c) if p == "2004-2007" else c for c, p in zip(df["codigo"], df["periodo"])]
    return df


def main():
    df = carrega()
    periodos = sorted(df["periodo"].unique())
    vec = TfidfVectorizer(token_pattern=r"\S+").fit(df["texto_lematizado"])
    texto = lambda sub: " ".join(sub["texto_lematizado"])
    dist = lambda a, b: max(0.0, 1 - cosine_similarity(vec.transform([a]), vec.transform([b]))[0, 0])

    # ---------------- transições
    trans, termos = [], []
    for p0, p1 in zip(periodos[:-1], periodos[1:]):
        a, b = df[df.periodo == p0], df[df.periodo == p1]
        cont = sorted(set(a.serie) & set(b.serie))
        ent = sorted(set(b.serie) - set(a.serie))
        sai = sorted(set(a.serie) - set(b.serie))
        contra = texto(a[a.serie.isin(cont)]) + " " + texto(b[b.serie.isin(ent)])
        ta, tb = texto(a), texto(b)
        tok_b = len(tb.split())
        trans.append({
            "transicao": f"{p0} → {p1}", "continuam": ", ".join(cont), "entram": ", ".join(ent), "saem": ", ".join(sai),
            "mudanca_total": round(dist(ta, tb), 3),
            "efeito_composicao": round(dist(ta, contra), 3),
            "efeito_reescrita": round(dist(contra, tb), 3),
            "pct_lemas_de_quem_continua": round(100 * len(texto(b[b.serie.isin(cont)]).split()) / tok_b, 1),
        })
        for t in CHAVE:
            n = lambda sub: sum(x.split().count(t) for x in sub["texto_lematizado"])
            termos.append({"transicao": f"{p0} → {p1}", "termo": t,
                           "continuam_antes": n(a[a.serie.isin(cont)]), "continuam_depois": n(b[b.serie.isin(cont)]),
                           "saem": n(a[a.serie.isin(sai)]), "entram": n(b[b.serie.isin(ent)])})
    tr = pd.DataFrame(trans)
    tt = pd.DataFrame(termos)
    tr.to_csv(SAIDAS / "composicao_transicoes.csv", index=False, encoding="utf-8")
    tt.to_csv(SAIDAS / "composicao_termos_chave.csv", index=False, encoding="utf-8")

    # ---------------- mesma série ao longo do tempo
    ser = []
    for s, g in df.groupby("serie"):
        g = g.groupby("periodo")["texto_lematizado"].apply(" ".join)
        ps = [p for p in periodos if p in g.index]
        for p0, p1 in zip(ps[:-1], ps[1:]):
            ser.append({"serie": s, "de": p0, "para": p1, "similaridade": round(1 - dist(g[p0], g[p1]), 3),
                        "texto_identico": g[p0] == g[p1]})
    se = pd.DataFrame(ser)
    se.to_csv(SAIDAS / "composicao_series.csv", index=False, encoding="utf-8")

    pd.set_option("display.width", 220)
    print("=== Transições: composição x reescrita (distância de cosseno; 0 = igual, 1 = sem palavras em comum) ===")
    print(tr[["transicao", "mudanca_total", "efeito_composicao", "efeito_reescrita", "pct_lemas_de_quem_continua"]].to_string(index=False))
    print("\nEntram / saem por transição:")
    for _, r in tr.iterrows():
        print(f"  {r['transicao']}: entram [{r['entram']}] | saem [{r['saem']}]")
    print("\n=== Mesma série entre períodos consecutivos (similaridade; texto idêntico = herança literal) ===")
    print(se.pivot_table(index="serie", columns="para", values="similaridade").round(2).to_string())
    print(f"\nPares de períodos com texto idêntico: {int(se['texto_identico'].sum())} de {len(se)}")
    print("\n=== Termos-chave: de onde vem a variação (contagens) ===")
    print(tt[(tt[["continuam_antes", "continuam_depois", "saem", "entram"]].sum(axis=1) > 0)].to_string(index=False))

    # ---------------- figura
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1.1, 1]})
    x = np.arange(len(tr))
    w = 0.36
    ax1.bar(x - w / 2 - 0.01, tr["efeito_composicao"], w, color=SERIES[1], label="composição (entram e saem programas)")
    ax1.bar(x + w / 2 + 0.01, tr["efeito_reescrita"], w, color=SERIES[0], label="reescrita (quem continua muda o texto)")
    ax1.scatter(x, tr["mudanca_total"], color=TINTA, s=28, zorder=3, label="mudança total")
    ax1.set_xticks(x)
    ax1.set_xticklabels([t.replace(" → ", "\n→ ") for t in tr["transicao"]], fontsize=8.5)
    ax1.set_ylabel("distância de cosseno (TF-IDF)", fontsize=9)
    eixo_limpo(ax1)
    titulo(ax1, "De onde vem a mudança entre períodos", "barras: cada força isolada; ponto: mudança total")
    ax1.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0, -0.2), ncol=1, labelcolor=TINTA2)

    nucleo = se.groupby("serie").size().sort_values(ascending=False).head(5).index.tolist()
    for i, s in enumerate(nucleo):
        g = se[se.serie == s]
        xs = [periodos.index(p) for p in g["para"]]
        ax2.plot(xs, g["similaridade"], color=SERIES[i], lw=2, marker="o", ms=6, markeredgecolor="white", markeredgewidth=1.2)
        ax2.text(xs[-1] + 0.12, g["similaridade"].iloc[-1], s, fontsize=8.5, color=TINTA2, va="center")
    ax2.set_xticks(range(1, len(periodos)))
    ax2.set_xticklabels([f"{p0[:4]}→{p1[:4]}" for p0, p1 in zip(periodos[:-1], periodos[1:])], fontsize=8.5)
    ax2.set_ylim(0, 1.05)
    ax2.set_xlim(0.6, len(periodos) - 0.3)
    ax2.set_ylabel("similaridade com o período anterior", fontsize=9)
    eixo_limpo(ax2)
    titulo(ax2, "Quanto o mesmo programa reescreve o texto", "1,0 = texto copiado do ciclo anterior; séries com mais períodos")
    fig.tight_layout()
    salvar(fig, "composicao_vs_reescrita.png")


if __name__ == "__main__":
    main()
