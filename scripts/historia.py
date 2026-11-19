"""A história dos PPAs de SC (notebooks/historia_ppa.ipynb): figuras e tabelas de cada capítulo.

Recupera a narrativa da primeira versão (o que cada plano fala, queda do agro, chegada da inovação,
competitividade no último plano) com todos os 529 programas, ao lado dos 42 pares selecionados.
Medida principal: contagem e % dos lemas. Listas de temas em ppa_inteiro_listas.py.
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo import CINZA, SERIES, TINTA, TINTA2, eixo_limpo, plt, salvar, titulo  # noqa: E402
from ppa_inteiro_analise import PER  # noqa: E402
from ppa_inteiro_listas import AGRO, LEXICO_ATUAL  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
ROT = [q[2:4] + "-" + q[-2:] for q in PER]
RNG = np.random.default_rng(42)
# temas da história: agro (novo) + as 5 dimensões do léxico validado
TEMAS_HISTORIA = {
    "agro": AGRO,
    "inovação e tecnologia": LEXICO_ATUAL["inovação e tecnologia"],
    "competitividade e produção": LEXICO_ATUAL["competitividade e produção"],
    "inserção internacional": LEXICO_ATUAL["inserção internacional"],
    "trabalho e renda": LEXICO_ATUAL["trabalho e renda"],
}
# "digital" (no léxico validado só "computador", 0 a 2 ocorrências por PPA) fica fora da história.
COR_TEMA = {"agro": "#6b8e23", "inovação e tecnologia": SERIES[0], "competitividade e produção": SERIES[1],
            "inserção internacional": SERIES[2], "trabalho e renda": SERIES[3]}
MIN_CARAC = {"PPA inteiro": 5, "selecionados": 3}   # ocorrências mínimas da palavra característica


def recortes(p):
    return {"PPA inteiro": p, "selecionados": p[p.selecionado == 1]}


# ------------------------------------------------------------------ capítulo 1: do que cada plano fala
def palavras_caracteristicas(p, top=20):
    """Por PPA: palavras mais características por contagem (razão entre a % da palavra no PPA e a % nos
    outros PPAs, com 0,5 somado às contagens) e o TF-IDF de 20 palavras como na primeira versão."""
    linhas, nuvens = [], {}
    for recorte, d in recortes(p).items():
        cont = {q: Counter(w for ls in d.loc[d.periodo == q, "lemas"] for w in ls) for q in PER}
        tot = sum(cont.values(), Counter())
        ntot = sum(tot.values())
        for q in PER:
            nq = sum(cont[q].values())
            esc = {}
            for w, c in cont[q].items():
                if c < MIN_CARAC[recorte]:
                    continue
                resto = tot[w] - c
                esc[w] = np.log2(((c + 0.5) / nq) / ((resto + 0.5) / (ntot - nq)))
            ordem = sorted(esc, key=lambda w: (-esc[w], -cont[q][w], w))[:top]
            nuvens[(recorte, q)] = {w: esc[w] for w in ordem if esc[w] > 0}
            for k, w in enumerate(ordem, 1):
                linhas.append({"recorte": recorte, "medida": "contagem", "periodo": q, "posição": k, "palavra": w,
                               "ocorrências": cont[q][w], "vezes mais frequente que nos outros PPAs": 2 ** esc[w]})
        # TF-IDF como na primeira versão: documento = PPA, 200 palavras no vocabulário
        textos = [" ".join(" ".join(ls) for ls in d.loc[d.periodo == q, "lemas"]) for q in PER]
        tv = TfidfVectorizer(max_features=200)
        M = tv.fit_transform(textos).toarray()
        voc = tv.get_feature_names_out()
        for i, q in enumerate(PER):
            for k, j in enumerate(np.argsort(-M[i])[:top], 1):
                linhas.append({"recorte": recorte, "medida": "TF-IDF", "periodo": q, "posição": k, "palavra": voc[j],
                               "ocorrências": cont[q][voc[j]], "tfidf": M[i, j]})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "historia_palavras_caracteristicas.csv", index=False, encoding="utf-8")

    cor = lambda *a, **k: TINTA
    for recorte in ("PPA inteiro", "selecionados"):
        fig, axs = plt.subplots(2, 3, figsize=(15, 8.6))
        for ax, q in zip(axs.ravel(), PER):
            freq = nuvens[(recorte, q)]
            if freq:
                wc = WordCloud(width=560, height=380, background_color="#fcfcfb", color_func=cor,
                               prefer_horizontal=1.0, random_state=42, font_path=None).generate_from_frequencies(freq)
                ax.imshow(wc, interpolation="bilinear")
            ax.set_title(q, loc="left", fontsize=12, fontweight="bold", color=TINTA)
            ax.axis("off")
        n = "529 programas" if recorte == "PPA inteiro" else "42 programas de política industrial"
        fig.suptitle(f"O que cada plano fala que os outros não falam ({n}); tamanho = quantas vezes a palavra é "
                     "mais frequente nesse PPA do que nos outros", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
        salvar(fig, "historia_palavras_" + ("ppa_inteiro" if recorte == "PPA inteiro" else "selecionados") + ".png")
        plt.close(fig)
    return t


# ------------------------------------------------------------------ testes de tema (capítulos 2 e 3)
def _taxas(cont, ntok, idx):
    return np.bincount(idx, weights=cont, minlength=6) / np.bincount(idx, weights=ntok, minlength=6)


def _spearman_t(v):
    r = pd.Series(v).rank().to_numpy() - 3.5
    t = np.arange(6) - 2.5
    return (r * t).sum() / np.sqrt((r ** 2).sum() * (t ** 2).sum())


def temas_no_tempo(p, B=3000):
    """% dos lemas de cada tema por PPA, com p da amplitude e da tendência (permutação dos PPAs dos programas)."""
    linhas = []
    for recorte, d in recortes(p).items():
        idx = d["periodo"].map({q: i for i, q in enumerate(PER)}).to_numpy()
        ntok = d["n_lemas"].to_numpy(float)
        for tema, termos in TEMAS_HISTORIA.items():
            ts = set(termos)
            cont = d["lemas"].map(lambda ls: sum(w in ts for w in ls)).to_numpy(float)
            obs = _taxas(cont, ntok, idx)
            amp = lambda v: (v.max() - v.min()) / v.mean() if v.mean() > 0 else 0
            a0, t0 = amp(obs), abs(_spearman_t(obs))
            ca = ct = 0
            for _ in range(B):
                v = _taxas(cont, ntok, RNG.permutation(idx))
                ca += amp(v) >= a0 - 1e-12
                ct += abs(_spearman_t(v)) >= t0 - 1e-12
            linhas.append({"recorte": recorte, "tema": tema, **{q: 100 * obs[i] for i, q in enumerate(PER)},
                           **{f"{q} n": int(np.bincount(idx, weights=cont, minlength=6)[i]) for i, q in enumerate(PER)},
                           "tendência (Spearman)": _spearman_t(obs), "p variação": (1 + ca) / (B + 1),
                           "p tendência": (1 + ct) / (B + 1)})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "historia_temas.csv", index=False, encoding="utf-8")

    fig, axs = plt.subplots(1, 2, figsize=(13, 4.4))
    x = np.arange(6)
    for ax, recorte in zip(axs, ("PPA inteiro", "selecionados")):
        destaque = ("agro", "inovação e tecnologia", "competitividade e produção")
        for _, r in t[t.recorte == recorte].iterrows():
            ax.plot(x, [r[q] for q in PER], "o-", lw=2.2 if r.tema in destaque else 1.2,
                    color=COR_TEMA[r.tema], label=r.tema, alpha=1 if r.tema in destaque else 0.75)
        ax.set_xticks(x, ROT)
        ax.set_ylim(0, None)
        eixo_limpo(ax)
        ax.set_title("PPA inteiro (529 programas)" if recorte == "PPA inteiro" else
                     "política industrial (42 programas selecionados)", loc="left", fontsize=11, color=TINTA)
    axs[0].set_ylabel("% dos lemas do PPA")
    axs[1].legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.suptitle("Na política industrial, competitividade sobe e inovação cai; no plano inteiro, só o agro muda "
                 "(% dos lemas de cada tema por PPA)",
                 x=0.01, ha="left", fontsize=12.5, fontweight="bold")
    salvar(fig, "historia_temas.png")
    plt.close(fig)
    return t


# ------------------------------------------------------------------ capítulo 2: o agro sai de cena
def agro(p, s, temas):
    """Três medidas do agro no plano: % dos lemas, % dos programas da área agricultura e pesca,
    % do valor do PPA (sem pessoal e emendas) nos programas dessa área."""
    progs = (p.assign(ag=p.area.eq("agricultura e pesca")).groupby("periodo").ag.mean() * 100).reindex(PER)
    sv = s[(s.pessoal == 0) & (s.emenda == 0)]
    orc = (sv[sv.area == "agricultura e pesca"].groupby("periodo").valor.sum() / sv.groupby("periodo").valor.sum()
           * 100).reindex(PER)
    lem = temas[(temas.recorte == "PPA inteiro") & (temas.tema == "agro")][PER].iloc[0]
    rural = [sum(ls.count("rural") for ls in p.loc[p.periodo == q, "lemas"]) for q in PER]
    tab = pd.DataFrame({"PPA": PER, "% dos lemas (tema agro)": lem.values, "ocorrências de 'rural'": rural,
                        "% dos programas (área agricultura e pesca)": progs.values,
                        "programas da área": [int((p.periodo.eq(q) & p.area.eq("agricultura e pesca")).sum()) for q in PER],
                        "% do valor do PPA (sem pessoal e emendas)": orc.values})
    tab.to_csv(SAIDAS / "historia_agro.csv", index=False, encoding="utf-8")
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
    x = np.arange(6)
    for ax, col, rot in zip(axs, ["% dos lemas (tema agro)", "% dos programas (área agricultura e pesca)",
                                  "% do valor do PPA (sem pessoal e emendas)"],
                            ["no discurso: % dos lemas", "na estrutura: % dos programas", "no orçamento: % do valor"]):
        ax.bar(x, tab[col], color="#6b8e23", width=0.6)
        for i, v in enumerate(tab[col]):
            ax.text(i, v, f"{v:.1f}".replace(".", ","), ha="center", va="bottom", fontsize=8.5, color=TINTA2)
        ax.set_xticks(x, ROT)
        eixo_limpo(ax)
        ax.set_title(rot, loc="left", fontsize=10.5, color=TINTA)
    fig.suptitle("O agro sai de cena no PPA inteiro (529 programas)", x=0.01, ha="left", fontsize=12.5,
                 fontweight="bold")
    fig.subplots_adjust(top=0.82)
    salvar(fig, "historia_agro.png")
    plt.close(fig)
    return tab


# ------------------------------------------------------------------ capítulo 4: quem fala de inovação
def quem_fala_de_inovacao(p, top=4):
    ts = set(LEXICO_ATUAL["inovação e tecnologia"])
    p = p.assign(inov=p["lemas"].map(lambda ls: sum(w in ts for w in ls)))
    g = p.groupby(["periodo", "selecionado"]).inov.sum().unstack().reindex(PER).fillna(0)
    tab = pd.DataFrame({"PPA": PER, "ocorrências nos selecionados": g[1].astype(int).values,
                        "ocorrências nos demais programas": g[0].astype(int).values})
    tab["% fora da política industrial"] = 100 * tab["ocorrências nos demais programas"] / (
        tab["ocorrências nos selecionados"] + tab["ocorrências nos demais programas"])
    quem = []
    for q in PER:
        d = p[(p.periodo == q) & (p.selecionado == 0) & (p.inov > 0)].nlargest(top, "inov")
        quem.append({"PPA": q, "programas de fora que mais usam o vocabulário de inovação":
                     "; ".join(f"{r.codigo} {r.nome[:45]} ({r.inov})" for r in d.itertuples())})
    tab.to_csv(SAIDAS / "historia_quem_fala_inovacao.csv", index=False, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    x = np.arange(6)
    a, b = tab["ocorrências nos selecionados"], tab["ocorrências nos demais programas"]
    ax.bar(x, a, color=SERIES[0], width=0.6, label="programas de política industrial")
    ax.bar(x, b, bottom=a, color=CINZA, width=0.6, label="demais programas")
    for i in range(6):
        ax.text(i, a[i] + b[i], f"{tab['% fora da política industrial'][i]:.0f}% fora", ha="center", va="bottom",
                fontsize=8.5, color=TINTA2)
    ax.set_xticks(x, ROT)
    ax.set_ylabel("ocorrências (inovação, tecnologia,\nmodernização, tecnológico)")
    eixo_limpo(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    titulo(ax, "Quem fala de inovação no PPA", "a inovação se concentra na política industrial em 2012-2019 e se espalha depois")
    salvar(fig, "historia_quem_fala_inovacao.png")
    plt.close(fig)
    return tab, pd.DataFrame(quem)


# ------------------------------------------------------------------ capítulo 6: discurso x orçamento
def discurso_orcamento(temas):
    o = pd.read_csv(SAIDAS / "orcamento_ajustado.csv").set_index("periodo").reindex(PER)
    v = pd.read_csv(SAIDAS / "ppa_inteiro_variaveis_tema.csv").pivot(index="periodo", columns="tema", values="pct_ppa").reindex(PER)
    sel = temas[temas.recorte == "selecionados"].set_index("tema")[PER]
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2))
    x = np.arange(6)
    for tema in ("competitividade e produção", "inovação e tecnologia"):
        axs[0].plot(x, sel.loc[tema].values, "o-", lw=2.2, color=COR_TEMA[tema], label=tema)
    axs[0].set_ylabel("% dos lemas dos programas selecionados")
    axs[0].set_title("O que a política industrial diz", loc="left", fontsize=11, color=TINTA)
    series = {"política industrial (sem pessoal e emendas)": (o.pct_selecionados_sem_pessoal_emendas, TINTA2),
              "subações de indústria e empresa (PPA inteiro)": (v["indústria e empresa"], SERIES[1]),
              "subações de inovação (PPA inteiro)": (v["inovação"], SERIES[0]),
              "crédito a empresas": (o.pct_credito_empresas, SERIES[3])}
    for rot, (val, cor) in series.items():
        axs[1].plot(x, val.values, "o-", lw=2, color=cor, label=rot)
    axs[1].set_ylabel("% do valor do PPA")
    axs[1].set_title("O que o orçamento faz", loc="left", fontsize=11, color=TINTA)
    for ax, loc in zip(axs, ("upper left", "upper right")):
        ax.set_xticks(x, ROT)
        ax.set_ylim(0, None)
        eixo_limpo(ax)
        ax.legend(frameon=False, fontsize=8.5, loc=loc)
    fig.suptitle("O discurso sobe, o dinheiro desce", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
    salvar(fig, "historia_discurso_orcamento.png")
    plt.close(fig)
    tab = pd.DataFrame({"PPA": PER, **{f"{t} (% lemas, selecionados)": sel.loc[t].values
                                       for t in ("competitividade e produção", "inovação e tecnologia")},
                        **{f"{k} (% PPA)": val.values for k, (val, _) in series.items()}})
    return tab


# ------------------------------------------------------------------ capítulo 7: planos copiados
def copia():
    c = pd.read_csv(SAIDAS / "ppa_inteiro_copia_transicoes.csv")
    col = "% lemas em frases iguais ou quase (≥ 0,9)"
    w = c.pivot(index="transição", columns="recorte", values=col).reindex(c["transição"].unique())
    fig, ax = plt.subplots(figsize=(9, 3.8))
    x = np.arange(len(w))
    ax.bar(x - 0.18, w["PPA inteiro"], width=0.36, color=CINZA, label="PPA inteiro")
    ax.bar(x + 0.18, w["selecionados"], width=0.36, color=SERIES[0], label="política industrial")
    for i in range(len(w)):
        for dx, val in ((-0.18, w["PPA inteiro"].iloc[i]), (0.18, w["selecionados"].iloc[i])):
            ax.text(i + dx, val, f"{val:.0f}%", ha="center", va="bottom", fontsize=8.5, color=TINTA2)
    ax.set_xticks(x, [t.replace(" → ", "\n→ ") for t in w.index], fontsize=8.5)
    ax.set_ylabel("% do texto repetido do PPA anterior")
    eixo_limpo(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    titulo(ax, "Planos copiados, política industrial reescrita", "% dos lemas em frases iguais ou quase iguais às do PPA anterior")
    salvar(fig, "historia_copia.png")
    plt.close(fig)
    return w.reset_index()


# ------------------------------------------------------------------ o que dizem x o que fazem
def dizem_fazem():
    """Coesão da política industrial no texto e nas subações (homofilia da rede de programas,
    saidas/rede_programas_resumo.csv, gerado por notebooks/redes_ppa.ipynb)."""
    r = pd.read_csv(SAIDAS / "rede_programas_resumo.csv")
    cam = {"texto (o que dizem)": SERIES[0], "subações (o que fazem)": SERIES[1]}
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    x = np.arange(6)
    for c, cor in cam.items():
        g = r[r.camada == c].set_index("periodo").reindex(PER)
        h, pv = g["homofilia (dentro/entre)"].to_numpy(), g["p homofilia"].to_numpy()
        ax.plot(x, h, "-", color=cor, lw=2, label=c)
        ax.scatter(x[pv < 0.05], h[pv < 0.05], color=cor, s=60, zorder=3)
        ax.scatter(x[pv >= 0.05], h[pv >= 0.05], facecolor="white", edgecolor=cor, s=60, zorder=3, lw=1.5)
    ax.axhline(1, color=CINZA, lw=1, ls="--")
    ax.text(5.1, 1.02, "igual ao resto do plano", fontsize=8, color=TINTA2, ha="right", va="bottom")
    ax.set_xticks(x, ROT)
    ax.set_ylim(0, None)
    ax.set_ylabel("similaridade entre selecionados /\nsimilaridade com o resto do plano")
    eixo_limpo(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    titulo(ax, "A política industrial fala parecido, mas faz coisas diferentes a partir de 2020",
           "ponto cheio: p < 0,05 (2.000 permutações); ponto vazio: não significativo")
    salvar(fig, "historia_dizem_fazem.png")
    plt.close(fig)
    linhas = []
    for q in PER:
        g = r[r.periodo == q].set_index("camada")
        linhas.append({"PPA": q,
                       "texto: razão": g.loc["texto (o que dizem)", "homofilia (dentro/entre)"],
                       "texto: p": g.loc["texto (o que dizem)", "p homofilia"],
                       "subações: razão": g.loc["subações (o que fazem)", "homofilia (dentro/entre)"],
                       "subações: p": g.loc["subações (o que fazem)", "p homofilia"]})
    return pd.DataFrame(linhas)


# ------------------------------------------------------------------ quem recebe
PUBLICOS_HISTORIA = ["empresas (com micro e pequenas)", "municípios", "produtores rurais", "instituições de pesquisa"]


def quem_recebe():
    """% do valor do PPA (sem pessoal e emendas) por público declarado: plano inteiro e política industrial.
    Fonte: saidas/rede_oferta_demanda_programas.csv (notebooks/redes_ppa.ipynb)."""
    e = pd.read_csv(SAIDAS / "rede_oferta_demanda_programas.csv", dtype={"codigo": str})
    e["publico"] = e["categoria"].replace({"empresas": "empresas (com micro e pequenas)",
                                           "micro e pequenas empresas": "empresas (com micro e pequenas)"})
    tabs = {}
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2))
    x = np.arange(6)
    cores = {"empresas (com micro e pequenas)": SERIES[0], "municípios": SERIES[1], "produtores rurais": "#6b8e23",
             "instituições de pesquisa": SERIES[2]}
    for ax, (rec, d) in zip(axs, (("PPA inteiro", e), ("política industrial", e[e.selecionado == 1]))):
        t = d.pivot_table(index="publico", columns="periodo", values="pct_ppa", aggfunc="sum").reindex(columns=PER).fillna(0)
        tabs[rec] = t
        for pub in PUBLICOS_HISTORIA:
            v = t.loc[pub].values if pub in t.index else np.zeros(6)
            ax.plot(x, v, "o-", lw=2, color=cores[pub], label=pub)
        ax.set_xticks(x, ROT)
        ax.set_ylim(0, None)
        eixo_limpo(ax)
        ax.set_title(f"{rec}: % do valor do PPA por público declarado", loc="left", fontsize=10.5, color=TINTA)
    axs[0].set_ylabel("% do valor do PPA (sem pessoal e emendas)")
    fig.legend(*axs[1].get_legend_handles_labels(), frameon=False, fontsize=9, loc="lower center",
               bbox_to_anchor=(0.5, -0.06), ncol=4)
    fig.suptitle("Quem recebe: empresas perdem espaço; em 2024-2027 municípios recebem um pouco mais que empresas na "
                 "política industrial", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
    salvar(fig, "historia_quem_recebe.png")
    plt.close(fig)
    out = pd.concat(tabs).reset_index().rename(columns={"level_0": "recorte", "publico": "público"})
    out.to_csv(SAIDAS / "historia_quem_recebe.csv", index=False, encoding="utf-8")
    return out


# ------------------------------------------------------------------ orçamento em % e em reais
IPCA = RAIZ / "dados" / "ipca" / "ipca_indice_mensal.csv"
ANOS_REF = {"2004-2007": [2007], "2008-2011": [2011], "2012-2015": [2012, 2013, 2014, 2015],
            "2016-2019": [2016, 2017, 2018, 2019], "2020-2023": [2020, 2021, 2022, 2023],
            "2024-2027": [2024, 2025, 2026, 2027]}


def fatores_reais(base=2024):
    """Multiplicador que leva o valor anual de cada PPA a preços médios de `base` (IPCA, média anual).
    2004-2007 e 2008-2011: valor de um ano (2007 e 2011); demais: média dos anos do quadriênio com 12
    meses de IPCA disponíveis (em 2024-2027, só 2024 e 2025)."""
    ip = pd.read_csv(IPCA, dtype={"mes": str})
    ano = ip.assign(a=ip.mes.str[:4].astype(int)).groupby("a").indice.agg(["size", "mean"])
    ano = ano.loc[ano["size"] == 12, "mean"]
    return {q: ano[base] / np.mean([ano[y] for y in ANOS_REF[q] if y in ano.index]) for q in PER}


def orcamento(s):
    """Política industrial no orçamento: % do PPA e R$ milhões por ano a preços de 2024 (sem pessoal e emendas)."""
    fat = fatores_reais()
    anual = {q: 1 if q in PER[:2] else 4 for q in PER}
    real = lambda v, q: v / anual[q] * fat[q] / 1e6
    sv = s[(s.pessoal == 0) & (s.emenda == 0)]
    o = pd.read_csv(SAIDAS / "orcamento_ajustado.csv").set_index("periodo").reindex(PER)
    vt = (pd.read_csv(SAIDAS / "ppa_inteiro_variaveis_tema.csv")
          .pivot(index="periodo", columns="tema", values="valor").reindex(PER))
    linhas = []
    for q in PER:
        tot = s.loc[s.periodo == q, "valor"].sum()
        pi = sv.loc[(sv.periodo == q) & (sv.selecionado == 1), "valor"].sum()
        linhas.append({"PPA": q,
                       "política industrial (% PPA)": 100 * pi / tot,
                       "crédito a empresas (% PPA)": o.loc[q, "pct_credito_empresas"],
                       "política industrial (R$ mi/ano, 2024)": real(pi, q),
                       "crédito a empresas (R$ mi/ano, 2024)": real(o.loc[q, "credito_empresas"], q),
                       "subações de inovação (R$ mi/ano, 2024)": real(vt.loc[q, "inovação"], q),
                       "subações de indústria e empresa (R$ mi/ano, 2024)": real(vt.loc[q, "indústria e empresa"], q),
                       "PPA total (R$ bi/ano, 2024)": real(tot, q) / 1000})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "historia_orcamento.csv", index=False, encoding="utf-8")

    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2))
    x = np.arange(6)
    axs[0].plot(x, t["política industrial (% PPA)"], "o-", lw=2.2, color=TINTA2, label="política industrial")
    axs[0].plot(x, t["crédito a empresas (% PPA)"], "o-", lw=2, color=SERIES[3], label="crédito a empresas")
    axs[0].set_ylabel("% do valor do PPA")
    axs[0].set_title("Fatia no orçamento do PPA", loc="left", fontsize=11, color=TINTA)
    for col, cor, rot in (("política industrial (R$ mi/ano, 2024)", TINTA2, "política industrial"),
                          ("crédito a empresas (R$ mi/ano, 2024)", SERIES[3], "crédito a empresas"),
                          ("subações de inovação (R$ mi/ano, 2024)", SERIES[0], "subações de inovação (PPA inteiro)"),
                          ("subações de indústria e empresa (R$ mi/ano, 2024)", SERIES[1],
                           "subações de indústria e empresa (PPA inteiro)")):
        axs[1].plot(x, t[col], "o-", lw=2, color=cor, label=rot)
    axs[1].set_ylabel("R$ milhões por ano, preços de 2024")
    axs[1].set_title("Em reais (IPCA)", loc="left", fontsize=11, color=TINTA)
    for ax in axs:
        ax.set_xticks(x, ROT)
        ax.set_ylim(0, None)
        eixo_limpo(ax)
        ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    fig.suptitle("A política industrial perde peso no orçamento e também encolhe em reais (sem pessoal e emendas)",
                 x=0.01, ha="left", fontsize=12.5, fontweight="bold")
    salvar(fig, "historia_orcamento.png")
    plt.close(fig)
    return t
