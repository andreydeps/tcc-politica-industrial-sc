"""Figura antes x depois do cenário de curadoria (lê saidas/cenario_curadoria_comparacao.csv)."""
from pathlib import Path

import numpy as np
import pandas as pd

from estilo import CINZA, SERIES, TINTA2, eixo_limpo, plt, salvar, titulo

SAIDAS = Path(__file__).resolve().parent.parent / "saidas"
t = pd.read_csv(SAIDAS / "cenario_curadoria_comparacao.csv", encoding="utf-8")
paineis = [
    ("taxa por mil lemas: competitividade e produção", "Competitividade e produção", "por mil lemas", "não muda: resultado robusto"),
    ("taxa por mil lemas: trabalho e renda", "Trabalho e renda", "por mil lemas", "muda: o pico de 2024-27 dependia da curadoria"),
    ("% do PPA: crédito", "Crédito no valor do PPA", "% do PPA", "a queda fica mais forte"),
]
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
for ax, (bloco, nome, unid, sub) in zip(axes, paineis):
    g = t[t.bloco == bloco]
    x = np.arange(len(g))
    ax.plot(x, g["antes"], color=CINZA, lw=2, ls="--", marker="o", ms=5, label="antes (lista oficial, 42 programas)")
    ax.plot(x, g["depois"], color=SERIES[0], lw=2, marker="o", ms=6, markeredgecolor="white", markeredgewidth=1.2,
            label="depois (+0530, 0101, 0204: 50 programas)")
    ax.set_xticks(x)
    ax.set_xticklabels([p[:4] + "-" + p[-2:] for p in g["item"]], fontsize=8.5)
    ax.set_ylim(bottom=0)
    ax.set_ylabel(unid, fontsize=9)
    eixo_limpo(ax)
    titulo(ax, nome, sub)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=2, frameon=False, fontsize=9, labelcolor=TINTA2)
fig.tight_layout(rect=(0, 0.07, 1, 1))
salvar(fig, "cenario_antes_depois.png")
