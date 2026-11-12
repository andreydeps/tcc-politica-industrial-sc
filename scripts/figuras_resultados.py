"""Figuras dos resultados que até agora só existiam em tabela.

Entradas (geradas pelos outros scripts e pelo notebook):
  saidas/valores_instrumentos.csv, saidas/mencoes_blocos.csv, saidas/corpus_programas.csv,
  saidas/clusters_termos.csv, saidas/clusters_por_periodo.csv
Saídas:
  saidas/instrumentos_participacao_ppa.png  peso dos programas selecionados e dos instrumentos no PPA
  saidas/instrumentos_presenca_acoes.png    em quantos programas cada instrumento aparece nas ações
  saidas/continuidade_series.png            linha do tempo das séries de programas
  saidas/campos_semanticos_por_periodo.png  trajetória dos campos temáticos
"""
from pathlib import Path

import numpy as np
import pandas as pd

from composicao_discurso import carrega
from estilo import CINZA, FUNDO, SERIES, TINTA, TINTA2, eixo_limpo, plt, salvar, titulo

SAIDAS = Path(__file__).resolve().parent.parent / "saidas"
ANUAIS = ("2004-2007", "2008-2011")


def instrumentos_participacao():
    r = pd.read_csv(SAIDAS / "valores_instrumentos.csv", encoding="utf-8")
    per = r["periodo"].tolist()
    x = np.arange(len(per))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6))
    sel = 100 * r["total_programas_selecionados"] / r["total_documento"]
    barras = a1.bar(x, sel, color=SERIES[0], width=0.62)
    for b, p in zip(barras, per):
        if p in ANUAIS:
            b.set_alpha(0.45)
    for xi, v in zip(x, sel):
        a1.text(xi, v + 0.05, f"{v:.1f}%".replace(".", ","), ha="center", fontsize=8.5, color=TINTA)
    a1.set_xticks(x)
    a1.set_xticklabels(per, fontsize=8.5)
    a1.set_ylabel("% do valor total do PPA", fontsize=9)
    eixo_limpo(a1)
    titulo(a1, "Programas selecionados no valor do PPA", "barras claras: valores de um ano só (2004 e 2008)")

    cats = [("crédito / financiamento", "crédito"), ("APL / arranjo produtivo", "APL"),
            ("incubadora / parque / centro de inovação", "incubadoras e parques")]
    for i, (c, rot) in enumerate(cats):
        y = r[f"{c} | % documento"]
        a2.plot(x, y, color=SERIES[i], lw=2, marker="o", ms=6, markeredgecolor="white", markeredgewidth=1.2)
        a2.text(x[-1] + 0.12, y.iloc[-1], rot, fontsize=8.5, color=TINTA2, va="center")
    a2.axvspan(-0.4, 1.4, color=CINZA, alpha=0.18, lw=0)
    a2.text(0.5, a2.get_ylim()[1] * 0.97, "um ano só", ha="center", va="top", fontsize=8, color=TINTA2)
    a2.set_xticks(x)
    a2.set_xticklabels(per, fontsize=8.5)
    a2.set_xlim(-0.4, len(per) - 0.2)
    a2.set_ylabel("% do valor total do PPA", fontsize=9)
    eixo_limpo(a2)
    titulo(a2, "Instrumentos nas subações dos programas selecionados", "valores orçados; crédito quase todo via BADESC")
    fig.tight_layout()
    salvar(fig, "instrumentos_participacao_ppa.png")


def instrumentos_presenca():
    d = pd.read_csv(SAIDAS / "mencoes_blocos.csv", encoding="utf-8", dtype={"codigo": str})
    per = ["2004-2007", "2008-2011", "2012-2015", "2016-2019", "2020-2023", "2024-2027"]
    m = d.groupby(["categoria", "periodo"])["codigo"].nunique().unstack(fill_value=0).reindex(columns=per, fill_value=0)
    ordem = ["crédito / financiamento", "APL / arranjo produtivo", "instrumento de inovação", "cluster / polo",
             "pequeno produtor rural", "educação tecnológica / qualificação", "incentivo fiscal"]
    m = m.reindex([o for o in ordem], fill_value=0)
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.imshow(m.values, cmap="Blues", vmin=0, vmax=max(4, m.values.max()), aspect="auto")
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.values[i, j]
            ax.text(j, i, str(v) if v else "·", ha="center", va="center", fontsize=9,
                    color="white" if v >= 3 else TINTA)
    ax.set_xticks(range(len(per)))
    ax.set_xticklabels(per, fontsize=8.5)
    ax.set_yticks(range(len(m)))
    rotulos = {"instrumento de inovação": "incubadora, parque, centro de inovação",
               "educação tecnológica / qualificação": "qualificação e capacitação (gestores, agricultores)"}
    ax.set_yticklabels([rotulos.get(o, o) for o in m.index], fontsize=9)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(per)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(m)), minor=True)
    ax.grid(which="minor", color=FUNDO, lw=2)
    ax.tick_params(which="minor", length=0)
    titulo(ax, "Programas selecionados com o instrumento nas ações e subações",
           "número de programas por período; ponto = nenhum")
    salvar(fig, "instrumentos_presenca_acoes.png")


def continuidade():
    df = carrega()
    per = sorted(df["periodo"].unique())
    pres = df.groupby(["serie", "periodo"]).size().unstack(fill_value=0).reindex(columns=per, fill_value=0) > 0
    nome = df.sort_values("periodo").groupby("serie")["nome"].last().str.split().str.join(" ")
    pres = pres.loc[pres.sum(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(11, 0.42 * len(pres) + 1.4))
    for i, (s, linha) in enumerate(pres.iterrows()):
        js = [j for j, v in enumerate(linha) if v]
        ax.plot([min(js), max(js)], [i, i], color=CINZA, lw=1.2, zorder=1)
        ax.scatter(js, [i] * len(js), s=70, color=SERIES[0], edgecolor="white", linewidth=1.2, zorder=2)
    ax.set_yticks(range(len(pres)))
    ax.set_yticklabels([f"{s}  {nome[s][:48]}" for s in pres.index], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xticks(range(len(per)))
    ax.set_xticklabels(per, fontsize=8.5)
    ax.xaxis.tick_top()
    eixo_limpo(ax, grade="x")
    ax.spines["bottom"].set_visible(False)
    ax.set_title("Continuidade dos programas selecionados (por série)", loc="left", fontsize=11.5,
                 fontweight="bold", color=TINTA, pad=26)
    ax.text(0, -0.035, "2004-2007 ligado aos períodos seguintes por tabela de equivalência proposta (a validar). "
            "Linha cinza: intervalo entre a primeira e a última aparição.", transform=ax.transAxes,
            fontsize=8, color=TINTA2, va="top")
    salvar(fig, "continuidade_series.png")


def campos():
    cl = pd.read_csv(SAIDAS / "clusters_termos.csv", encoding="utf-8")
    por = pd.read_csv(SAIDAS / "clusters_por_periodo.csv", encoding="utf-8", index_col=0)
    alvo = [("inovação", "inovação e tecnologia"), ("empresa", "empresa e economia"), ("acesso", "acesso, informação e digital")]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = np.arange(len(por))
    for i, (termo, rot) in enumerate(alvo):
        c = int(cl.loc[cl.termo == termo, "cluster"].iloc[0])
        y = por[f"C{c:02d}"]
        exemplos = ", ".join(cl[cl.cluster == c].termo.head(4))
        ax.plot(x, y, color=SERIES[i], lw=2, marker="o", ms=6, markeredgecolor="white", markeredgewidth=1.2)
        ax.text(x[-1] + 0.12, y.iloc[-1], f"{rot}\n({exemplos})", fontsize=8, color=TINTA2, va="center")
    ax.set_xticks(x)
    ax.set_xticklabels(por.index, fontsize=8.5)
    ax.set_xlim(-0.3, len(por) + 1.6)
    ax.set_ylabel("% das ocorrências de termos agrupados", fontsize=9)
    eixo_limpo(ax)
    titulo(ax, "Campos semânticos ao longo dos PPAs", "clusters de termos por vetores do spaCy; estrutura de clusters fraca (ver achados)")
    salvar(fig, "campos_semanticos_por_periodo.png")


if __name__ == "__main__":
    instrumentos_participacao()
    instrumentos_presenca()
    continuidade()
    # campos() fica fora: a clusterização muda por inteiro com um programa a mais (ver achados.md)
