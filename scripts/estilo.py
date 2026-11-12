"""Estilo comum das figuras do TCC (paleta validada, marcas finas, grade discreta).

Cores categóricas na ordem fixa da paleta de referência (slots 1 a 5); texto sempre em
tinta neutra, nunca na cor da série; cinza para referências e controles.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"

FUNDO = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
CINZA = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]   # azul, laranja, água, amarelo, magenta
AZUIS = "Blues"

plt.rcParams.update({
    "font.family": ["Arial", "DejaVu Sans"],
    "axes.edgecolor": CINZA,
    "axes.labelcolor": TINTA2,
    "xtick.color": TINTA2,
    "ytick.color": TINTA2,
    "figure.facecolor": FUNDO,
    "axes.facecolor": FUNDO,
    "savefig.facecolor": FUNDO,
})


def eixo_limpo(ax, grade="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_visible(grade != "y")
    ax.tick_params(length=0, labelsize=9)
    if grade:
        ax.grid(axis=grade, color=CINZA, alpha=0.4, lw=0.6)
        ax.set_axisbelow(True)


def titulo(ax, texto, sub=None):
    ax.set_title(texto, loc="left", fontsize=11.5, fontweight="bold", color=TINTA, pad=18 if sub else 8)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=8.5, color=TINTA2, va="bottom")


def salvar(fig, nome):
    caminho = SAIDAS / nome
    fig.savefig(caminho, dpi=170, bbox_inches="tight")
    print("figura:", caminho)
    return caminho
