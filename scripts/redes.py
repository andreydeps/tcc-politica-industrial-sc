"""Redes do PPA (notebooks/redes_ppa.ipynb). Regras e limiares em scripts/redes_regras.py.

Entradas: as bases da análise do PPA inteiro (saidas/ppa_inteiro_programas.csv, _subacoes.csv,
_frases.csv), lidas por ppa_inteiro_analise.carregar().
Saídas  : saidas/rede_*.csv e saidas/rede_*.png.
Medida  : contagens (sem TF-IDF).
"""
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path as MPath
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import redes_regras as R  # noqa: E402
from estilo import CINZA, SERIES, TINTA, TINTA2, plt, salvar  # noqa: E402
from ppa_inteiro_analise import PER, _norm  # noqa: E402
from ppa_inteiro_listas import AREAS  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
CORES = SERIES + ["#7f6dd6", "#a0785a", "#3f9fae", "#c94f4f", "#6b8e23", "#d4a5ff"]
ROT = {q: q[2:4] + "-" + q[-2:] for q in PER}


# ================================================================== rede 1: termos
def _matriz_frases(f, vocab):
    ix = {w: i for i, w in enumerate(vocab)}
    M = np.zeros((len(f), len(vocab)), dtype=np.float32)
    for r, ls in enumerate(f["lemas"]):
        for w in set(ls):
            j = ix.get(w)
            if j is not None:
                M[r, j] = 1
    return M


def _proximidade(M):
    N = M.sum(axis=0)
    C = M.T @ M
    np.fill_diagonal(C, 0)
    den = np.maximum.outer(N, N)
    phi = np.divide(C, den, out=np.zeros_like(C), where=den > 0)
    phi[C < R.COOC_MIN] = 0
    return phi, C, N


def _grafo(phi, vocab):
    G = nx.Graph()
    G.add_nodes_from(vocab)
    ii, jj = np.nonzero(np.triu(phi, 1))
    G.add_weighted_edges_from((vocab[i], vocab[j], float(phi[i, j])) for i, j in zip(ii, jj))
    G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
    return G


def _louvain(G, seed=R.SEMENTE):
    com = nx.community.louvain_communities(G, weight="weight", seed=seed)
    com = sorted(com, key=len, reverse=True)
    return {n: k for k, c in enumerate(com) for n in c}


def _espinha(G):
    """Árvore geradora máxima + ligações mais fortes até o grau médio definido nas regras."""
    T = nx.maximum_spanning_tree(G, weight="weight")
    alvo = int(R.GRAU_MEDIO_DESENHO * G.number_of_nodes() / 2)
    resto = sorted(((d["weight"], u, v) for u, v, d in G.edges(data=True) if not T.has_edge(u, v)), reverse=True)
    for w, u, v in resto[:max(0, alvo - T.number_of_edges())]:
        T.add_edge(u, v, weight=w)
    return T


def rede_termos(f, p):
    rng = np.random.default_rng(R.SEMENTE)
    sets = [set(ls) for ls in f["lemas"]]
    nfr = Counter(w for st in sets for w in st)
    vocab = sorted(w for w, n in nfr.items() if n >= R.TERMOS_MIN_FRASES)
    M = _matriz_frases(f, vocab)
    phi, C, N = _proximidade(M)
    G = _grafo(phi, vocab)
    ref = _louvain(G)
    nos = list(G)

    # estabilidade: outras sementes do Louvain e reamostragem de frases
    lab = lambda part, ns: [part.get(n, -1) for n in ns]
    ari_sementes = [adjusted_rand_score(lab(ref, nos), lab(_louvain(G, s), nos)) for s in range(1, 21)]
    ari_boot, coas = [], Counter()
    alvos = [a for a in R.ALVOS if a in G]
    viz_ref = {a: [v for v, _ in sorted(G[a].items(), key=lambda kv: -kv[1]["weight"])[:5]] for a in alvos}
    for _ in range(R.BOOTSTRAP_TERMOS):
        Mb = M[rng.integers(0, len(M), len(M))]
        Gb = _grafo(_proximidade(Mb)[0], vocab)
        pb = _louvain(Gb)
        comuns = [n for n in nos if n in pb]
        ari_boot.append(adjusted_rand_score(lab(ref, comuns), lab(pb, comuns)))
        for a in alvos:
            for v in viz_ref[a]:
                if a in pb and v in pb and pb[a] == pb[v]:
                    coas[(a, v)] += 1
    estab = pd.DataFrame([{"teste": "outras 20 sementes do Louvain", "ARI médio": np.mean(ari_sementes),
                           "ARI mínimo": np.min(ari_sementes)},
                          {"teste": f"{R.BOOTSTRAP_TERMOS} reamostragens de frases", "ARI médio": np.mean(ari_boot),
                           "ARI mínimo": np.min(ari_boot)}])

    # comunidades: rótulo = 4 lemas de maior força dentro da própria comunidade
    nfreq = dict(zip(vocab, N))
    forca = {n: sum(d["weight"] for v, d in G[n].items() if ref[v] == ref[n]) for n in nos}
    com = pd.DataFrame({"lema": nos, "comunidade": [ref[n] for n in nos], "frases": [int(nfreq[n]) for n in nos],
                        "grau": [G.degree(n) for n in nos], "forca_na_comunidade": [forca[n] for n in nos]})
    rot = (com.sort_values("forca_na_comunidade", ascending=False).groupby("comunidade")["lema"]
           .apply(lambda x: ", ".join(x.head(4))))
    com["rótulo"] = com["comunidade"].map(rot)
    resumo = (com.groupby(["comunidade", "rótulo"]).agg(lemas=("lema", "size")).reset_index()
              .sort_values("comunidade"))

    # alvos: vizinhos no período todo e estabilidade do agrupamento com eles
    linhas = []
    for a in alvos:
        viz = sorted(G[a].items(), key=lambda kv: -kv[1]["weight"])[:6]
        linhas.append({"alvo": a, "frases": int(nfreq[a]), "grau": G.degree(a),
                       "vizinhos mais próximos (phi)": ", ".join(f"{v} ({d['weight']:.2f})" for v, d in viz),
                       "co-agrupado com os 5 vizinhos (% das reamostragens)":
                           np.mean([coas[(a, v)] for v in viz_ref[a]]) / R.BOOTSTRAP_TERMOS * 100})
    alvos_tab = pd.DataFrame(linhas)

    # vizinhos por metade (2004-2015 x 2016-2027), com estabilidade: % de 200 reamostragens de frases
    # em que o vizinho continua entre os 6 mais próximos
    def top_viz(st, a, k=6):
        n = Counter(w for x in st for w in x)
        c = Counter(w for x in st if a in x for w in x if w != a)
        top = sorted(((c[w] / max(n[a], n[w]), w) for w in c if c[w] >= R.COOC_MIN), reverse=True)[:k]
        return [w for _, w in top], n, c

    metades = []
    for nome, per in (("2004-2015", PER[:3]), ("2016-2027", PER[3:])):
        st = [set(ls) for ls in f.loc[f.periodo.isin(per), "lemas"]]
        for a in R.ALVOS:
            top, n, c = top_viz(st, a)
            fica = Counter()
            for _ in range(200):
                amostra = [st[i] for i in rng.integers(0, len(st), len(st))]
                fica.update(top_viz(amostra, a)[0])
            metades.append({"alvo": a, "metade": nome, "frases": n[a],
                            "vizinhos (phi; frases juntas; % das reamostragens no top 6)":
                                ", ".join(f"{w} ({c[w] / max(n[a], n[w]):.2f}; {c[w]}; {fica[w] / 2:.0f}%)" for w in top)})
    metades = pd.DataFrame(metades)

    # figura 1: espinha da rede, nós coloridos pelos temas aprovados (não pelas comunidades, que são instáveis)
    from ppa_inteiro_listas import TEMAS
    temas = ["inovação", "competitividade", "empresa", "indústria", "educação"]
    tema_de = {}
    for k, t in enumerate(temas):
        for w in TEMAS[t]:
            tema_de.setdefault(w, k)
    T = _espinha(G)
    pos = nx.spring_layout(T, weight="weight", seed=R.SEMENTE, k=1.6 / np.sqrt(T.number_of_nodes()), iterations=200)
    fig, ax = plt.subplots(figsize=(14, 10.5))
    nx.draw_networkx_edges(T, pos, ax=ax, edge_color=CINZA,
                           width=[0.3 + 2 * d["weight"] for *_, d in T.edges(data=True)], alpha=0.5)
    outros = [n for n in T if n not in tema_de]
    nx.draw_networkx_nodes(T, pos, nodelist=outros, ax=ax, node_color="#d9d8d0",
                           node_size=[6 + 4 * nfreq[n] for n in outros], linewidths=0)
    for k, t in enumerate(temas):
        ns = [n for n in T if tema_de.get(n) == k]
        nx.draw_networkx_nodes(T, pos, nodelist=ns, ax=ax, node_color=SERIES[k],
                               node_size=[30 + 6 * nfreq[n] for n in ns], linewidths=0.5, edgecolors="white", label=t)
        for n in ns:
            ax.text(*pos[n], n, fontsize=8.5, fontweight="bold", color=TINTA, ha="center", va="bottom")
    for n in sorted(outros, key=lambda n: -nfreq[n])[:25]:
        ax.text(*pos[n], n, fontsize=7, color=TINTA2, ha="center", va="bottom")
    ax.legend(frameon=False, fontsize=9, loc="lower left", title="lemas dos temas aprovados", title_fontsize=9)
    ax.axis("off")
    ax.set_title(f"Rede de termos dos PPAs 2004-2027: {G.number_of_nodes()} lemas, ligação = aparecer na mesma frase "
                 "(desenho: árvore máxima + ligações mais fortes)", loc="left", fontsize=12, fontweight="bold",
                 color=TINTA)
    salvar(fig, "rede_termos.png")
    plt.close(fig)

    # figura 2: vizinhança de competitividade e inovação nas duas metades
    fig, axs = plt.subplots(2, 2, figsize=(13, 10.5))
    for lin, a in enumerate(("competitividade", "inovação")):
        for col, (nome, per) in enumerate((("2004-2015", PER[:3]), ("2016-2027", PER[3:]))):
            ax = axs[lin, col]
            st = [set(ls) for ls in f.loc[f.periodo.isin(per), "lemas"]]
            n = Counter(w for x in st for w in x)
            c = Counter(w for x in st if a in x for w in x if w != a)
            viz = sorted(((c[w] / max(n[a], n[w]), w) for w in c if c[w] >= R.COOC_MIN), reverse=True)[:10]
            ps = nx.circular_layout([w for _, w in viz]) if viz else {}
            ps[a] = np.array([0.0, 0.0])
            for ph, w in viz:
                ax.plot([0, ps[w][0]], [0, ps[w][1]], color=CINZA, lw=0.5 + 8 * ph, zorder=1)
            for w, xy in ps.items():
                cor = SERIES[tema_de[w]] if w in tema_de else "#bdbcb4"
                ax.scatter(*xy, s=420 if w == a else 120 + 40 * c.get(w, 0), color=cor, zorder=2, edgecolors="white")
                ax.text(xy[0], xy[1] - (0.16 if w == a else 0.13), w, ha="center", va="top",
                        fontsize=11 if w == a else 9, color=TINTA, zorder=3,
                        fontweight="bold" if (w == a or w in tema_de) else "normal",
                        bbox=dict(facecolor="#fcfcfb", edgecolor="none", pad=1) if w == a else None)
            ax.set_xlim(-1.35, 1.35)
            ax.set_ylim(-1.35, 1.3)
            ax.axis("off")
            ax.set_title(f"{a}, {nome} ({n[a]} frases)", loc="left", fontsize=11, color=TINTA)
    for k, t in enumerate(temas):
        axs[0, 0].scatter([], [], color=SERIES[k], label=t)
    axs[0, 0].scatter([], [], color="#bdbcb4", label="fora dos temas")
    fig.legend(*axs[0, 0].get_legend_handles_labels(), loc="upper right", ncol=6, frameon=False, fontsize=9)
    fig.suptitle("Os 10 lemas mais próximos (phi) de competitividade e inovação; espessura = proximidade; "
                 "cor = tema aprovado", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
    salvar(fig, "rede_termos_vizinhancas.png")
    plt.close(fig)

    com.to_csv(SAIDAS / "rede_termos_nos.csv", index=False, encoding="utf-8")
    pd.DataFrame([(u, v, d["weight"], int(C[vocab.index(u), vocab.index(v)])) for u, v, d in G.edges(data=True)],
                 columns=["lema_1", "lema_2", "phi", "frases_juntas"]).to_csv(SAIDAS / "rede_termos_ligacoes.csv",
                                                                             index=False, encoding="utf-8")
    metades.to_csv(SAIDAS / "rede_termos_vizinhos_metades.csv", index=False, encoding="utf-8")
    info = {"lemas na rede": G.number_of_nodes(), "ligações": G.number_of_edges(), "comunidades": len(resumo),
            "frases": len(f)}
    return info, resumo, estab, alvos_tab, metades


def sensibilidade_termos(f, reamostragens=15):
    """Estabilidade das comunidades de termos com outros limiares (as regras continuam as de redes_regras)."""
    rng = np.random.default_rng(1)
    nfr = Counter(w for ls in f["lemas"] for w in set(ls))
    out = []
    for minf, cmin, phimin in [(4, 2, 0), (8, 2, 0), (8, 3, 0), (12, 3, 0), (8, 2, 0.15), (12, 3, 0.15), (15, 3, 0.2)]:
        vocab = sorted(w for w, n in nfr.items() if n >= minf)
        M = _matriz_frases(f, vocab)

        def grafo(Mx):
            phi, C, _ = _proximidade(Mx)
            phi[C < cmin] = 0
            phi[phi < phimin] = 0
            return _grafo(phi, vocab)
        G = grafo(M)
        ref = _louvain(G)
        nos = list(G)
        lab = lambda part, ns: [part.get(n, -1) for n in ns]
        a_s = np.mean([adjusted_rand_score(lab(ref, nos), lab(_louvain(G, sd), nos)) for sd in range(1, 11)])
        ab = []
        for _ in range(reamostragens):
            pb = _louvain(grafo(M[rng.integers(0, len(M), len(M))]))
            cm = [n for n in nos if n in pb]
            ab.append(adjusted_rand_score(lab(ref, cm), lab(pb, cm)))
        out.append({"mín. frases do lema": minf, "mín. frases juntas": cmin, "phi mínimo": phimin, "lemas": len(nos),
                    "ligações": G.number_of_edges(), "comunidades": len(set(ref.values())),
                    "ARI entre sementes": a_s, "ARI nas reamostragens": np.mean(ab)})
    t = pd.DataFrame(out)
    t.to_csv(SAIDAS / "rede_termos_sensibilidade.csv", index=False, encoding="utf-8")
    return t


# ================================================================== rede 2: programas
def lemas_subacoes(s):
    """Lemas dos nomes das subações (parte depois de ' | ' em 2004-2011), com cache."""
    arq = SAIDAS / "rede_subacoes_lemas.csv"
    if arq.exists():
        return pd.read_csv(arq, encoding="utf-8", dtype={"programa": str, "subacao": str}, keep_default_na=False)
    import spacy
    nlp = spacy.load("pt_core_news_lg", disable=["ner", "parser"])
    u = s[["periodo", "programa", "subacao", "texto"]].copy()
    u["nome"] = u["texto"].str.split(" | ", regex=False).str[-1]
    nomes = u["nome"].drop_duplicates().tolist()
    lema = lambda doc: " ".join(tk.lemma_.lower() for tk in doc if not tk.is_stop and not tk.is_punct
                                and not tk.is_space and tk.is_alpha and tk.pos_ in {"NOUN", "VERB", "ADJ"})
    mapa = dict(zip(nomes, (lema(d) for d in nlp.pipe(nomes, batch_size=128))))
    u["lemas_nome"] = u["nome"].map(mapa)
    u = u.drop(columns=["texto"])
    u.to_csv(arq, index=False, encoding="utf-8")
    return u


def _cosseno(docs):
    """docs: lista de listas de lemas (já filtradas). Devolve matriz de cosseno das contagens."""
    vocab = sorted({w for d in docs for w in d})
    ix = {w: i for i, w in enumerate(vocab)}
    X = np.zeros((len(docs), len(vocab)))
    for r, d in enumerate(docs):
        for w, n in Counter(d).items():
            X[r, ix[w]] = n
    nrm = np.linalg.norm(X, axis=1, keepdims=True)
    X = np.divide(X, nrm, out=np.zeros_like(X), where=nrm > 0)
    S = X @ X.T
    np.fill_diagonal(S, 0)
    return S


def _filtra_formato(docs):
    df = Counter(w for d in docs for w in set(d))
    corte = R.FORMATO_DF * len(docs)
    formato = {w for w, n in df.items() if n > corte}
    return [[w for w in d if w not in formato] for d in docs], formato


def _knn(S, codigos):
    G = nx.Graph()
    G.add_nodes_from(codigos)
    for i in range(len(S)):
        for j in np.argsort(-S[i])[:R.KNN]:
            if S[i, j] >= R.SIM_MIN:
                G.add_edge(codigos[i], codigos[j], weight=float(S[i, j]))
    return G


def _homofilia(S, sel, rng):
    sel = np.asarray(sel, bool)
    iu = np.triu_indices(len(S), 1)

    def razao(m):
        a, b = m[iu[0]], m[iu[1]]
        v = S[iu]
        dentro, entre = v[a & b], v[a ^ b]
        return dentro.mean() / entre.mean() if entre.mean() > 0 else np.nan

    obs = razao(sel)
    c = sum(razao(rng.permutation(sel)) >= obs for _ in range(R.PERM_PROGRAMAS))
    return obs, (1 + c) / (R.PERM_PROGRAMAS + 1)


def _mantel(A, B, rng):
    iu = np.triu_indices(len(A), 1)
    ra = pd.Series(A[iu]).rank().to_numpy()
    rb_full = np.zeros_like(B)
    rb_full[iu] = pd.Series(B[iu]).rank().to_numpy()
    rb_full = rb_full + rb_full.T
    obs = np.corrcoef(ra, rb_full[iu])[0, 1]
    c = 0
    for _ in range(R.PERM_PROGRAMAS):
        pm = rng.permutation(len(A))
        c += np.corrcoef(ra, rb_full[np.ix_(pm, pm)][iu])[0, 1] >= obs
    return obs, (1 + c) / (R.PERM_PROGRAMAS + 1)


def rede_programas(p, s):
    rng = np.random.default_rng(R.SEMENTE)
    ls = lemas_subacoes(s)
    sub_docs = (ls.drop_duplicates(["periodo", "programa", "lemas_nome"])
                .groupby(["periodo", "programa"])["lemas_nome"].apply(lambda x: " ".join(x).split()))
    prob = pd.read_csv(SAIDAS / "classificador_programas.csv", dtype={"codigo": str}).set_index(["periodo", "codigo"])
    resumo, dens, grafos, comunidades = [], [], {}, []
    for q in PER:
        d = p[p.periodo == q].reset_index(drop=True)
        cods = d.codigo.tolist()
        docs_txt, fmt_txt = _filtra_formato(d.lemas.tolist())
        docs_sub, fmt_sub = _filtra_formato([sub_docs.get((q, c), []) for c in cods])
        sel = d.selecionado.to_numpy().astype(bool)
        mats = {"texto (o que dizem)": _cosseno(docs_txt), "subações (o que fazem)": _cosseno(docs_sub)}
        rho, p_m = _mantel(*mats.values(), rng)
        for camada, S in mats.items():
            G = _knn(S, cods)
            grafos[(q, camada)] = (G, dict(zip(cods, sel)))
            h, ph = _homofilia(S, sel, rng)
            part = _louvain(G) if G.number_of_edges() else {c: k for k, c in enumerate(cods)}
            com_sel = Counter(part[c] for c in np.array(cods)[sel])
            principal = com_sel.most_common(1)[0][0]
            membros = [c for c in cods if part[c] == principal]
            comunidades.append({"periodo": q, "camada": camada, "comunidade principal da política industrial":
                                ", ".join(f"{c}{'*' if sel[cods.index(c)] else ''}" for c in membros)})
            resumo.append({"periodo": q, "camada": camada, "programas": len(cods), "ligações": G.number_of_edges(),
                           "homofilia (dentro/entre)": h, "p homofilia": ph,
                           "comunidades": len(set(part.values())),
                           "comunidades com selecionados": len(com_sel),
                           "selecionados na comunidade principal": com_sel[principal],
                           "palavras de formato retiradas": len(fmt_txt if camada.startswith("texto") else fmt_sub)})
            tot = S.sum(axis=1)
            dsel = (S * sel[None, :]).sum(axis=1)
            for i, c in enumerate(cods):
                dens.append({"periodo": q, "codigo": c, "nome": d.nome[i], "selecionado": int(sel[i]), "camada": camada,
                             "densidade": dsel[i] / tot[i] if tot[i] > 0 else np.nan})
        resumo.append({"periodo": q, "camada": "correlação entre as camadas (Mantel, Spearman)",
                       "homofilia (dentro/entre)": rho, "p homofilia": p_m})
    resumo = pd.DataFrame(resumo)
    dens = pd.DataFrame(dens)
    dw = dens.pivot_table(index=["periodo", "codigo", "nome", "selecionado"], columns="camada",
                          values="densidade").reset_index()
    dw["prob_classificador"] = [prob["prob_politica_industrial"].get((q, c), np.nan) for q, c in zip(dw.periodo, dw.codigo)]
    dw.to_csv(SAIDAS / "rede_programas_densidade.csv", index=False, encoding="utf-8")
    resumo.to_csv(SAIDAS / "rede_programas_resumo.csv", index=False, encoding="utf-8")

    # figura: 2 camadas x 6 PPAs
    fig, axs = plt.subplots(2, 6, figsize=(24, 8.6))
    for col, q in enumerate(PER):
        for lin, camada in enumerate(("texto (o que dizem)", "subações (o que fazem)")):
            ax = axs[lin, col]
            G, selm = grafos[(q, camada)]
            pos = nx.spring_layout(G, weight="weight", seed=R.SEMENTE, k=1.2 / np.sqrt(G.number_of_nodes()))
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color=CINZA, width=0.6, alpha=0.7)
            ns = [n for n in G if selm[n]]
            nx.draw_networkx_nodes(G, pos, nodelist=[n for n in G if not selm[n]], ax=ax, node_size=14,
                                   node_color="#bdbcb4", linewidths=0)
            nx.draw_networkx_nodes(G, pos, nodelist=ns, ax=ax, node_size=60, node_color=SERIES[0], linewidths=0.5,
                                   edgecolors="white")
            for n in ns:
                ax.text(*pos[n], n, fontsize=7.5, color=TINTA, ha="left", va="bottom", fontweight="bold")
            ax.axis("off")
            if lin == 0:
                ax.set_title(q, loc="left", fontsize=11, color=TINTA)
            if col == 0:
                ax.text(-0.05, 0.5, camada, transform=ax.transAxes, rotation=90, va="center", ha="right",
                        fontsize=10.5, color=TINTA2)
    fig.suptitle("Rede de programas de cada PPA (cada programa ligado aos 3 mais parecidos); em azul, os selecionados",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    salvar(fig, "rede_programas.png")
    plt.close(fig)
    return resumo, dw, pd.DataFrame(comunidades)


# ================================================================== rede 3: oferta e demanda
def rede_oferta_demanda(p, s):
    p = p.assign(cat=p["publico_alvo"].map(R.categorias_publico_rede))
    sv = s[(s.pessoal == 0) & (s.emenda == 0)]
    tot = sv.groupby("periodo")["valor"].sum()
    val = sv.groupby(["periodo", "programa"])["valor"].sum()
    linhas = []
    for r in p.itertuples():
        v = val.get((r.periodo, r.codigo), 0.0)
        for c in r.cat:
            linhas.append({"periodo": r.periodo, "codigo": r.codigo, "nome": r.nome, "selecionado": r.selecionado,
                           "orgao": r.orgao, "area": r.area, "publico_alvo": r.publico_alvo, "categoria": c,
                           "valor": v / len(r.cat), "programas": 1 / len(r.cat)})
    e = pd.DataFrame(linhas)
    e["pct_ppa"] = 100 * e["valor"] / e["periodo"].map(tot)
    e.to_csv(SAIDAS / "rede_oferta_demanda_programas.csv", index=False, encoding="utf-8")
    lig = e.groupby(["periodo", "area", "categoria"]).agg(pct_ppa=("pct_ppa", "sum"), programas=("programas", "sum")).reset_index()
    lig.to_csv(SAIDAS / "rede_oferta_demanda_ligacoes.csv", index=False, encoding="utf-8")

    demanda = lig.pivot_table(index="categoria", columns="periodo", values="pct_ppa", aggfunc="sum").reindex(columns=PER).fillna(0)
    demanda = demanda.sort_values(PER[-1], ascending=False)
    # diversidade da área (nº de categorias que atende) e ubiquidade da categoria (nº de áreas que a atendem)
    pres = lig[lig.programas > 0]
    divers = pres.groupby(["area", "periodo"])["categoria"].nunique().unstack().reindex(columns=PER).fillna(0).astype(int)
    ubiq = pres.groupby(["categoria", "periodo"])["area"].nunique().unstack().reindex(columns=PER).fillna(0).astype(int)
    # quem atende empresas (empresas + micro e pequenas), em % do PPA
    emp = (lig[lig.categoria.isin(["empresas", "micro e pequenas empresas"])]
           .pivot_table(index="area", columns="periodo", values="pct_ppa", aggfunc="sum").reindex(columns=PER).fillna(0))
    emp.loc["total"] = emp.sum()
    sel = (e[e.selecionado == 1].groupby(["periodo", "codigo", "orgao", "publico_alvo"])["categoria"]
           .agg(", ".join).reset_index())
    sel["pct_ppa"] = [e[(e.periodo == q) & (e.codigo == c)].pct_ppa.sum() for q, c in zip(sel.periodo, sel.codigo)]

    # figura: bipartida por PPA
    areas = [a for a, _ in AREAS]
    cats = list(R.PUBLICO_REDE) + ["outros"]
    fig, axs = plt.subplots(2, 3, figsize=(18, 13))
    for ax, q in zip(axs.ravel(), PER):
        L = lig[lig.periodo == q]
        ya = {a: 1 - i / (len(areas) - 1) for i, a in enumerate(areas)}
        yc = {c: 1 - i / (len(cats) - 1) for i, c in enumerate(cats)}
        for r in L[L.pct_ppa >= R.MIN_LIGACAO_DESENHO].itertuples():
            empresa = r.categoria in ("empresas", "micro e pequenas empresas")
            ax.plot([0, 1], [ya[r.area], yc[r.categoria]], color=SERIES[0] if empresa else "#9d9c94",
                    lw=0.4 + 1.6 * np.sqrt(r.pct_ppa), alpha=0.85 if empresa else 0.45, solid_capstyle="round")
        sa = L.groupby("area").pct_ppa.sum()
        sc = L.groupby("categoria").pct_ppa.sum()
        for a in areas:
            ax.scatter(0, ya[a], s=10 + 9 * sa.get(a, 0), color=TINTA2, zorder=3)
            ax.text(-0.03, ya[a], f"{a[:34]} ({sa.get(a, 0):.1f})".replace(".", ","), ha="right", va="center", fontsize=7.6)
        for c in cats:
            ax.scatter(1, yc[c], s=10 + 9 * sc.get(c, 0), color=SERIES[0] if "empresa" in c else TINTA2, zorder=3)
            ax.text(1.03, yc[c], f"{c} ({sc.get(c, 0):.1f})".replace(".", ","), ha="left", va="center", fontsize=7.6)
        ax.set_xlim(-0.95, 1.75)
        ax.set_ylim(-0.06, 1.06)
        ax.axis("off")
        ax.set_title(f"{q}: oferta (área do órgão) → demanda (público-alvo)", loc="left", fontsize=10.5, color=TINTA)
    fig.suptitle("Oferta e demanda: % do valor do PPA sem pessoal e emendas (ligações de 0,10% ou mais); "
                 "em azul, o público empresas", x=0.01, ha="left", fontsize=13, fontweight="bold")
    salvar(fig, "rede_oferta_demanda.png")
    plt.close(fig)
    return demanda, divers, ubiq, emp, sel


# ================================================================== rede 4: genealogia
def _heranca_texto(f, limiar=0.9):
    f = f.copy()
    f["norm"] = f["frase"].map(_norm)
    f["n_lemas"] = f["lemas"].str.len()
    f["sim"], f["origem"] = np.nan, None
    for a, b in zip(PER[:-1], PER[1:]):
        A = f[f.periodo == a]
        ant = list(zip(A["norm"], A["codigo"]))
        exatas = {}
        for t, c in ant:
            exatas.setdefault(t, c)
        for i in f.index[f.periodo == b]:
            s = f.at[i, "norm"]
            if s in exatas:
                f.at[i, "sim"], f.at[i, "origem"] = 1.0, exatas[s]
                continue
            best, orig = 0.0, None
            for t, c in ant:
                if not (0.75 <= len(t) / max(len(s), 1) <= 1.33):
                    continue
                m = SequenceMatcher(None, s, t, autojunk=False)
                if m.real_quick_ratio() <= best or m.quick_ratio() <= best:
                    continue
                r = m.ratio()
                if r > best:
                    best, orig = r, c
            f.at[i, "sim"], f.at[i, "origem"] = best, orig
    f["herdada"] = f["sim"] >= limiar
    return f


def genealogia(p, s, f):
    fh = _heranca_texto(f)
    ltot = fh.groupby(["periodo", "codigo"])["n_lemas"].sum()
    txt = (fh[fh.herdada].groupby(["periodo", "codigo", "origem"])["n_lemas"].sum().rename("lemas").reset_index())
    txt["w_txt"] = txt["lemas"] / [ltot[(q, c)] for q, c in zip(txt.periodo, txt.codigo)]
    vtot = s.groupby(["periodo", "programa"])["valor"].sum()
    ntot = s.groupby(["periodo", "programa"]).size()
    sub = []
    nome_sub = s["texto"].str.split(" | ", regex=False).str[-1].map(_norm)
    for a, b in zip(PER[:-1], PER[1:]):
        dono = dict(zip(s.loc[s.periodo == a, "subacao"], s.loc[s.periodo == a, "programa"]))
        nome_a = dict(zip(s.loc[s.periodo == a, "subacao"], nome_sub[s.periodo == a]))
        B = s[(s.periodo == b) & s.subacao.isin(dono)].assign(origem=lambda d: d.subacao.map(dono))
        parecido = [SequenceMatcher(None, nome_sub[i], nome_a[c], autojunk=False).ratio() >= R.SUBACAO_NOME_MIN
                    for i, c in zip(B.index, B.subacao)]
        B = B[parecido]
        g = B.groupby(["programa", "origem"]).agg(valor=("valor", "sum"), n=("valor", "size")).reset_index()
        for r in g.itertuples():
            vt = vtot[(b, r.programa)]
            sub.append({"periodo": b, "codigo": r.programa, "origem": r.origem,
                        "w_sub": r.valor / vt if vt > 0 else r.n / ntot[(b, r.programa)]})
    sub = pd.DataFrame(sub)
    ed = (pd.merge(txt[["periodo", "codigo", "origem", "w_txt"]], sub, on=["periodo", "codigo", "origem"], how="outer")
          .fillna({"w_txt": 0, "w_sub": 0}))
    ed["periodo_origem"] = ed["periodo"].map(dict(zip(PER[1:], PER[:-1])))
    ed["w"] = ed[["w_txt", "w_sub"]].max(axis=1)
    ed["forte"] = ed["w"] >= R.HERANCA_MIN
    info = p.set_index(["periodo", "codigo"])
    ed["orgao"] = [info.at[(q, c), "orgao"] for q, c in zip(ed.periodo, ed.codigo)]
    ed["orgao_origem"] = [info.at[(q, c), "orgao"] for q, c in zip(ed.periodo_origem, ed.origem)]
    ed["mesmo_dono"] = [R.mesmo_dono(a, b) for a, b in zip(ed.orgao_origem, ed.orgao)]
    ed.to_csv(SAIDAS / "rede_genealogia_ligacoes.csv", index=False, encoding="utf-8")

    forte = ed[ed.forte]
    eventos = []
    for q in PER[1:]:
        anterior = PER[PER.index(q) - 1]
        for r in p[p.periodo == q].itertuples():
            pais = forte[(forte.periodo == q) & (forte.codigo == r.codigo)].sort_values("w", ascending=False)
            if pais.empty:
                ev, mesmo_cod, dono = "novo", None, None
            else:
                ev = "fusão (2+ pais)" if len(pais) > 1 else "um pai"
                mesmo_cod = (pais.iloc[0].origem == r.codigo) if anterior != PER[0] else None
                dono = bool(pais.iloc[0].mesmo_dono)
            eventos.append({"periodo": q, "codigo": r.codigo, "nome": r.nome, "selecionado": r.selecionado,
                            "evento": ev, "pai principal": None if pais.empty else pais.iloc[0].origem,
                            "mesmo código do pai": mesmo_cod, "mesmo dono do pai": dono,
                            "pais": ", ".join(f"{o} ({w:.0%})" for o, w in zip(pais.origem, pais.w))})
    eventos = pd.DataFrame(eventos)
    filhos = forte.groupby(["periodo_origem", "origem"]).size()
    lado_a = []
    for q in PER[:-1]:
        for r in p[p.periodo == q].itertuples():
            n = filhos.get((q, r.codigo), 0)
            lado_a.append({"periodo": q, "codigo": r.codigo, "selecionado": r.selecionado,
                           "destino": "extinto" if n == 0 else ("cisão (2+ filhos)" if n > 1 else "um filho")})
    lado_a = pd.DataFrame(lado_a)

    def resumo(ev, la):
        out = []
        for a, b in zip(PER[:-1], PER[1:]):
            e, l = ev[ev.periodo == b], la[la.periodo == a]
            com_pai = e[e.evento != "novo"]
            out.append({"transição": f"{a} → {b}", "programas novos (%)": 100 * (e.evento == "novo").mean(),
                        "um pai (%)": 100 * (e.evento == "um pai").mean(),
                        "fusão (%)": 100 * (e.evento == "fusão (2+ pais)").mean(),
                        "extintos no PPA anterior (%)": 100 * (l.destino == "extinto").mean(),
                        "cisão no PPA anterior (%)": 100 * (l.destino == "cisão (2+ filhos)").mean(),
                        "troca de dono (% dos com pai)": 100 * (~com_pai["mesmo dono do pai"].astype(bool)).mean()
                        if len(com_pai) else np.nan,
                        "programas": len(e)})
        return pd.DataFrame(out)
    res_inteiro = resumo(eventos, lado_a)
    res_sel = resumo(eventos[eventos.selecionado == 1], lado_a[lado_a.selecionado == 1])
    eventos.to_csv(SAIDAS / "rede_genealogia_eventos.csv", index=False, encoding="utf-8")

    # componente da política industrial: selecionados + pais e filhos diretos (ligações fortes)
    selset = set(zip(p.loc[p.selecionado == 1, "periodo"], p.loc[p.selecionado == 1, "codigo"]))
    comp = forte[[((r.periodo, r.codigo) in selset) or ((r.periodo_origem, r.origem) in selset)
                  for r in forte.itertuples()]].copy()
    linhagem = comp.assign(
        nome_origem=[info.at[(q, c), "nome"] for q, c in zip(comp.periodo_origem, comp.origem)],
        nome=[info.at[(q, c), "nome"] for q, c in zip(comp.periodo, comp.codigo)])[
        ["periodo_origem", "origem", "nome_origem", "periodo", "codigo", "nome", "w_sub", "w_txt", "mesmo_dono"]]
    _figura_linhagem(p, comp, selset)
    return res_inteiro, res_sel, eventos, linhagem


def _figura_linhagem(p, comp, selset):
    nos = set(zip(comp.periodo_origem, comp.origem)) | set(zip(comp.periodo, comp.codigo)) | selset
    serie = dict(zip(zip(p.periodo, p.codigo), p.serie))
    # família de cada nó: série do selecionado a que ele se liga (para ordenar na vertical)
    fam = {n: serie[n] for n in nos if n in selset}
    for _ in range(3):
        for r in comp.itertuples():
            a, b = (r.periodo_origem, r.origem), (r.periodo, r.codigo)
            if a in fam and b not in fam:
                fam[b] = fam[a]
            if b in fam and a not in fam:
                fam[a] = fam[b]
    ordem = sorted({fam.get(n, "zz") for n in nos})
    ypos = {}
    # posição vertical: famílias em faixas; dentro da faixa, um abaixo do outro
    faixa = {}
    y = 0
    for fm in ordem:
        alt = max(sum(1 for n in nos if n[0] == q and fam.get(n, "zz") == fm) for q in PER)
        faixa[fm] = (y, alt)
        y += alt + 0.6
    for q in PER:
        cont = Counter()
        for n in sorted([n for n in nos if n[0] == q], key=lambda n: n[1]):
            fm = fam.get(n, "zz")
            ypos[n] = -(faixa[fm][0] + cont[fm])
            cont[fm] += 1
    nome = dict(zip(zip(p.periodo, p.codigo), p.nome))
    fig, ax = plt.subplots(figsize=(17, 0.42 * y + 1.5))
    xs = {q: i * 3.4 for i, q in enumerate(PER)}
    larg = 1.75
    for r in comp.itertuples():
        a, b = (r.periodo_origem, r.origem), (r.periodo, r.codigo)
        x0, y0, x1, y1 = xs[a[0]] + larg, ypos[a], xs[b[0]], ypos[b]
        cor = TINTA2 if (r.w_sub >= R.HERANCA_MIN and r.w_txt >= R.HERANCA_MIN) else (
            SERIES[1] if r.w_sub >= R.HERANCA_MIN else SERIES[2])
        caminho = MPath([(x0, y0), (x0 + 0.9, y0), (x1 - 0.9, y1), (x1, y1)],
                        [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4])
        ax.add_patch(PathPatch(caminho, fill=False, lw=0.6 + 3.2 * r.w, color=cor, alpha=0.75,
                               linestyle="-" if r.mesmo_dono else (0, (4, 2))))
    for n, yy in ypos.items():
        sel = n in selset
        ax.add_patch(FancyBboxPatch((xs[n[0]], yy - 0.32), larg, 0.64, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    facecolor=SERIES[0] if sel else "white", edgecolor=SERIES[0] if sel else CINZA, lw=0.8))
        ax.text(xs[n[0]] + 0.06, yy, f"{n[1]} {nome.get(n, '')[:22]}", fontsize=6.4, va="center",
                color="white" if sel else TINTA)
    for q in PER:
        ax.text(xs[q] + larg / 2, 0.9, q, ha="center", fontsize=10.5, fontweight="bold", color=TINTA)
    for cor, rot in ((SERIES[1], "herança de subações (mesmo código e nome)"), (SERIES[2], "herança de texto"),
                     (TINTA2, "subações e texto")):
        ax.plot([], [], color=cor, lw=2.5, label=rot)
    ax.plot([], [], color=TINTA2, lw=1.5, ls=(0, (4, 2)), label="troca de dono (órgão responsável)")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.set_xlim(-0.3, xs[PER[-1]] + larg + 0.3)
    ax.set_ylim(-y + 0.2, 1.4)
    ax.axis("off")
    ax.set_title("Genealogia dos programas de política industrial (azul) e de seus pais e filhos diretos "
                 f"(herança de pelo menos {R.HERANCA_MIN:.0%})".replace(".", ","), loc="left", fontsize=12,
                 fontweight="bold", color=TINTA)
    salvar(fig, "rede_genealogia.png")
    plt.close(fig)
