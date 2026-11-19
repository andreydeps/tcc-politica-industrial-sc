"""Figura conceitual do método: separa a estrutura do documento (PDF, programa, campo)
da classificação analítica (o que é política industrial) e do tratamento do texto.

Saída: saidas/figura_conceitual_metodo.png (escala de cinza, para ficar legível impressa).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

RAIZ = Path(__file__).resolve().parent.parent
plt.rcParams["font.family"] = ["Arial", "DejaVu Sans"]
INK, MUTED, LINE, FILL = "#111111", "#555555", "#444444", "#e9e9e7"

fig, ax = plt.subplots(figsize=(13, 7.6))
ax.set_xlim(0, 100)
ax.set_ylim(-6, 60)
ax.axis("off")


def caixa(x, y, w, h, titulo, linhas=(), fundo="white", negrito=True, tam=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8",
                                fc=fundo, ec=LINE, lw=1.1))
    ax.text(x + w / 2, y + h - 1.6, titulo, ha="center", va="top", fontsize=tam,
            fontweight="bold" if negrito else "normal", color=INK)
    for i, l in enumerate(linhas):
        ax.text(x + w / 2, y + h - 4.3 - 2.3 * i, l, ha="center", va="top", fontsize=8.4, color=MUTED)


def seta(x1, y1, x2, y2, estilo="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=estilo, mutation_scale=14, lw=1.2, color=LINE))


def faixa(y, h, rotulo):
    ax.text(0.5, y + h + 0.6, rotulo, fontsize=10.5, fontweight="bold", color=INK, va="bottom")
    ax.plot([0.5, 99.5], [y + h + 0.3, y + h + 0.3], color="#bdbdbb", lw=0.8)


# ---------------- faixa 1: estrutura do documento
faixa(40, 15, "1. Estrutura do documento (o que está escrito no PPA)")
caixa(1, 40, 20, 15, "PPA", ["Anexo Único (PDF)", "um por ciclo:", "2004-2007 a 2024-2027"])
caixa(27, 40, 22, 15, "Programa", ["unidade de planejamento", "identificada por código", "de 4 dígitos (ex.: 0200)"])
caixa(55, 40, 44, 15, "Campos do programa (seções)", [])
for i, c in enumerate(["nome", "órgão", "objetivo", "justificativa", "público-alvo", "subações"]):
    destaque = c in ("objetivo", "justificativa", "público-alvo", "subações")
    x = 56.2 + i * 7.1
    ax.add_patch(FancyBboxPatch((x, 41.8), 6.5, 6.6, boxstyle="round,pad=0.15,rounding_size=0.5",
                                fc=FILL if destaque else "white", ec=LINE, lw=1.0 if destaque else 0.7))
    ax.text(x + 3.25, 45.1, c, ha="center", va="center", fontsize=7.8, color=INK,
            fontweight="bold" if destaque else "normal")
seta(21.4, 47.5, 26.6, 47.5)
seta(49.4, 47.5, 54.6, 47.5)
ax.text(77, 39.2, "extração automática (regex por formato; os rótulos só delimitam, não classificam)",
        ha="center", va="top", fontsize=8, color=MUTED, style="italic")

# ---------------- faixa 2: recortes e material analisado
faixa(19, 14, "2. Recortes e material analisado")
caixa(1, 19, 30, 14, "Plano inteiro", ["todos os programas dos seis PPAs", "(529 códigos distintos)", "base de todas as medidas"], fundo=FILL)
caixa(37, 19, 29, 14, "Política industrial (recorte)", ["seleção manual pelo conceito", "(Chang, 1994; Rodrik, 2004, 2008)", "42 pares programa-PPA"], fundo=FILL)
caixa(72, 19, 27, 14, "Material", ["texto: objetivo + justificativa", "subações: nome e valor orçado",
                                    "público-alvo: categorias"], fundo=FILL)
seta(31.4, 26, 36.6, 26)
seta(66.4, 26, 71.6, 26)
seta(29.5, 39.4, 29.5, 33.8)    # programas extraídos -> plano inteiro

# ---------------- faixa 3: tratamento e análise
faixa(0, 14, "3. Tratamento e análises (sempre plano inteiro x política industrial)")
caixa(1, 0, 25, 14, "Pré-processamento", ["lematização (spaCy, pt_core_news_lg)", "minúsculas, sem stopwords", "substantivo, verbo, adjetivo"])
caixa(31, 0, 68, 14, "Análises por PPA", [])
for i, (t, d) in enumerate([("Temas", "% dos lemas"), ("Testes", "permutação"), ("Palavras", "características, n-gramas"),
                            ("Texto copiado", "entre planos"), ("Orçamento", "% do PPA e R$ (IPCA)"),
                            ("Público-alvo", "quem recebe")]):
    x = 32.2 + i * 11.05
    ax.add_patch(FancyBboxPatch((x, 1.6), 10.1, 7.6, boxstyle="round,pad=0.15,rounding_size=0.5", fc="white", ec=LINE, lw=0.8))
    ax.text(x + 5.05, 7.1, t, ha="center", va="center", fontsize=8.4, fontweight="bold", color=INK)
    ax.text(x + 5.05, 4.1, d, ha="center", va="center", fontsize=6.9, color=MUTED)
seta(26.4, 7, 30.6, 7)
seta(85.5, 18.7, 85.5, 14.6)   # material -> análises

ax.text(0.5, -3.2, "Programa e campo são categorias do documento. \"Política industrial\" é uma classificação feita pelo pesquisador "
        "sobre os programas e é analisada como recorte do plano inteiro.", fontsize=8.6, color=MUTED, va="top")
fig.tight_layout()
saida = RAIZ / "saidas" / "figura_conceitual_metodo.png"
fig.savefig(saida, dpi=200, facecolor="white", bbox_inches="tight")
print("ok:", saida)
