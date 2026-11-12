"""Testes adicionais do achado de competitividade (revisão de 12/11/2026).

1. Viés de seleção: a mesma medida no PPA inteiro (514 programas) e só nos programas NÃO selecionados.
   Se a linguagem de competitividade sobe também fora da lista, o achado não vem da curadoria.
2. Semente x expansão: só "competitividade" ao lado da dimensão expandida (os termos novos vieram de
   coocorrência com a semente e podem reproduzir a trajetória dela).
3. Último PPA x anteriores: diferença entre a taxa de 2024-2027 e a taxa conjunta de 2004-2023,
   com p por permutação (embaralha o período dos programas) e IC por bootstrap.
4. Sem o 0353 (Incentivo à Competitividade da Indústria, do Comércio e do Serviço), que só existe em
   2024-2027 e tem "competitividade" no nome.
5. Digital somada a inovação (a dimensão digital tem um termo só).
Também reporta as contagens brutas (ocorrências e lemas por período).

Testes de trajetória: os mesmos de indice_lexico.py (amplitude relativa e tendência de Spearman).
Saída: saidas/robustez_competitividade.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from circularidade import amplitude_rel, tendencia

S = Path(__file__).resolve().parent.parent / "saidas"
RNG = np.random.default_rng(42)
NPERM, NBOOT = 5000, 2000
COMP = ["competitividade", "produtividade", "competitivo", "diversificação"]
INOV = ["inovação", "tecnologia", "modernização", "tecnológico"]


def preparar(df):
    df = df.copy()
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    per = sorted(df.periodo.unique())
    pidx = df.periodo.map({p: i for i, p in enumerate(per)}).to_numpy()
    cv = CountVectorizer(token_pattern=r"\S+", lowercase=False)
    X = cv.fit_transform(df.texto_lematizado)
    ix = {t: i for i, t in enumerate(cv.get_feature_names_out())}
    return per, pidx, X, ix, np.asarray(X.sum(axis=1)).ravel()


def taxa(serie, ntok, pidx, nper):
    return np.bincount(pidx, weights=serie, minlength=nper) / np.bincount(pidx, weights=ntok, minlength=nper) * 1000


def ultimo_vs_antes(serie, ntok, pidx, nper):
    u = pidx == nper - 1
    return serie[u].sum() / ntok[u].sum() * 1000 - serie[~u].sum() / ntok[~u].sum() * 1000


def testar(nome, df, termos):
    per, pidx, X, ix, ntok = preparar(df)
    nper = len(per)
    cols = [ix[t] for t in termos if t in ix]
    serie = np.asarray(X[:, cols].sum(axis=1)).ravel()
    obs = taxa(serie, ntok, pidx, nper)
    amp, tr, dif = amplitude_rel(obs[:, None])[0], tendencia(obs[:, None])[0], ultimo_vs_antes(serie, ntok, pidx, nper)
    ca = ct = cd = 0
    for _ in range(NPERM):
        pm = RNG.permutation(pidx)
        r = taxa(serie, ntok, pm, nper)
        ca += amplitude_rel(r[:, None])[0] >= amp
        ct += abs(tendencia(r[:, None])[0]) >= abs(tr)
        cd += ultimo_vs_antes(serie, ntok, pm, nper) >= dif
    grupos = [np.where(pidx == i)[0] for i in range(nper)]
    boot = []
    for _ in range(NBOOT):
        s = np.concatenate([RNG.choice(g, len(g)) for g in grupos])
        boot.append(ultimo_vs_antes(serie[s], ntok[s], pidx[s], nper))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    linha = {"teste": nome, "termos": ", ".join(t for t in termos if t in ix), "documentos": len(df),
             "p_amplitude": (1 + ca) / (NPERM + 1), "p_tendencia": (1 + ct) / (NPERM + 1),
             "spearman": round(tr, 2), "dif_ultimo_vs_antes": round(dif, 1), "dif_ic_inf": round(lo, 1),
             "dif_ic_sup": round(hi, 1), "p_ultimo_maior": (1 + cd) / (NPERM + 1)}
    for i, p in enumerate(per):
        m = pidx == i
        linha[f"{p} taxa"] = round(obs[i], 1)
        linha[f"{p} ocorr/lemas"] = f"{int(serie[m].sum())}/{int(ntok[m].sum())}"
    return linha


def main():
    sel = pd.read_csv(S / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str})
    todos = pd.read_csv(S / "programas_todos.csv", encoding="utf-8", dtype={"codigo": str})
    nao_sel = todos[~todos.selecionado.astype(bool)]
    sem_0353 = sel[~((sel.codigo.str.zfill(4) == "0353") & (sel.periodo == "2024-2027"))]
    casos = [
        ("selecionados | dimensão", sel, COMP),
        ("selecionados | só a semente", sel, ["competitividade"]),
        ("selecionados | só os termos novos", sel, COMP[1:]),
        ("selecionados sem o 0353 | dimensão", sem_0353, COMP),
        ("selecionados sem o 0353 | só a semente", sem_0353, ["competitividade"]),
        ("PPA inteiro | dimensão", todos, COMP),
        ("PPA inteiro | só a semente", todos, ["competitividade"]),
        ("não selecionados | dimensão", nao_sel, COMP),
        ("não selecionados | só a semente", nao_sel, ["competitividade"]),
        ("selecionados | inovação + digital", sel, INOV + ["computador"]),
    ]
    out = []
    for nome, df, termos in casos:
        out.append(testar(nome, df, termos))
        print("ok:", nome, flush=True)
    r = pd.DataFrame(out)
    r.to_csv(S / "robustez_competitividade.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 40)
    print(r[["teste", "documentos", "p_amplitude", "p_tendencia", "spearman", "dif_ultimo_vs_antes",
             "dif_ic_inf", "dif_ic_sup", "p_ultimo_maior"]].to_string(index=False))
    print(r[["teste"] + [c for c in r.columns if c.endswith("taxa")]].to_string(index=False))
    print(r[["teste"] + [c for c in r.columns if c.endswith("lemas")]].to_string(index=False))


if __name__ == "__main__":
    main()
