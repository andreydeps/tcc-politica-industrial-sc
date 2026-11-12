"""Índice de discurso por dimensão do léxico, com testes de robustez.

Entrada : um CSV de léxico (termo, dimensao e uma coluna de status: decisao ou proposta)
          e um corpus (programas: objetivo + justificativa; acoes: nomes de ações e subações)
Saídas  : saidas/indice_lexico_<corpus>.csv          taxa por período e dimensão, com IC 95%
          saidas/indice_lexico_<corpus>_testes.csv   testes por dimensão
          saidas/indice_lexico_<corpus>.png          figura

Uso:
    python scripts/indice_lexico.py --lexico saidas/lexico_proposta.csv --corpus programas
    python scripts/indice_lexico.py --lexico saidas/lexico_proposta.csv --corpus acoes

Para cada dimensão (inovação e tecnologia, competitividade e produção, inserção internacional,
trabalho e renda, digital) e para o léxico inteiro:
- taxa: ocorrências dos termos da dimensão por 1000 lemas, em cada período;
- bootstrap: IC 95% reamostrando programas dentro do período;
- permutação: o período dos programas é embaralhado; p = chance de o acaso dar trajetória
  tão grande (amplitude) ou tão ordenada no tempo (tendência);
- léxicos aleatórios: 1000 léxicos com o mesmo número de termos, cada termo trocado por um
  sorteado entre os 25 de frequência mais próxima. Percentil = em quantos % deles a trajetória
  é menor que a observada. É a resposta à circularidade para o léxico expandido: se a dimensão
  não destoa de um léxico qualquer, a escolha dos termos é que estaria produzindo o resultado.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from circularidade import amplitude_rel, tendencia
from estilo import CINZA, SERIES, TINTA, TINTA2, eixo_limpo, plt, salvar

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
RNG = np.random.default_rng(42)
ARQ = {"programas": "corpus_programas.csv", "acoes": "corpus_acoes.csv",
       "cenario": "corpus_programas_cenario.csv"}   # cenário de curadoria (scripts/cenario_curadoria.py)


def taxa(serie, ntok, pidx, nper):
    return np.bincount(pidx, weights=serie, minlength=nper) / np.bincount(pidx, weights=ntok, minlength=nper) * 1000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lexico", default=str(SAIDAS / "lexico_proposta.csv"))
    ap.add_argument("--corpus", choices=list(ARQ), default="programas")
    ap.add_argument("--incluir", default="entra,variante", help="status que contam como aceitos")
    ap.add_argument("--perm", type=int, default=3000)
    ap.add_argument("--aleatorios", type=int, default=1000)
    a = ap.parse_args()

    lex = pd.read_csv(a.lexico, encoding="utf-8")
    col = "decisao" if "decisao" in lex.columns and lex["decisao"].notna().any() else "proposta"
    aceitos = lex[lex[col].isin(a.incluir.split(",")) & lex["dimensao"].notna()]
    print(f"Léxico: {a.lexico} | status lido de '{col}' | {len(aceitos)} termos aceitos")

    df = pd.read_csv(SAIDAS / ARQ[a.corpus], encoding="utf-8", dtype={"codigo": str})
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    periodos = sorted(df["periodo"].unique())
    nper = len(periodos)
    pidx = df["periodo"].map({p: i for i, p in enumerate(periodos)}).to_numpy()
    cv = CountVectorizer(token_pattern=r"\S+", lowercase=False)
    X = cv.fit_transform(df["texto_lematizado"]).toarray().astype(float)
    vocab = list(cv.get_feature_names_out())
    ix = {t: i for i, t in enumerate(vocab)}
    ntok = X.sum(axis=1)
    freq = X.sum(axis=0)
    print(f"Corpus: {a.corpus} | {len(df)} documentos | {int(ntok.sum())} lemas | períodos {periodos}")

    dims = {d: [t for t in g["termo"] if t in ix] for d, g in aceitos.groupby("dimensao")}
    ausentes = sorted(set(aceitos["termo"]) - set(ix))
    if ausentes:
        print("Termos do léxico que não aparecem neste corpus:", ", ".join(ausentes))
    dims["léxico inteiro"] = sorted({t for ts in dims.values() for t in ts})
    lexset = set(dims["léxico inteiro"])
    pool = np.array([i for i, t in enumerate(vocab) if t not in lexset and freq[i] >= 1])

    def vizinhos(j, k=25):
        d = np.abs(np.log(freq[pool] / freq[j]))
        return pool[np.argsort(d, kind="stable")[:k]]

    idx_periodo = [np.where(pidx == i)[0] for i in range(nper)]
    linhas_taxa, linhas_teste, fig_dados = [], [], {}
    for d, termos in dims.items():
        if not termos:
            continue
        cols = [ix[t] for t in termos]
        serie = X[:, cols].sum(axis=1)
        obs = taxa(serie, ntok, pidx, nper)
        amp = amplitude_rel(obs[:, None])[0]
        tr = tendencia(obs[:, None])[0]

        # bootstrap
        boot = np.zeros((2000, nper))
        for b in range(2000):
            for i in range(nper):
                s = RNG.choice(idx_periodo[i], size=len(idx_periodo[i]), replace=True)
                boot[b, i] = serie[s].sum() / ntok[s].sum() * 1000
        lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)

        # permutação
        ca = ct = 0
        for _ in range(a.perm):
            pm = taxa(serie, ntok, RNG.permutation(pidx), nper)
            ca += amplitude_rel(pm[:, None])[0] >= amp
            ct += abs(tendencia(pm[:, None])[0]) >= abs(tr)
        p_amp, p_tr = (1 + ca) / (a.perm + 1), (1 + ct) / (a.perm + 1)

        # léxicos aleatórios de mesma frequência
        viz = [vizinhos(j) for j in cols]
        amps, trs, trajs = [], [], []
        for _ in range(a.aleatorios):
            esc = [RNG.choice(v) for v in viz]
            r = taxa(X[:, esc].sum(axis=1), ntok, pidx, nper)
            if r.mean() == 0:
                continue
            amps.append(amplitude_rel(r[:, None])[0])
            trs.append(abs(tendencia(r[:, None])[0]))
            trajs.append(r / r.mean())
        amps, trs, trajs = np.array(amps), np.array(trs), np.array(trajs)
        pct_amp = float(np.mean(amps <= amp) * 100)
        pct_tr = float(np.mean(trs <= abs(tr)) * 100)

        for i, p in enumerate(periodos):
            linhas_taxa.append({"dimensao": d, "periodo": p, "taxa_por_mil": round(obs[i], 2),
                                "ic_inf": round(lo[i], 2), "ic_sup": round(hi[i], 2)})
        linhas_teste.append({"dimensao": d, "n_termos": len(termos), "termos": ", ".join(termos),
                             "ocorrencias": int(serie.sum()), "amplitude_rel": round(amp, 2),
                             "tendencia_spearman": round(tr, 2), "p_perm_amplitude": round(p_amp, 4),
                             "p_perm_tendencia": round(p_tr, 4), "pct_lexicos_aleatorios_amplitude": round(pct_amp, 1),
                             "pct_lexicos_aleatorios_tendencia": round(pct_tr, 1)})
        fig_dados[d] = (obs, lo, hi, np.percentile(trajs, [5, 95], axis=0) * obs.mean(), p_amp, pct_amp, tr, p_tr)

    t1, t2 = pd.DataFrame(linhas_taxa), pd.DataFrame(linhas_teste)
    t1.to_csv(SAIDAS / f"indice_lexico_{a.corpus}.csv", index=False, encoding="utf-8")
    t2.to_csv(SAIDAS / f"indice_lexico_{a.corpus}_testes.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 230)
    print("\n=== Taxa por 1000 lemas ===")
    print(t1.pivot(index="dimensao", columns="periodo", values="taxa_por_mil").to_string())
    print("\n=== Testes ===")
    print(t2.drop(columns=["termos"]).to_string(index=False))

    # figura: um painel por dimensão, escala própria
    ordem = [d for d in ["inovação e tecnologia", "competitividade e produção", "inserção internacional",
                         "trabalho e renda", "digital", "léxico inteiro"] if d in fig_dados]
    ncol = 3
    nlin = int(np.ceil(len(ordem) / ncol))
    fig, axes = plt.subplots(nlin, ncol, figsize=(15, 4.3 * nlin), squeeze=False)
    xs = np.arange(nper)
    for k, d in enumerate(ordem):
        ax = axes.flat[k]
        obs, lo, hi, env, p_amp, pct_amp, tr, p_tr = fig_dados[d]
        ax.fill_between(xs, env[0], env[1], color=CINZA, alpha=0.5, lw=0, label="léxicos aleatórios (5%–95%)")
        ax.fill_between(xs, lo, hi, color=SERIES[0], alpha=0.18, lw=0, label="IC 95% (bootstrap)")
        ax.plot(xs, obs, color=SERIES[0], lw=2, marker="o", ms=6, markeredgecolor="white", markeredgewidth=1.2,
                label="dimensão")
        ax.set_xticks(xs)
        ax.set_xticklabels([p[:4] + "-" + p[-2:] for p in periodos], fontsize=8.5)
        ax.set_ylim(bottom=0)
        eixo_limpo(ax)
        ax.set_title(d, loc="left", fontsize=11, fontweight="bold", color=TINTA, pad=18)
        sentido = "sobe" if tr > 0 else "cai"
        ax.text(0, 1.02, f"tendência {sentido} (ρ={tr:+.2f}, p={p_tr:.3f}) | amplitude p={p_amp:.3f}, "
                f"acima de {pct_amp:.0f}% dos léxicos aleatórios", transform=ax.transAxes, fontsize=7.4,
                color=TINTA2, va="bottom")
        if k % ncol == 0:
            ax.set_ylabel("ocorrências por 1000 lemas", fontsize=9)
    for ax in axes.flat[len(ordem):]:
        ax.axis("off")
    h, l = axes.flat[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=9, labelcolor=TINTA2)
    rotulo = "objetivo + justificativa" if a.corpus == "programas" else "nomes das ações e subações"
    fig.suptitle(f"Dimensões do léxico ao longo dos PPAs ({rotulo})", x=0.01, ha="left", fontsize=13,
                 fontweight="bold", color=TINTA)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    salvar(fig, f"indice_lexico_{a.corpus}.png")


if __name__ == "__main__":
    main()
