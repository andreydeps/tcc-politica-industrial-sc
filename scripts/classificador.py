"""Classificador de texto para conferir a curadoria (inspirado em Juhász, Lane, Oehlsen e Pérez, 2025).

NÃO é regressão econométrica: é um classificador que aprende com a seleção manual quais textos
de programa parecem "política industrial" e devolve, para cada programa, uma probabilidade.
Serve para três coisas:
  1. programas NÃO selecionados que o modelo acha parecidos com os selecionados (rever curadoria);
  2. programas selecionados que o modelo acha pouco parecidos (casos frágeis);
  3. as palavras que mais pesam (validação de face, como no artigo).

Entradas: PDFs (cache de texto) e definições do notebook (regex, lista de códigos, equivalência)
Saídas  : saidas/programas_todos.csv          todos os programas dos 6 PPAs, com texto lematizado
          saidas/classificador_programas.csv  probabilidade fora da amostra para cada programa
          saidas/classificador_palavras.csv   coeficientes das palavras

Método: TF-IDF de unigramas e bigramas sobre objetivo + justificativa lematizados; regressão
logística com penalidade L1 e pesos balanceados (poucos positivos). Validação cruzada por GRUPO:
o mesmo programa (série) em outro período nunca está no treino quando ele é testado, para o
modelo não "decorar" texto copiado entre ciclos. A probabilidade de cada programa vem do modelo
que não o viu.
"""
import ast
import re
import sys
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocos_programas import definicoes_do_notebook, texto_pdf  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
CORTE_PUBLICO = re.compile(r"\s*p[úu]blico[\s-]*alvo\s*:", re.IGNORECASE)


def equivalencia():
    nb = nbformat.read(RAIZ / "notebooks" / "TCC.ipynb", as_version=4)
    src = next(c.source for c in nb.cells if c.cell_type == "code" and "equivalencia_2004 = {" in c.source)
    return ast.literal_eval(re.search(r"equivalencia_2004 = (\{.*?\n\})", src, re.S).group(1))


def todos_os_programas():
    arq = SAIDAS / "programas_todos.csv"
    if arq.exists():
        return pd.read_csv(arq, encoding="utf-8", dtype={"codigo": str})
    ns = definicoes_do_notebook()
    regex = {"2004-2007": ns["padrao_2004"], "2008-2011": ns["padrao_2008"]}
    limpar = {"2004-2007": ns["rodape_2004"], "2008-2011": ns["rodape_2008"]}
    linhas = []
    for per, cam in ns["caminhos"].items():
        t = texto_pdf(cam)
        if per in limpar:
            t = limpar[per].sub(" ", t)
        for m in regex.get(per, ns["padrao"]).finditer(t):
            d = m.groupdict()
            nome = " ".join((d["nome"] + " " + (d.get("nome2") or "")).split())
            just = CORTE_PUBLICO.split(d["justificativa"], maxsplit=1)[0]
            linhas.append({"periodo": per, "codigo": d["codigo"], "nome": nome,
                           "objetivo": " ".join(d["objetivo"].split()), "justificativa": " ".join(just.split())})
    df = pd.DataFrame(linhas).drop_duplicates(["periodo", "codigo", "objetivo"])
    sel = ns["codigos_industria"]
    df["selecionado"] = [int(c in sel.get(p, [])) for p, c in zip(df["periodo"], df["codigo"])]
    nlp = spacy.load("pt_core_news_lg", disable=["ner", "parser"])
    lema = lambda doc: " ".join(tk.lemma_.lower() for tk in doc if not tk.is_stop and not tk.is_punct
                                and not tk.is_space and tk.is_alpha and tk.pos_ in {"NOUN", "VERB", "ADJ"})
    textos = (df["objetivo"] + " " + df["justificativa"]).tolist()
    df["texto_lematizado"] = [lema(d) for d in nlp.pipe(textos, batch_size=32)]
    df.to_csv(arq, index=False, encoding="utf-8")
    return df


def main():
    df = todos_os_programas()
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    eq = equivalencia()
    # grupo = série do programa (2004-2007 tem numeração própria: só os equivalentes entram na série)
    df["grupo"] = [eq.get(c, f"2004:{c}") if p == "2004-2007" else c for c, p in zip(df["codigo"], df["periodo"])]
    y = df["selecionado"].to_numpy()
    print(f"Programas: {len(df)} | selecionados: {y.sum()} | por período:",
          df.groupby("periodo")["selecionado"].agg(["size", "sum"]).to_dict("index"))

    def modelo():
        return (TfidfVectorizer(token_pattern=r"\S+", ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                LogisticRegression(l1_ratio=1.0, solver="liblinear", C=2.0, class_weight="balanced", max_iter=2000))

    prob = np.zeros(len(df))
    for tr, te in GroupKFold(n_splits=5).split(df, y, df["grupo"]):
        vec, clf = modelo()
        Xtr = vec.fit_transform(df["texto_lematizado"].iloc[tr])
        clf.fit(Xtr, y[tr])
        prob[te] = clf.predict_proba(vec.transform(df["texto_lematizado"].iloc[te]))[:, 1]
    pred = (prob >= 0.5).astype(int)
    base = y.mean()
    print(f"\nFora da amostra (validação cruzada por série): precisão {precision_score(y, pred):.2f} | "
          f"revocação {recall_score(y, pred):.2f} | F1 {f1_score(y, pred):.2f} | "
          f"precisão média {average_precision_score(y, prob):.2f} (acaso = {base:.2f})")

    df["prob_politica_industrial"] = prob.round(3)
    df[["periodo", "codigo", "nome", "selecionado", "prob_politica_industrial", "objetivo"]].sort_values(
        "prob_politica_industrial", ascending=False).to_csv(SAIDAS / "classificador_programas.csv", index=False, encoding="utf-8")

    vec, clf = modelo()
    clf.fit(vec.fit_transform(df["texto_lematizado"]), y)
    coef = pd.DataFrame({"termo": vec.get_feature_names_out(), "coef": clf.coef_[0]})
    coef = coef[coef.coef != 0].sort_values("coef", ascending=False)
    coef.to_csv(SAIDAS / "classificador_palavras.csv", index=False, encoding="utf-8")

    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 70)
    print("\n=== Palavras que mais indicam política industrial (modelo com todos os dados) ===")
    print(", ".join(f"{t} ({c:.1f})" for t, c in coef.head(20).itertuples(index=False)))
    neg = coef[coef.coef < 0].sort_values("coef")
    print(f"\nTermos com peso diferente de zero: {len(coef)} ({(coef.coef > 0).sum()} positivos, {len(neg)} negativos)")
    if len(neg):
        print("=== Palavras que mais indicam o contrário ===")
        print(", ".join(f"{t} ({c:.1f})" for t, c in neg.head(12).itertuples(index=False)))
    print("\n=== NÃO selecionados que o modelo acha parecidos (rever curadoria) ===")
    nao = df[df.selecionado == 0].sort_values("prob_politica_industrial", ascending=False).head(15)
    print(nao[["periodo", "codigo", "nome", "prob_politica_industrial"]].to_string(index=False))
    print("\n=== Selecionados que o modelo acha pouco parecidos (casos frágeis) ===")
    sim = df[df.selecionado == 1].sort_values("prob_politica_industrial").head(12)
    print(sim[["periodo", "codigo", "nome", "prob_politica_industrial"]].to_string(index=False))
    print("\n=== Proporção de programas por período: selecionados x previstos pelo modelo (prob >= 0,5) ===")
    print(df.assign(previsto=pred).groupby("periodo").agg(programas=("codigo", "size"), selecionados=("selecionado", "sum"),
                                                           previstos=("previsto", "sum")).to_string())


if __name__ == "__main__":
    main()
