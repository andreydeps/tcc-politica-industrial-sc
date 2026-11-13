"""Funções da análise do PPA inteiro (notebooks/analise_ppa_inteiro.ipynb).

Medida principal: contagem de lemas e % sobre o total de lemas do recorte (sem TF-IDF).
Todas as listas e regras de seleção estão em scripts/ppa_inteiro_listas.py.

Entradas (geradas por scripts/ppa_inteiro_base.py, ppa_inteiro_subacoes.py, ppa_inteiro_frases.py):
  saidas/ppa_inteiro_programas.csv, saidas/ppa_inteiro_subacoes.csv, saidas/ppa_inteiro_frases.csv
Cada função devolve DataFrames e grava em saidas/ o CSV ou PNG correspondente.
"""
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo import CINZA, SERIES, TINTA, TINTA2, eixo_limpo, plt, salvar, titulo  # noqa: E402
from ppa_inteiro_listas import (GOVERNOS, LEXICO_ATUAL, PALAVRAS_SOLTAS, TEMAS, TRANSICOES,  # noqa: E402
                                area_orgao, categorias_publico, sem_acento, tema_subacao)

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
PER = ["2004-2007", "2008-2011", "2012-2015", "2016-2019", "2020-2023", "2024-2027"]
RNG = np.random.default_rng(42)
EQUIV_2004 = {"0580": "0200", "0490": "0230", "0230": "0310", "0540": "0342", "0570": "0212",
              "0410": "0250", "0510": "0210", "0530": "0354", "0970": "0970-2004"}   # regras-de-negocio.md


# ------------------------------------------------------------------ carga
def carregar():
    p = pd.read_csv(SAIDAS / "ppa_inteiro_programas.csv", encoding="utf-8", dtype={"codigo": str})
    p["texto_lematizado"] = p["texto_lematizado"].fillna("")
    p["lemas"] = p["texto_lematizado"].str.split()
    p["n_lemas"] = p["lemas"].str.len()
    p["area"] = p["orgao"].map(area_orgao)
    p["publico_cat"] = p["publico_alvo"].map(categorias_publico)
    p["serie"] = np.where(p["periodo"].eq("2004-2007"), p["codigo"].map(EQUIV_2004).fillna(p["codigo"] + "-2004"),
                          p["codigo"])
    s = pd.read_csv(SAIDAS / "ppa_inteiro_subacoes.csv", encoding="utf-8", dtype={"programa": str, "subacao": str},
                    keep_default_na=False)
    s["tema"] = s["texto"].map(tema_subacao)
    s = s.merge(p[["periodo", "codigo", "nome", "orgao", "area", "serie"]],
                left_on=["periodo", "programa"], right_on=["periodo", "codigo"], how="left").drop(columns="codigo")
    f = pd.read_csv(SAIDAS / "ppa_inteiro_frases.csv", encoding="utf-8", dtype={"codigo": str})
    f["frase_lematizada"] = f["frase_lematizada"].fillna("")
    f["lemas"] = f["frase_lematizada"].str.split()
    return p, s, f


def contar(lemas, termos):
    ts = set(termos)
    return sum(1 for w in lemas if w in ts)


def _amp(m):
    mu = m.mean(axis=0)
    return (m.max(axis=0) - m.min(axis=0)) / np.where(mu == 0, np.nan, mu)


def perm_amplitude(cont, ntok, per, B=3000):
    """p da amplitude relativa (máx - mín)/média das taxas por PPA, sorteando o PPA dos programas."""
    idx = pd.Series(per).map({q: i for i, q in enumerate(PER)}).to_numpy()
    def taxas(ix):
        return np.bincount(ix, weights=cont, minlength=6) / np.bincount(ix, weights=ntok, minlength=6)
    obs = _amp(taxas(idx)[:, None])[0]
    c = sum(_amp(taxas(RNG.permutation(idx))[:, None])[0] >= obs - 1e-12 for _ in range(B))
    return (1 + c) / (B + 1)


# ------------------------------------------------------------------ item 1
def item1_temas(p, B=3000):
    linhas = []
    for recorte, d in (("PPA inteiro", p), ("selecionados", p[p.selecionado == 1])):
        tot = d.groupby("periodo")["n_lemas"].sum()
        for tema, termos in TEMAS.items():
            cont = d["lemas"].map(lambda ls: contar(ls, termos))
            oc = cont.groupby(d["periodo"]).sum()
            linha = {"recorte": recorte, "tema": tema}
            for q in PER:
                linha[f"{q} ocorr"] = int(oc.get(q, 0))
                linha[q] = 100 * oc.get(q, 0) / tot[q]
            linha["p variação"] = perm_amplitude(cont.to_numpy(float), d["n_lemas"].to_numpy(float),
                                                 d["periodo"].to_numpy(), B)
            linhas.append(linha)
        linhas.append({"recorte": recorte, "tema": "total de lemas",
                       **{f"{q} ocorr": int(tot[q]) for q in PER}, **{q: 100.0 for q in PER}})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "ppa_inteiro_temas.csv", index=False, encoding="utf-8")

    soltas = []
    for recorte, d in (("PPA inteiro", p), ("selecionados", p[p.selecionado == 1])):
        for w in PALAVRAS_SOLTAS:
            oc = d["lemas"].map(lambda ls: ls.count(w)).groupby(d["periodo"]).sum()
            soltas.append({"recorte": recorte, "palavra": w, **{q: int(oc.get(q, 0)) for q in PER}})
    s = pd.DataFrame(soltas)
    s.to_csv(SAIDAS / "ppa_inteiro_palavras_contagem.csv", index=False, encoding="utf-8")

    x = np.arange(6)
    rot = [q[2:4] + "-" + q[-2:] for q in PER]
    for nome, pares in (("ppa_inteiro_inovacao_x_educacao.png", ["inovação", "educação"]),
                        ("ppa_inteiro_inovacao_e_industria.png", ["inovação", "indústria", "competitividade", "empresa"])):
        fig, ax = plt.subplots(figsize=(7.2, 3.6))
        for k, tema in enumerate(pares):
            r = t[(t.recorte == "PPA inteiro") & (t.tema == tema)].iloc[0]
            ax.plot(x, [r[q] for q in PER], "o-", color=SERIES[k], lw=2, label=tema)
        ax.set_xticks(x, rot)
        ax.set_ylabel("% dos lemas do PPA")
        ax.set_ylim(0, None)
        eixo_limpo(ax)
        ax.legend(frameon=False, fontsize=9, ncol=len(pares))
        titulo(ax, "PPA inteiro (514 programas): % dos lemas de cada tema",
               "objetivo + justificativa; contagem simples")
        salvar(fig, nome)
        plt.close(fig)
    return t, s


# ------------------------------------------------------------------ item 2
def item2_comp_inov(p, f):
    linhas = []
    for recorte, d in (("PPA inteiro", p), ("selecionados", p[p.selecionado == 1])):
        tot = d.groupby("periodo")["n_lemas"].sum()
        c = d["lemas"].map(lambda ls: ls.count("competitividade")).groupby(d["periodo"]).sum()
        i = d["lemas"].map(lambda ls: ls.count("inovação")).groupby(d["periodo"]).sum()
        for nome, v in (("competitividade", c), ("inovação", i), ("soma", c + i)):
            linhas.append({"recorte": recorte, "palavra": nome,
                           **{f"{q} n": int(v.get(q, 0)) for q in PER},
                           **{q: 100 * v.get(q, 0) / tot[q] for q in PER}})
    serie = pd.DataFrame(linhas)

    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), sharey=False)
    x = np.arange(6)
    for ax, recorte in zip(axs, ("PPA inteiro", "selecionados")):
        for k, nome in enumerate(("competitividade", "inovação", "soma")):
            r = serie[(serie.recorte == recorte) & (serie.palavra == nome)].iloc[0]
            ax.plot(x, [r[q] for q in PER], "o-" if nome != "soma" else "s--",
                    color=SERIES[k] if nome != "soma" else TINTA2, lw=2 if nome != "soma" else 1.2, label=nome)
        ax.set_xticks(x, [q[2:4] + "-" + q[-2:] for q in PER])
        ax.set_ylim(0, None)
        eixo_limpo(ax)
        ax.set_title(recorte, loc="left", fontsize=10.5, color=TINTA)
    axs[0].set_ylabel("% dos lemas")
    axs[0].legend(frameon=False, fontsize=9)
    salvar(fig, "ppa_inteiro_competitividade_x_inovacao.png")
    plt.close(fig)

    p = p.assign(tem_c=p["lemas"].map(lambda ls: "competitividade" in ls),
                 tem_i=p["lemas"].map(lambda ls: "inovação" in ls))
    mesmos = (p.groupby("periodo")
              .agg(programas=("codigo", "size"), com_competitividade=("tem_c", "sum"), com_inovacao=("tem_i", "sum"),
                   com_as_duas=("tem_c", lambda s: int((s & p.loc[s.index, "tem_i"]).sum())))
              .reset_index())

    # programas com competitividade em 2024-2027: o que tinham em 2020-2023?
    ult = p[(p.periodo == "2024-2027") & (p.tem_c | p.tem_i)]
    ant = p[p.periodo == "2020-2023"].set_index("serie")
    troca = pd.DataFrame([{
        "codigo": r.codigo, "nome": r.nome, "selecionado": r.selecionado,
        "2024-27 competitividade": int(r.tem_c), "2024-27 inovação": int(r.tem_i),
        "2020-23 competitividade": int(ant.loc[r.serie, "tem_c"]) if r.serie in ant.index else None,
        "2020-23 inovação": int(ant.loc[r.serie, "tem_i"]) if r.serie in ant.index else None,
    } for r in ult.itertuples()])

    fr = f[f.periodo == "2024-2027"].copy()
    fr["palavra"] = fr["lemas"].map(lambda ls: ", ".join(w for w in ("competitividade", "inovação") if w in ls))
    frases = fr[fr.palavra != ""][["palavra", "codigo", "selecionado", "campo", "frase"]].sort_values(["palavra", "codigo"])
    serie.to_csv(SAIDAS / "ppa_inteiro_comp_inov_serie.csv", index=False, encoding="utf-8")
    frases.to_csv(SAIDAS / "ppa_inteiro_comp_inov_frases_2024.csv", index=False, encoding="utf-8")
    return serie, mesmos, troca, frases


# ------------------------------------------------------------------ item 3
def item3_publico(p):
    tab = p[["periodo", "codigo", "nome", "orgao", "selecionado", "publico_alvo"]].assign(
        publico_categorias=p["publico_cat"].map(", ".join), oferta_area=p["area"])
    tab.to_csv(SAIDAS / "ppa_inteiro_publico_alvo.csv", index=False, encoding="utf-8")
    cats = ["empresas", "micro e pequenas empresas", "trabalhadores", "produtores rurais", "municípios",
            "instituições de pesquisa", "sociedade em geral", "outros"]
    dem = []
    for recorte, d in (("PPA inteiro", p), ("selecionados", p[p.selecionado == 1])):
        n = d.groupby("periodo").size()
        for c in cats:
            k = d[d["publico_cat"].map(lambda xs: c in xs)].groupby("periodo").size()
            dem.append({"recorte": recorte, "categoria": c, **{q: 100 * k.get(q, 0) / n[q] for q in PER}})
    demanda = pd.DataFrame(dem)
    of = []
    for recorte, d in (("PPA inteiro", p), ("selecionados", p[p.selecionado == 1])):
        x = pd.crosstab(d["area"], d["periodo"], normalize="columns").reindex(columns=PER).fillna(0) * 100
        of.append(x.reset_index().assign(recorte=recorte))
    oferta = pd.concat(of, ignore_index=True)[["recorte", "area"] + PER]
    demanda.to_csv(SAIDAS / "ppa_inteiro_publico_demanda.csv", index=False, encoding="utf-8")
    oferta.to_csv(SAIDAS / "ppa_inteiro_publico_oferta.csv", index=False, encoding="utf-8")
    return tab, demanda, oferta


# ------------------------------------------------------------------ item 4
def item4_subacoes(p, s):
    x = s.explode("tema").dropna(subset=["tema"])
    lista = x[["periodo", "tema", "programa", "nome", "selecionado", "subacao", "texto", "unidade", "valor", "pct_ppa"]]
    lista.to_csv(SAIDAS / "ppa_inteiro_subacoes_tema.csv", index=False, encoding="utf-8")
    tot = s.groupby("periodo")["valor"].sum()
    var = []
    for (tema, q), g in x.groupby(["tema", "periodo"]):
        var.append({"tema": tema, "periodo": q, "base": "1 ano" if q in PER[:2] else "quadriênio",
                    "subacoes": len(g), "programas": g.programa.nunique(),
                    "valor": g.valor.sum(), "pct_ppa": 100 * g.valor.sum() / tot[q],
                    "valor_nos_selecionados": g.loc[g.selecionado == 1, "valor"].sum(),
                    "pct_ppa_fora_dos_selecionados": 100 * g.loc[g.selecionado == 0, "valor"].sum() / tot[q]})
    variaveis = pd.DataFrame(var)
    variaveis.to_csv(SAIDAS / "ppa_inteiro_variaveis_tema.csv", index=False, encoding="utf-8")

    # mesmo tema, programas diferentes: % do PPA por programa
    por_prog = (x.groupby(["tema", "programa", "periodo"])["pct_ppa"].sum().unstack("periodo")
                .reindex(columns=PER).fillna(0).reset_index())
    nomes = p.sort_values("periodo").groupby("codigo")["nome"].last()
    por_prog.insert(2, "nome (último PPA)", por_prog["programa"].map(nomes).str[:55])
    por_prog["total"] = por_prog[PER].sum(axis=1)
    por_prog = por_prog.sort_values(["tema", "total"], ascending=[True, False])

    # unidade responsável dos programas selecionados, por série
    sel = p[p.selecionado == 1]
    orgaos = sel.pivot_table(index="serie", columns="periodo", values="orgao", aggfunc="first").reindex(columns=PER)
    ss = s[s.selecionado == 1]
    unid = (ss[ss.unidade != ""].groupby(["serie", "periodo"])["unidade"]
            .agg(lambda u: ", ".join(sorted(set(u) - {"SDR"}) + (["SDR"] if "SDR" in set(u) else [])))
            .unstack().reindex(columns=PER))

    # o que muda nas subações do mesmo programa entre PPAs consecutivos (código da subação)
    mud = []
    for serie, g in ss.groupby("serie"):
        for a, b in zip(PER[:-1], PER[1:]):
            A, Bq = g[g.periodo == a], g[g.periodo == b]
            if A.empty or Bq.empty:
                continue
            ca, cb = set(A.subacao), set(Bq.subacao)
            novas = Bq[~Bq.subacao.isin(ca)].sort_values("valor", ascending=False)
            mud.append({"serie": serie, "transição": f"{a} → {b}", "subações antes": len(ca),
                        "subações depois": len(cb), "mantidas (mesmo código)": len(ca & cb),
                        "% do valor em subações mantidas": 100 * Bq[Bq.subacao.isin(ca)].valor.sum() / Bq.valor.sum()
                        if Bq.valor.sum() else np.nan,
                        "maiores subações novas": " | ".join(novas.texto.str.split(" \\| ").str[-1].str[:60].head(3))})
    mudancas = pd.DataFrame(mud)
    mudancas.to_csv(SAIDAS / "ppa_inteiro_subacoes_mudancas.csv", index=False, encoding="utf-8")
    return lista, variaveis, por_prog, orgaos, unid, mudancas


# ------------------------------------------------------------------ item 5
def _norm(s):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", sem_acento(s)).split())


def item5_copia(p, f, limiar=0.9):
    f = f.copy()
    f["norm"] = f["frase"].map(_norm)
    f["n_lemas"] = f["lemas"].str.len()
    f["sim_anterior"] = np.nan
    for a, b in zip(PER[:-1], PER[1:]):
        ant = f.loc[f.periodo == a, "norm"].tolist()
        exatas = set(ant)
        for i in f.index[f.periodo == b]:
            s = f.at[i, "norm"]
            if s in exatas:
                f.at[i, "sim_anterior"] = 1.0
                continue
            best = 0.0
            for t in ant:
                if not (0.75 <= len(t) / max(len(s), 1) <= 1.33):
                    continue
                m = SequenceMatcher(None, s, t, autojunk=False)
                if m.real_quick_ratio() <= best or m.quick_ratio() <= best:
                    continue
                best = max(best, m.ratio())
            f.at[i, "sim_anterior"] = best
    f["copiada"] = f["sim_anterior"] >= limiar
    f["identica"] = f["sim_anterior"] >= 0.9999
    linhas = []
    for a, b in zip(PER[:-1], PER[1:]):
        for recorte, g in (("PPA inteiro", f[f.periodo == b]), ("selecionados", f[(f.periodo == b) & (f.selecionado == 1)])):
            n = g.n_lemas.sum()
            linhas.append({"transição": f"{a} → {b}", "governo": TRANSICOES[f"{a} → {b}"], "recorte": recorte,
                           "% lemas em frases idênticas": 100 * g.loc[g.identica, "n_lemas"].sum() / n,
                           "% lemas em frases iguais ou quase (≥ 0,9)": 100 * g.loc[g.copiada, "n_lemas"].sum() / n})
    trans = pd.DataFrame(linhas)

    prog = (f[f.periodo != PER[0]].groupby(["periodo", "codigo", "selecionado"])
            .apply(lambda g: 100 * g.loc[g.copiada, "n_lemas"].sum() / max(g.n_lemas.sum(), 1), include_groups=False)
            .rename("% lemas copiados").reset_index())

    termos = TEMAS["competitividade"]
    comp = []
    for recorte, g in (("PPA inteiro", f), ("selecionados", f[f.selecionado == 1])):
        for versao, h in (("todo o texto", g), ("só frases reescritas", g[~g.copiada])):
            oc = h["lemas"].map(lambda ls: contar(ls, termos)).groupby(h.periodo).sum()
            n = h.groupby("periodo").n_lemas.sum()
            comp.append({"recorte": recorte, "texto": versao,
                         **{q: 100 * oc.get(q, 0) / n[q] for q in PER},
                         **{f"{q} ocorr": int(oc.get(q, 0)) for q in PER}})
    comp = pd.DataFrame(comp)
    f.drop(columns=["lemas"]).to_csv(SAIDAS / "ppa_inteiro_frases_copia.csv", index=False, encoding="utf-8")
    trans.to_csv(SAIDAS / "ppa_inteiro_copia_transicoes.csv", index=False, encoding="utf-8")
    prog.to_csv(SAIDAS / "ppa_inteiro_copia_programas.csv", index=False, encoding="utf-8")
    comp.to_csv(SAIDAS / "ppa_inteiro_competitividade_reescrito.csv", index=False, encoding="utf-8")
    return trans, prog, comp


# ------------------------------------------------------------------ item 6
def item6_fichas(p, s):
    sel = p[p.selecionado == 1].sort_values(["serie", "periodo"])
    out = ["# Fichas dos programas selecionados", "",
           "Gerado por scripts/ppa_inteiro_analise.py (item6_fichas). Campos lidos do PDF; "
           "\"O que não faz\" fica para a leitura qualitativa.", ""]
    for serie, g in sel.groupby("serie", sort=False):
        out.append(f"## Série {serie}")
        for r in g.itertuples():
            sub = s[(s.periodo == r.periodo) & (s.programa == r.codigo)].sort_values("valor", ascending=False)
            tot = sub.valor.sum()
            out += [f"### {r.codigo} {r.nome} ({r.periodo})", "",
                    f"- **Órgão responsável:** {r.orgao}",
                    f"- **Público-alvo (como no PDF, até 50 caracteres):** {r.publico_alvo}",
                    f"- **O que é / propósito (objetivo):** {r.objetivo}",
                    f"- **Subações:** {len(sub)}; soma {tot / 1e6:,.1f} mi ({'1 ano' if r.periodo in PER[:2] else 'quadriênio'})".replace(",", "X").replace(".", ",").replace("X", "."),
                    "- **Principais subações (o que faz):**"]
            for x in sub.head(5).itertuples():
                pct = 100 * x.valor / tot if tot else 0
                out.append(f"  - {x.texto.split(' | ')[-1][:110]} ({pct:.0f}% do programa)".replace(".", ","))
            out += ["- **O que não faz:** [preencher na leitura]", ""]
    (SAIDAS / "fichas_programas_selecionados.md").write_text("\n".join(out), encoding="utf-8")

    sec = (sel.groupby("periodo")["orgao"].agg(lambda o: "; ".join(sorted(set(o)))).rename("secretarias dos selecionados"))
    gov = GOVERNOS.merge(sec, left_on="periodo", right_index=True)
    gov["programas no PPA"] = gov.periodo.map(p.groupby("periodo").size())
    gov["órgãos responsáveis distintos"] = gov.periodo.map(p.groupby("periodo")["orgao"].nunique())

    # programas que entram e saem (por código; 2004-2007 tem outra numeração e fica de fora)
    es = []
    for a, b in zip(PER[1:-1], PER[2:]):
        ca, cb = set(p.loc[p.periodo == a, "codigo"]), set(p.loc[p.periodo == b, "codigo"])
        es.append({"transição": f"{a} → {b}", "governo": TRANSICOES[f"{a} → {b}"],
                   "mantidos": len(ca & cb), "entram": len(cb - ca), "saem": len(ca - cb),
                   "% renovado": 100 * len(cb - ca) / len(cb)})
    entra_sai = pd.DataFrame(es)

    tot = s.groupby("periodo").valor.sum()
    sem = s[(s.pessoal == 0) & (s.emenda == 0)]
    tot_sem = sem.groupby("periodo").valor.sum()
    ar = (s.groupby(["area", "periodo"]).valor.sum().unstack().reindex(columns=PER).fillna(0).div(tot[PER]) * 100)
    ar_sem = (sem.groupby(["area", "periodo"]).valor.sum().unstack().reindex(columns=PER).fillna(0).div(tot_sem[PER]) * 100)
    ar.to_csv(SAIDAS / "ppa_inteiro_orcamento_area.csv", encoding="utf-8")
    ar_sem.to_csv(SAIDAS / "ppa_inteiro_orcamento_area_sem_pessoal_emendas.csv", encoding="utf-8")
    return gov, entra_sai, ar.sort_values(PER[-1], ascending=False), ar_sem.sort_values(PER[-1], ascending=False)


# ------------------------------------------------------------------ itens 7 a 10
def item7_bigramas(f, top=10):
    linhas = []
    for recorte, d in (("PPA inteiro", f), ("selecionados", f[f.selecionado == 1])):
        for q in PER:
            c = Counter((a, b) for ls in d.loc[d.periodo == q, "lemas"] for a, b in zip(ls, ls[1:]))
            for k, ((a, b), n) in enumerate(c.most_common(top), 1):
                linhas.append({"recorte": recorte, "periodo": q, "posição": k, "bigrama": f"{a} {b}", "n": n})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "ppa_inteiro_bigramas.csv", index=False, encoding="utf-8")
    return t


def item8_coocorrencia(f, alvos=("inovação", "competitividade", "indústria", "tecnologia", "empresa"), top=6):
    linhas = []
    for alvo in alvos:
        for q in PER:
            fr = [ls for ls in f.loc[f.periodo == q, "lemas"] if alvo in ls]
            c = Counter(w for ls in fr for w in set(ls) if w != alvo)
            linhas.append({"alvo": alvo, "periodo": q, "frases com o alvo": len(fr),
                           "mais frequentes na mesma frase (nº de frases)":
                               ", ".join(f"{w} ({n})" for w, n in c.most_common(top))})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "ppa_inteiro_coocorrencia.csv", index=False, encoding="utf-8")
    return t


def _squarify(vals, x, y, w, h):
    vals = list(vals)
    soma = sum(vals)
    vals = [v * w * h / soma for v in vals]
    rects = []

    def pior(row, lado):
        s = sum(row)
        return max(max(lado * lado * r / (s * s), s * s / (lado * lado * r)) for r in row)

    while vals:
        lado = min(w, h)
        row, i = [vals[0]], 1
        while i < len(vals) and pior(row + [vals[i]], lado) <= pior(row, lado):
            row.append(vals[i])
            i += 1
        s = sum(row)
        if w >= h:
            cw, yy = s / h, y
            for r in row:
                rects.append((x, yy, cw, r / cw))
                yy += r / cw
            x, w = x + cw, w - cw
        else:
            rh, xx = s / w, x
            for r in row:
                rects.append((xx, y, r / rh, rh))
                xx += r / rh
            y, h = y + rh, h - rh
        vals = vals[i:]
    return rects


def item9_treemap(p, top=25, recorte="PPA inteiro"):
    d = p if recorte == "PPA inteiro" else p[p.selecionado == 1]
    fig, axs = plt.subplots(2, 3, figsize=(15, 8.5))
    tabela = []
    for ax, q in zip(axs.ravel(), PER):
        c = Counter(w for ls in d.loc[d.periodo == q, "lemas"] for w in ls).most_common(top)
        tabela += [{"periodo": q, "lema": w, "n": n} for w, n in c]
        rects = _squarify([n for _, n in c], 0, 0, 1, 1)
        mx = c[0][1]
        for (w, n), (rx, ry, rw, rh) in zip(c, rects):
            cor = plt.get_cmap("Blues")(0.25 + 0.6 * n / mx)
            ax.add_patch(plt.Rectangle((rx, ry), rw, rh, facecolor=cor, edgecolor="white", lw=1.2))
            # fonte cabe na largura (painel de ~4,6 pol.) e na altura (2 linhas) da célula
            fs = min(11, rw * 4.6 * 72 / (0.62 * len(w) + 0.8), rh * 3.6 * 72 / 2.6)
            if fs >= 5.5:
                ax.text(rx + rw / 2, ry + rh / 2, f"{w}\n{n}", ha="center", va="center",
                        fontsize=fs, color=TINTA if n < 0.7 * mx else "white")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title(f"{q} ({d.loc[d.periodo == q, 'n_lemas'].sum():,} lemas)".replace(",", "."),
                     loc="left", fontsize=10.5, color=TINTA)
    fig.suptitle(f"{top} lemas mais frequentes por PPA ({recorte}), área proporcional à contagem",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    nome = "ppa_inteiro_treemap.png" if recorte == "PPA inteiro" else "selecionados_treemap.png"
    salvar(fig, nome)
    plt.close(fig)
    return pd.DataFrame(tabela)


def item10_refazer(p):
    termos = ["inovação", "competitividade", "digital", "internacional", "emprego"]
    ev = []
    for recorte, d in (("selecionados", p[p.selecionado == 1]), ("PPA inteiro", p)):
        tot = d.groupby("periodo").n_lemas.sum()
        for w in termos:
            oc = d["lemas"].map(lambda ls: ls.count(w)).groupby(d.periodo).sum()
            ev.append({"recorte": recorte, "termo": w, **{q: 1000 * oc.get(q, 0) / tot[q] for q in PER},
                       **{f"{q} n": int(oc.get(q, 0)) for q in PER}})
    ev = pd.DataFrame(ev)

    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    x = np.arange(6)
    for ax, recorte in zip(axs, ("selecionados", "PPA inteiro")):
        for k, w in enumerate(termos):
            r = ev[(ev.recorte == recorte) & (ev.termo == w)].iloc[0]
            ax.plot(x, [r[q] for q in PER], "o-", color=SERIES[k], lw=1.8, label=w)
        ax.set_xticks(x, [q[2:4] + "-" + q[-2:] for q in PER])
        ax.set_ylim(0, None)
        eixo_limpo(ax)
        ax.set_title(recorte, loc="left", fontsize=10.5, color=TINTA)
    axs[0].set_ylabel("ocorrências por mil lemas")
    axs[0].legend(frameon=False, fontsize=8.5)
    salvar(fig, "contagem_evolucao_termos_chave.png")
    plt.close(fig)

    sims = {}
    for recorte, d in (("selecionados", p[p.selecionado == 1]), ("PPA inteiro", p)):
        cont = {q: Counter(w for ls in d.loc[d.periodo == q, "lemas"] for w in ls) for q in PER}
        vocab = sorted(set().union(*cont.values()))
        M = np.array([[cont[q].get(w, 0) for w in vocab] for q in PER], float)
        M = M / np.linalg.norm(M, axis=1, keepdims=True)
        sims[recorte] = pd.DataFrame(M @ M.T, index=PER, columns=PER)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, (recorte, S) in zip(axs, sims.items()):
        ax.imshow(S.values, cmap="Blues", vmin=0, vmax=1)
        for i in range(6):
            for j in range(6):
                ax.text(j, i, f"{S.values[i, j]:.2f}".replace(".", ","), ha="center", va="center", fontsize=8.5,
                        color="white" if S.values[i, j] > 0.75 else TINTA)
        rot = [q[2:4] + "-" + q[-2:] for q in PER]
        ax.set_xticks(range(6), rot, fontsize=8.5)
        ax.set_yticks(range(6), rot, fontsize=8.5)
        ax.set_title(f"{recorte}: cosseno das contagens", loc="left", fontsize=10.5, color=TINTA)
    salvar(fig, "contagem_similaridade_entre_ppas.png")
    plt.close(fig)
    ev.to_csv(SAIDAS / "contagem_evolucao_termos_chave.csv", index=False, encoding="utf-8")
    pd.concat({k: v for k, v in sims.items()}).to_csv(SAIDAS / "contagem_similaridade_entre_ppas.csv", encoding="utf-8")
    return ev, sims
