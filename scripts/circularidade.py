"""Checagem de circularidade dos termos-chave (lexical + semântica).

A crítica: "usar palavra-chave para achar palavra-chave". A resposta aqui compara o
comportamento de cada termo-chave com (i) o acaso e (ii) termos de controle de mesma
frequência, sem depender de ele ter sido escolhido à mão.

Entrada : saidas/corpus_programas.csv (gerado pelo notebook)
Saídas  : saidas/circularidade_resumo*.csv, saidas/circularidade_ranking*.csv,
          saidas/circularidade_termos_chave_vs_controles*.png

Uso:
    python scripts/circularidade.py                 # todos os programas
    python scripts/circularidade.py --dedup         # sensibilidade: remove textos idênticos
    python scripts/circularidade.py --sementes inovação competitividade ...

Três testes por termo-chave (cada um responde a uma pergunta diferente):

A) PERMUTAÇÃO. "A trajetória no tempo é maior do que se os programas tivessem sido
   sorteados entre os períodos?" Embaralha o rótulo de período dos programas (mantendo o
   tamanho de cada período) e vê quantas vezes a amplitude/tendência observada é superada.
B) CONTROLES POR FREQUÊNCIA. "Esse termo se mexe mais do que outros termos qualquer com
   a mesma frequência?" Pega os 25 termos de frequência mais próxima e compara. É a
   resposta direta à circularidade: se os termos-chave não destoam dos controles, a
   escolha deles não está produzindo o resultado.
C) BOOTSTRAP. Intervalo de confiança de 95% da trajetória, reamostrando programas dentro
   de cada período (mostra o quanto o resultado depende de poucos programas).

Duas medidas, para não depender só de a palavra aparecer escrita:
- LEXICAL : taxa do termo por 1000 lemas em cada período.
- SEMÂNTICA: similaridade (cosseno) entre o termo e cada programa, usando vetores do spaCy
  (vetor do programa = média dos vetores dos seus lemas, SEM contar o próprio termo,
  para não premiar quem só repete a palavra). Pega tema escrito com outras palavras
  (ex.: "computador", "rede" em vez de "digital").
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spacy
from scipy.stats import rankdata
from sklearn.feature_extraction.text import CountVectorizer

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
RNG = np.random.default_rng(42)

AZUL, TXT1, TXT2, FUNDO, CINZA = "#2a78d6", "#0b0b0b", "#52514e", "#fcfcfb", "#c3c2b7"


# ----------------------------------------------------------------------------- dados
def carrega(dedup, arquivo="corpus_programas.csv"):
    df = pd.read_csv(SAIDAS / arquivo, encoding="utf-8", dtype={"codigo": str})
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    if dedup:
        df = df.drop_duplicates("texto_lematizado")
    df = df.reset_index(drop=True)
    periodos = sorted(df["periodo"].unique())
    pidx = df["periodo"].map({p: i for i, p in enumerate(periodos)}).to_numpy()
    cv = CountVectorizer(token_pattern=r"\S+", lowercase=False)
    X = cv.fit_transform(df["texto_lematizado"]).toarray().astype(float)   # programa x termo
    vocab = list(cv.get_feature_names_out())
    return df, periodos, pidx, X, vocab


# ----------------------------------------------------------------------------- estatísticas
def amplitude_rel(m):
    """(máx - mín) / média, por coluna: variação relativa ao próprio nível do termo."""
    mu = m.mean(axis=0)
    mu = np.where(mu == 0, np.nan, mu)
    return (m.max(axis=0) - m.min(axis=0)) / mu


def amplitude_abs(m):
    return m.max(axis=0) - m.min(axis=0)


def tendencia(m):
    """Correlação de Spearman entre o tempo e o valor (ordem dos períodos), por coluna."""
    r = rankdata(m, axis=0)
    t = np.arange(1, m.shape[0] + 1, dtype=float)
    r = r - r.mean(axis=0)
    t = t - t.mean()
    den = np.sqrt((r ** 2).sum(axis=0) * (t ** 2).sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        out = (r * t[:, None]).sum(axis=0) / den
    return np.nan_to_num(out)


def taxa_por_periodo(X, ntok, pidx, nper):
    """Taxa por 1000 lemas em cada período (períodos x termos)."""
    P = np.eye(nper)[pidx]                       # programa x período (one-hot)
    return (P.T @ X) / (P.T @ ntok)[:, None] * 1000


def media_por_periodo(valores, pidx, nper):
    """Média por período de um vetor por programa, ignorando NaN."""
    ok = ~np.isnan(valores)
    soma = np.bincount(pidx[ok], weights=valores[ok], minlength=nper)
    n = np.bincount(pidx[ok], minlength=nper)
    with np.errstate(invalid="ignore", divide="ignore"):
        return soma / n


def p_perm(obs, estat, serie_prog, pidx, nper, taxa=None, ntok=None, B=5000):
    """p-valor de permutação (unilateral: valor permutado >= observado)."""
    cont = 0
    for _ in range(B):
        perm = RNG.permutation(pidx)
        if taxa is not None:      # lexical: contagem do termo / lemas por período
            m = np.bincount(perm, weights=serie_prog, minlength=nper) / np.bincount(perm, weights=ntok, minlength=nper) * 1000
        else:                     # semântico: média do escore por período
            m = media_por_periodo(serie_prog, perm, nper)
        if not np.all(np.isfinite(m)):
            continue
        v = estat(m[:, None])[0]
        cont += (v >= obs)
    return (1 + cont) / (B + 1)


def bootstrap_ci(serie_prog, pidx, nper, ntok=None, B=2000):
    """IC 95% por período, reamostrando programas dentro de cada período."""
    idx = [np.where(pidx == i)[0] for i in range(nper)]
    out = np.zeros((B, nper))
    for b in range(B):
        for i in range(nper):
            s = RNG.choice(idx[i], size=len(idx[i]), replace=True)
            if ntok is not None:
                out[b, i] = serie_prog[s].sum() / ntok[s].sum() * 1000
            else:
                out[b, i] = np.nanmean(serie_prog[s])
    return np.nanpercentile(out, [2.5, 97.5], axis=0)


# ----------------------------------------------------------------------------- semântica
def escores_semanticos(nlp, X, vocab, termos_idx):
    """Cosseno programa x termo, para cada termo em termos_idx, com o termo removido do programa."""
    tem_vet = np.array([nlp.vocab[t].has_vector for t in vocab])
    W = np.array([nlp.vocab[t].vector if h else np.zeros(300) for t, h in zip(vocab, tem_vet)])
    # centralização: tira a direção comum a todas as palavras (ver embeddings_candidatos.py)
    cont = X[:, tem_vet].sum(axis=0)
    mu = (cont[:, None] * W[tem_vet]).sum(axis=0) / cont.sum()
    W = np.where(tem_vet[:, None], W - mu, 0.0)
    S = X @ W                                         # soma dos vetores dos lemas de cada programa
    nvet = X[:, tem_vet].sum(axis=1)
    res = {}
    for t in termos_idx:
        if not tem_vet[t]:
            continue
        c = X[:, t]
        soma = S - c[:, None] * W[t]                  # remove o próprio termo do programa
        n = nvet - c
        with np.errstate(invalid="ignore", divide="ignore"):
            vp = soma / n[:, None]
            cos = (vp @ W[t]) / (np.linalg.norm(vp, axis=1) * np.linalg.norm(W[t]))
        cos[n <= 0] = np.nan
        res[t] = cos
    return res, tem_vet


# ----------------------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sementes", nargs="+", default=["inovação", "competitividade", "digital", "internacional", "emprego"])
    ap.add_argument("--dedup", action="store_true")
    ap.add_argument("--controles", type=int, default=25)
    ap.add_argument("--perm", type=int, default=5000)
    ap.add_argument("--arquivo", default="corpus_programas.csv", help="corpus em saidas/ (ex.: cenário de curadoria)")
    ap.add_argument("--sufixo", default="", help="sufixo dos arquivos de saída")
    a = ap.parse_args()
    suf = ("_dedup" if a.dedup else "") + a.sufixo

    df, periodos, pidx, X, vocab = carrega(a.dedup, a.arquivo)
    nper = len(periodos)
    ntok = X.sum(axis=1)
    freq = X.sum(axis=0)
    ix = {t: i for i, t in enumerate(vocab)}
    sementes = [s for s in a.sementes if s in ix]
    print(f"Programas: {len(df)} | períodos: {periodos} | lemas distintos: {len(vocab)} | dedup={a.dedup}")
    print("Programas por período:", dict(zip(periodos, np.bincount(pidx))))
    print("Lemas por período:", dict(zip(periodos, np.bincount(pidx, weights=ntok).astype(int))))

    nlp = spacy.load("pt_core_news_lg", disable=["tagger", "parser", "ner", "lemmatizer", "attribute_ruler"])
    taxa = taxa_por_periodo(X, ntok, pidx, nper)                       # períodos x termos

    # pool de controles: lemas com frequência >= 2 e vetor, fora das sementes
    tem_vet0 = np.array([nlp.vocab[t].has_vector for t in vocab])
    pool = np.array([i for i in range(len(vocab)) if freq[i] >= 2 and tem_vet0[i] and vocab[i] not in sementes])
    controles = {}
    for s in sementes:
        d = np.abs(np.log(freq[pool] / freq[ix[s]]))
        controles[s] = pool[np.argsort(d, kind="stable")[: a.controles]]

    todos_idx = sorted({ix[s] for s in sementes} | {i for c in controles.values() for i in c})
    esc, tem_vet = escores_semanticos(nlp, X, vocab, todos_idx)
    sem_mat = {t: media_por_periodo(v, pidx, nper) for t, v in esc.items()}   # média do escore por período

    # ------------------------------------------------------------------ resumo por termo
    linhas, fig_dados = [], {}
    for s in sementes:
        j = ix[s]
        ctrl = controles[s]
        for medida in ("lexical", "semantica"):
            if medida == "lexical":
                traj = taxa[:, j]
                estat_amp, serie, kw = amplitude_rel, X[:, j], dict(taxa=True, ntok=ntok)
                trajs_ctrl = np.column_stack([taxa[:, c] for c in ctrl])
            else:
                if j not in sem_mat:
                    continue
                traj = sem_mat[j]
                estat_amp, serie, kw = amplitude_abs, esc[j], {}
                trajs_ctrl = np.column_stack([sem_mat[c] for c in ctrl if c in sem_mat])
            amp = estat_amp(traj[:, None])[0]
            tr = abs(tendencia(traj[:, None])[0])
            amp_c = estat_amp(trajs_ctrl)
            tr_c = np.abs(tendencia(trajs_ctrl))
            p_amp = p_perm(amp, estat_amp, serie, pidx, nper, B=a.perm, **kw)
            p_tr = p_perm(tr, lambda m: np.abs(tendencia(m)), serie, pidx, nper, B=a.perm, **kw)
            ci = bootstrap_ci(X[:, j], pidx, nper, ntok=ntok) if medida == "lexical" else bootstrap_ci(esc[j], pidx, nper)
            linhas.append({
                "termo": s, "medida": medida, "freq_corpus": int(freq[j]),
                "amplitude": round(float(amp), 3), "p_perm_amplitude": round(p_amp, 4),
                "tendencia_abs": round(float(tr), 3), "p_perm_tendencia": round(p_tr, 4),
                "pct_acima_controles_amplitude": round(float(np.nanmean(amp_c <= amp) * 100), 0),
                "pct_acima_controles_tendencia": round(float(np.nanmean(tr_c <= tr) * 100), 0),
            })
            fig_dados[(s, medida)] = (traj, ci, trajs_ctrl)

    res = pd.DataFrame(linhas)
    res.to_csv(SAIDAS / f"circularidade_resumo{suf}.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    print("\n=== RESUMO (p pequeno = trajetória maior que o acaso; pct = % de controles que o termo supera) ===")
    print(res.to_string(index=False))

    print("\n=== TRAJETÓRIAS por período (lexical: taxa por 1000 lemas | semântica: cosseno médio com o termo) ===")
    print(" " * 26 + "  ".join(f"{p:>9}" for p in periodos))
    for (s, medida), (traj, ci, tc) in fig_dados.items():
        fmt = "{:9.2f}" if medida == "lexical" else "{:9.3f}"
        print(f"{s:<16}{medida:<10}" + "  ".join(fmt.format(v) for v in traj))
        print(f"{'':<26}" + "  ".join(f"[{lo:.1f},{hi:.1f}]".rjust(9) if medida == "lexical" else f"[{lo:.2f},{hi:.2f}]".rjust(9)
                                      for lo, hi in zip(ci[0], ci[1])))

    # ------------------------------------------------------------------ ranking no vocabulário
    elegiveis = np.array([i for i in range(len(vocab)) if freq[i] >= 2])
    rk = []
    for s in sementes:
        linha = {"termo": s, "freq": int(freq[ix[s]])}
        for k, p in enumerate(periodos):
            r = rankdata(-taxa[k, elegiveis], method="min")
            pos = np.where(elegiveis == ix[s])[0][0]
            linha[p] = int(r[pos]) if taxa[k, ix[s]] > 0 else None
        rk.append(linha)
    rk = pd.DataFrame(rk)
    rk.to_csv(SAIDAS / f"circularidade_ranking{suf}.csv", index=False, encoding="utf-8")
    print(f"\n=== POSIÇÃO NO VOCABULÁRIO (1 = termo mais frequente do período; {len(elegiveis)} lemas com freq>=2) ===")
    print(rk.to_string(index=False))

    # ------------------------------------------------------------------ figura
    plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "axes.edgecolor": CINZA})
    fig, axes = plt.subplots(2, len(sementes), figsize=(4.3 * len(sementes), 7.4), facecolor=FUNDO)
    xs = np.arange(nper)
    for col, s in enumerate(sementes):
        for lin, medida in enumerate(("lexical", "semantica")):
            ax = axes[lin, col]
            ax.set_facecolor(FUNDO)
            if (s, medida) not in fig_dados:
                ax.axis("off"); continue
            traj, ci, tc = fig_dados[(s, medida)]
            if medida == "lexical":
                nivel = traj.mean()
                f = lambda v: v / nivel               # índice: 1 = nível médio do próprio termo
                ylabel = "índice (1 = média do termo)"
            else:
                nivel = traj.mean()
                f = lambda v: v - nivel               # desvio em relação à própria média
                ylabel = "cosseno − média do termo"
            ytc = np.column_stack([ (tc[:, i] / tc[:, i].mean() if medida == "lexical" else tc[:, i] - np.nanmean(tc[:, i]))
                                   for i in range(tc.shape[1]) ])
            lo, hi = np.nanpercentile(ytc, [5, 95], axis=1)
            ax.fill_between(xs, lo, hi, color=CINZA, alpha=0.55, linewidth=0, label="controles (5%–95%)")
            ax.fill_between(xs, f(ci[0]), f(ci[1]), color=AZUL, alpha=0.18, linewidth=0, label="IC 95% (bootstrap)")
            ax.plot(xs, f(traj), color=AZUL, lw=2, marker="o", ms=6, markeredgecolor=FUNDO, markeredgewidth=1.5, label="termo-chave")
            ax.axhline(1 if medida == "lexical" else 0, color=CINZA, lw=0.8)
            ax.set_xticks(xs); ax.set_xticklabels(periodos, rotation=45, ha="right", fontsize=8, color=TXT2)
            ax.tick_params(axis="y", labelsize=8, colors=TXT2, length=0); ax.tick_params(axis="x", length=0)
            ax.grid(axis="y", color=CINZA, alpha=0.35, lw=0.6); ax.set_axisbelow(True)
            for sp in ("top", "right", "left"):
                ax.spines[sp].set_visible(False)
            r = res[(res.termo == s) & (res.medida == medida)].iloc[0]
            titulo = f"{s}" + (f" (freq {r['freq_corpus']})" if lin == 0 else "")
            ax.set_title(titulo, fontsize=11, color=TXT1, loc="left", fontweight="bold", pad=18)
            ax.text(0.0, 1.02, f"permutação p={r['p_perm_amplitude']:.3f} | acima de {int(r['pct_acima_controles_amplitude'])}% dos controles",
                    transform=ax.transAxes, fontsize=7.5, color=TXT2, va="bottom")
            if col == 0:
                ax.set_ylabel(("Lexical (taxa por 1000 lemas)\n" if lin == 0 else "Semântica (cosseno com o termo)\n") + ylabel.split("(")[0].strip() + ("" if lin == 0 else ""), fontsize=8, color=TXT2)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=9, labelcolor=TXT2)
    fig.suptitle("Termos-chave contra o acaso e contra termos de controle de mesma frequência", fontsize=13, color=TXT1, x=0.01, ha="left", fontweight="bold")
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    png = SAIDAS / f"circularidade_termos_chave_vs_controles{suf}.png"
    fig.savefig(png, dpi=150, facecolor=FUNDO)
    print("\nFigura:", png)


if __name__ == "__main__":
    main()
