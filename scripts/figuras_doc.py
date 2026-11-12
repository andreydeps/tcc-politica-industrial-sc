"""Figuras no tamanho de impressão (16,5 cm = 6,5 pol de largura) para os documentos.

As figuras de análise (saidas/*.png) foram feitas para tela, com muitos painéis; reduzidas à largura da
página, o texto fica ilegível. Aqui cada figura é desenhada já no tamanho final, com fonte de 8,5 a 10 pt.
Saídas: saidas/doc_lexico.png, doc_cenario.png, doc_instrumentos.png, doc_ods.png
"""
from pathlib import Path

import numpy as np
import pandas as pd

from estilo import CINZA, SERIES, TINTA, TINTA2, plt, salvar

S = Path(__file__).resolve().parent.parent / "saidas"
LARG = 6.5
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
                     "xtick.labelsize": 8.5, "ytick.labelsize": 8.5})
CURTO = lambda p: p[2:4] + "-" + p[-2:]          # "2004-2007" -> "04-07"


def limpa(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(CINZA)
    ax.tick_params(length=0)
    ax.grid(axis="y", color=CINZA, alpha=0.4, lw=0.5)
    ax.set_axisbelow(True)


# ------------------------------------------------------------------ 1. léxico: um eixo, competitividade em destaque
t = pd.read_csv(S / "indice_lexico_programas.csv", encoding="utf-8")
per = sorted(t.periodo.unique())
x = np.arange(len(per))
fig, ax = plt.subplots(figsize=(LARG, 3.6))
outras = ["inovação e tecnologia", "inserção internacional", "trabalho e renda", "digital"]
desloc = {"trabalho e renda": -5, "digital": 2.5}       # afasta rótulos que terminam no mesmo ponto
for d in outras:
    g = t[t.dimensao == d].set_index("periodo").loc[per]
    ax.plot(x, g.taxa_por_mil, color="#a9a89f", lw=1.4, marker="o", ms=3.5)
    ax.text(x[-1] + 0.12, g.taxa_por_mil.iloc[-1] + desloc.get(d, 0), d, fontsize=8.5, color=TINTA2, va="center")
g = t[t.dimensao == "competitividade e produção"].set_index("periodo").loc[per]
ax.fill_between(x, g.ic_inf, g.ic_sup, color=SERIES[0], alpha=0.15, lw=0)
ax.plot(x, g.taxa_por_mil, color=SERIES[0], lw=2.4, marker="o", ms=5, markeredgecolor="white", markeredgewidth=1)
ax.text(x[-1] + 0.12, g.taxa_por_mil.iloc[-1] + 5, "competitividade\ne produção", fontsize=9, color=SERIES[0],
        va="center", fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(per)
ax.set_xlim(-0.3, len(per) + 0.9)
ax.set_ylim(0, None)
ax.set_ylabel("ocorrências por mil lemas")
limpa(ax)
fig.tight_layout()
salvar(fig, "doc_lexico.png")

# ------------------------------------------------------------------ 2. cenário de curadoria
c = pd.read_csv(S / "cenario_curadoria_comparacao.csv", encoding="utf-8")
paineis = [("taxa por mil lemas: competitividade e produção", "Competitividade e produção\n(por mil lemas)"),
           ("taxa por mil lemas: trabalho e renda", "Trabalho e renda\n(por mil lemas)"),
           ("% do PPA: crédito", "Crédito\n(% do valor do PPA)")]
fig, axes = plt.subplots(1, 3, figsize=(LARG, 2.7))
for ax, (bloco, nome) in zip(axes, paineis):
    g = c[c.bloco == bloco]
    xx = np.arange(len(g))
    ax.plot(xx, g["antes"], color="#a9a89f", lw=1.6, ls="--", marker="o", ms=3)
    ax.plot(xx, g["depois"], color=SERIES[0], lw=2, marker="o", ms=4)
    ax.set_title(nome, fontsize=9.5, loc="left", color=TINTA, fontweight="bold")
    ax.set_xticks(xx)
    ax.set_xticklabels([CURTO(p) for p in g["item"]], fontsize=7.5, rotation=45, ha="right")
    ax.set_ylim(0, None)
    limpa(ax)
from matplotlib.lines import Line2D  # noqa: E402
fig.legend([Line2D([], [], color="#a9a89f", ls="--", lw=1.6), Line2D([], [], color=SERIES[0], lw=2)],
           ["antes: lista atual (42 programas)", "depois: com 8 programas a mais (50)"],
           loc="lower center", ncol=2, frameon=False, fontsize=8.5)
fig.tight_layout(rect=(0, 0.09, 1, 1))
salvar(fig, "doc_cenario.png")

# ------------------------------------------------------------------ 3. instrumentos
v = pd.read_csv(S / "valores_instrumentos.csv", encoding="utf-8")
per = v.periodo.tolist()
xx = np.arange(len(per))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(LARG, 2.9))
sel = 100 * v.total_programas_selecionados / v.total_documento
bars = a1.bar(xx, sel, color=SERIES[0], width=0.65)
for bb, p in zip(bars, per):
    if p in ("2004-2007", "2008-2011"):
        bb.set_alpha(0.45)
for xi, val in zip(xx, sel):
    a1.text(xi, val + 0.06, f"{val:.1f}".replace(".", ","), ha="center", fontsize=8, color=TINTA)
a1.set_title("Programas selecionados\n(% do valor do PPA)", fontsize=9.5, loc="left", fontweight="bold", color=TINTA)
cr = v["crédito / financiamento | % documento"]
a2.plot(xx, cr, color=SERIES[0], lw=2, marker="o", ms=4)
for xi, val in zip(xx, cr):
    a2.text(xi, val + 0.05, f"{val:.1f}".replace(".", ","), ha="center", fontsize=8, color=TINTA)
outros = v["APL / arranjo produtivo | % documento"] + v["incubadora / parque / centro de inovação | % documento"]
a2.plot(xx, outros, color="#a9a89f", lw=1.4, marker="o", ms=3)
a2.text(xx[-1], outros.iloc[-1] + 0.07, "APL + incubadoras", fontsize=8, color=TINTA2, ha="right")
a2.set_title("Crédito nas subações\n(% do valor do PPA)", fontsize=9.5, loc="left", fontweight="bold", color=TINTA)
for ax in (a1, a2):
    ax.set_xticks(xx)
    ax.set_xticklabels([CURTO(p) for p in per], fontsize=8)
    ax.set_ylim(0, None)
    limpa(ax)
fig.tight_layout()
salvar(fig, "doc_instrumentos.png")

# ------------------------------------------------------------------ 4. ODS
o = pd.read_csv(S / "ods_taxas.csv", encoding="utf-8")
o = o[(o.corpus == "PPA inteiro") & (o.ods != "todos os ODS")].copy()
o["ods"] = o.ods.astype(int)
ods = pd.read_csv(S.parent / "dados" / "ods" / "ods_metas_onu_brasil.csv", encoding="utf-8")
tit = ods.groupby("ods").titulo.first()
curto = {3: "Saúde e bem-estar", 8: "Trabalho decente e crescimento", 9: "Indústria, inovação, infraestrutura",
         11: "Cidades sustentáveis", 12: "Consumo e produção responsáveis", 13: "Ação contra a mudança do clima",
         16: "Paz, justiça e instituições", 17: "Parcerias e implementação", 2: "Fome zero e agricultura"}
m = o.pivot(index="ods", columns="periodo", values="taxa_por_mil").sort_index()
fig, ax = plt.subplots(figsize=(LARG, 5.6))
ax.imshow(m.values, cmap="Blues", aspect="auto", vmin=0, vmax=m.values.max() * 1.05)
for a in range(m.shape[0]):
    for b in range(m.shape[1]):
        val = m.values[a, b]
        ax.text(b, a, f"{val:.1f}".replace(".", ","), ha="center", va="center", fontsize=8,
                color="white" if val > m.values.max() * 0.6 else TINTA)
ax.set_xticks(range(m.shape[1]))
ax.set_xticklabels(m.columns, fontsize=8.5)
ax.xaxis.tick_top()
ax.set_yticks(range(m.shape[0]))
ax.set_yticklabels([f"{i}. {curto.get(i, tit[i])}" for i in m.index], fontsize=8.5)
ax.axvline(2.5, color=TINTA, lw=1.2, ls="--")
ax.tick_params(length=0)
for s_ in ax.spines.values():
    s_.set_visible(False)
fig.tight_layout()
salvar(fig, "doc_ods.png")
