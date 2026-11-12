"""Aprofundamento do achado central: competitividade.

Parte 1, "que competitividade é essa?": lê as frases do texto ORIGINAL (objetivo + justificativa)
com competitividade, competitivo, produtividade ou diversificação, período a período, e marca
DE QUEM é a competitividade (empresas, indústria, agro, economia catarinense, região, setores) e
com que palavras ela anda. Frases copiadas de um ciclo anterior são marcadas como herança.

Parte 2, "tira um programa": refaz o teste da dimensão "competitividade e produção" (léxico
validado) e do termo isolado "competitividade" tirando UM programa de cada vez. Mostra se o
resultado depende de algum programa específico.

Entrada : saidas/corpus_programas.csv, saidas/lexico_validado.csv
Saídas  : saidas/competitividade_frases.csv, saidas/competitividade_tira_um.csv
"""
import re
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from circularidade import amplitude_rel

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
RNG = np.random.default_rng(42)

TERMOS = r"competitiv|produtividade|diversifica"
DE_QUEM = {   # sobre a frase sem acento, em minúsculas
    "empresas": r"\bempresa|empreendedor|micro e pequena|\bmpe|\bmei\b|negocio",
    "indústria": r"industria|industrial",
    "agro e pesca": r"agro|agricult|pesca|pesqueir|rural|cadeias produtivas",
    "economia catarinense / estado": r"economia catarinense|santa catarina|\bestado\b|catarinense|\bsc\b",
    "regiões": r"regiao|regioes|regional|territori|municipio",
    "setores estratégicos": r"setores? estrategic|\bsetores?\b",
    "inserção externa": r"internacional|mercado(s)? (externo|mundial|global)|exporta|mundial",
}


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def frases(texto):
    return [" ".join(f.split()) for f in re.split(r"(?<=[.;!?])\s+", str(texto)) if f.strip()]


def parte1(df):
    periodos = sorted(df.periodo.unique())
    vistas, linhas = {}, []
    for per in periodos:
        for _, r in df[df.periodo == per].iterrows():
            for fr in frases(r["texto_completo"]):
                fn = sem_acento(fr)
                if not re.search(TERMOS, fn):
                    vistas.setdefault(fn, per)
                    continue
                origem = vistas.setdefault(fn, per)
                linhas.append({"periodo": per, "codigo": r["codigo"], "frase": fr,
                               "heranca_de": origem if origem != per else "",
                               **{k: int(bool(re.search(p, fn))) for k, p in DE_QUEM.items()}})
    f = pd.DataFrame(linhas)
    f.to_csv(SAIDAS / "competitividade_frases.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 200)
    print(f"Frases com competitividade/produtividade/diversificação: {len(f)} ({(f.heranca_de == '').sum()} novas, "
          f"{(f.heranca_de != '').sum()} herdadas de ciclo anterior)")
    print("\n=== De quem é a competitividade: nº de frases por período (frases novas | todas) ===")
    tab_novas = f[f.heranca_de == ""].groupby("periodo")[list(DE_QUEM)].sum()
    tab_todas = f.groupby("periodo")[list(DE_QUEM)].sum()
    tab = tab_todas.astype(str) + " (" + tab_novas.reindex(tab_todas.index, fill_value=0).astype(str) + " novas)"
    print(f.groupby("periodo").size().rename("frases").to_frame().join(tab).to_string())
    print("\n=== Frases NOVAS (não herdadas), por período ===")
    for per, g in f[f.heranca_de == ""].groupby("periodo"):
        print(f"\n[{per}]")
        for _, r in g.iterrows():
            print(f"  {r['codigo']}: {r['frase'][:240]}")


def parte2(df):
    lex = pd.read_csv(SAIDAS / "lexico_validado.csv", encoding="utf-8")
    dim = lex[(lex.decisao.isin(["entra", "variante"])) & (lex.dimensao == "competitividade e produção")].termo.tolist()
    df = df.assign(texto_lematizado=df["texto_lematizado"].fillna(""))
    cv = CountVectorizer(token_pattern=r"\S+", lowercase=False)
    X = cv.fit_transform(df["texto_lematizado"]).toarray().astype(float)
    ix = {t: i for i, t in enumerate(cv.get_feature_names_out())}
    ntok = X.sum(axis=1)
    periodos = sorted(df.periodo.unique())
    pidx = df["periodo"].map({p: i for i, p in enumerate(periodos)}).to_numpy()
    nper = len(periodos)
    alvos = {"dimensão competitividade e produção": X[:, [ix[t] for t in dim if t in ix]].sum(axis=1),
             "termo competitividade": X[:, ix["competitividade"]]}

    def teste(serie, tok, pid, B=2000):
        taxa = lambda pp: np.bincount(pp, weights=serie, minlength=nper) / np.bincount(pp, weights=tok, minlength=nper) * 1000
        obs = taxa(pid)
        amp = amplitude_rel(obs[:, None])[0]
        cont = sum(amplitude_rel(taxa(RNG.permutation(pid))[:, None])[0] >= amp for _ in range(B))
        return obs, (1 + cont) / (B + 1)

    linhas = []
    for nome, serie in alvos.items():
        obs, p = teste(serie, ntok, pidx)
        linhas.append({"alvo": nome, "retirado": "(nenhum)", "p_perm": round(p, 4),
                       **{per: round(v, 1) for per, v in zip(periodos, obs)}})
        for i in range(len(df)):
            m = np.ones(len(df), bool)
            m[i] = False
            obs, p = teste(serie[m], ntok[m], pidx[m])
            linhas.append({"alvo": nome, "retirado": f"{df.periodo.iloc[i]} {df.codigo.iloc[i]}", "p_perm": round(p, 4),
                           **{per: round(v, 1) for per, v in zip(periodos, obs)}})
    t = pd.DataFrame(linhas)
    t.to_csv(SAIDAS / "competitividade_tira_um.csv", index=False, encoding="utf-8")
    print("\n\n=== Tira um programa de cada vez ===")
    for nome, g in t.groupby("alvo", sort=False):
        base = g[g["retirado"] == "(nenhum)"].iloc[0]
        resto = g[g["retirado"] != "(nenhum)"]
        print(f"\n[{nome}] com todos: p = {base.p_perm} | 2024-2027 = {base['2024-2027']} por mil")
        print(f"  p de permutação ao tirar um programa: mínimo {resto.p_perm.min()}, máximo {resto.p_perm.max()}; "
              f"acima de 0,05 em {(resto.p_perm > 0.05).sum()} de {len(resto)} casos")
        print(f"  taxa de 2024-2027 ao tirar um programa: de {resto['2024-2027'].min()} a {resto['2024-2027'].max()} por mil")
        print("  os 5 programas cuja retirada mais enfraquece o resultado:")
        print(resto.sort_values("p_perm", ascending=False).head(5)[["retirado", "p_perm"] + periodos].to_string(index=False))


if __name__ == "__main__":
    corpus = pd.read_csv(SAIDAS / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str})
    parte1(corpus)
    parte2(corpus)

