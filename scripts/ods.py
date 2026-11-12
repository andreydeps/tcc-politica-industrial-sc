"""Vocabulário dos 17 ODS nos PPAs de Santa Catarina: está presente? cresce depois de 2015?

A busca anterior procurou só o rótulo ("ODS", "Agenda 2030") e achou zero. Aqui a pergunta é se o
CONTEÚDO dos ODS aparece, mesmo sem a sigla, e se ganha espaço depois da adoção da Agenda 2030
(setembro de 2015), ou seja, a partir do PPA 2016-2019.

Entradas: dados/ods/ods_metas_onu_brasil.csv (17 objetivos e 169 metas, texto oficial da ONU Brasil)
          saidas/programas_todos.csv (514 programas dos 6 PPAs) e saidas/corpus_programas.csv (42 selecionados)
Saídas  : dados/ods/lexico_ods.csv                léxico de cada ODS (revisável)
          saidas/ods_taxas.csv                    taxa por mil lemas, por ODS, período e corpus
          saidas/ods_antes_depois.csv             antes x depois de 2015, com teste de permutação
          saidas/ods_semantico_programas.csv      ODS mais próximo de cada programa (vetores do spaCy)
          saidas/ods_mapa_ppa.png, saidas/ods_antes_depois.png

Duas medidas:
- LEXICAL: termos característicos de cada ODS = lemas com maior TF-IDF no texto do ODS (objetivo +
  metas) em comparação com os outros 16, que aparecem em no máximo 3 ODS (descarta vocabulário comum
  a todos, como "país", "promover", "desenvolvimento"). Mede-se a taxa desses termos por mil lemas.
- SEMÂNTICA: cosseno entre o vetor médio de cada programa e o vetor médio de cada ODS (vetores do
  spaCy, centralizados). Pega paráfrases que o léxico não pega.
Antes x depois: 2004-2015 (3 PPAs) contra 2016-2027 (3 PPAs). Teste de permutação: os programas são
sorteados entre os dois blocos, mantendo o tamanho de cada bloco.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from estilo import CINZA, SERIES, TINTA, TINTA2, eixo_limpo, plt, salvar, titulo

RAIZ = Path(__file__).resolve().parent.parent
S = RAIZ / "saidas"
D = RAIZ / "dados" / "ods"
RNG = np.random.default_rng(42)
ANTES = ["2004-2007", "2008-2011", "2012-2015"]
N_TERMOS, MAX_ODS = 12, 3
# Termos que o TF-IDF escolhe mas que são genéricos ou ambíguos no texto dos PPAs (revisão manual,
# 12/11/2026). Ficam registrados no lexico_ods.csv com mantido = 0.
GENERICOS = {
    "dimensão", "viver", "lugar", "homem", "adequar", "propriedade", "planta", "manter", "banco", "exportação",
    "produtividade", "vivo", "essencial", "risco", "moderno", "confiável", "produtivo", "setor", "inovação",
    "sustentar", "instituição", "regulamentação", "custo", "responsável", "atenção", "produção", "empresa", "longo",
    "conta", "padrão", "subsídio", "reportar", "regulamentar", "reforço", "ilegal", "deter", "degradar",
    "capacitação", "objetivo", "mecanismo", "renda", "bruto", "existente", "coordenação", "âmbito", "preferencial",
    # segunda revisão: casam com outros temas nos PPAs (ex.: "conservação" de rodovias, "mudança" qualquer)
    "ano", "ajudar", "base", "fornecer", "interno", "regra", "complementar", "ciência", "mudança", "conservação",
}


def lematiza(nlp, textos):
    return [" ".join(t.lemma_.lower() for t in d if not t.is_stop and not t.is_punct and not t.is_space
                     and t.is_alpha and t.pos_ in {"NOUN", "VERB", "ADJ"}) for d in nlp.pipe(textos, batch_size=32)]


def lexico_ods(nlp):
    ods = pd.read_csv(D / "ods_metas_onu_brasil.csv", encoding="utf-8")
    docs = ods.groupby("ods")["texto"].apply(" ".join).sort_index()
    titulos = ods.groupby("ods")["titulo"].first().sort_index()
    lem = lematiza(nlp, docs.tolist())
    tf = TfidfVectorizer(token_pattern=r"\S+", min_df=1)
    M = tf.fit_transform(lem).toarray()
    termos = tf.get_feature_names_out()
    em_quantos = (M > 0).sum(axis=0)
    cont = CountVectorizer(token_pattern=r"\S+", vocabulary=termos).fit_transform(lem).toarray()
    linhas = []
    for k, i in enumerate(docs.index):
        ok = (em_quantos <= MAX_ODS) & (cont[k] >= 2)        # específico do ODS e repetido nas metas
        ordem = np.argsort(-M[k] * ok)
        n_mantidos = 0
        for j in ordem:
            if not ok[j] or n_mantidos >= N_TERMOS:
                continue
            mantido = termos[j] not in GENERICOS
            n_mantidos += mantido
            linhas.append({"ods": i, "titulo": titulos[i], "termo": termos[j], "tfidf": round(M[k, j], 3),
                           "ocorrencias_nas_metas": int(cont[k, j]), "ods_em_que_aparece": int(em_quantos[j]),
                           "mantido": int(mantido)})
    lex = pd.DataFrame(linhas)
    lex.to_csv(D / "lexico_ods.csv", index=False, encoding="utf-8")
    return lex[lex.mantido == 1], dict(zip(docs.index, lem)), titulos


def main():
    nlp = spacy.load("pt_core_news_lg")
    lex, docs_lem, titulos = lexico_ods(nlp)
    print("=== Léxico de cada ODS (termos característicos das metas) ===")
    for i, g in lex.groupby("ods"):
        print(f"  ODS {i:2d} {titulos[i][:38]:<38} {', '.join(g.termo)}")

    corpora = {
        "PPA inteiro": pd.read_csv(S / "programas_todos.csv", encoding="utf-8", dtype={"codigo": str}),
        "política industrial": pd.read_csv(S / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str}),
    }
    taxas, testes, sem_rows = [], [], []
    for nome, df in corpora.items():
        df = df.assign(texto_lematizado=df["texto_lematizado"].fillna("")).reset_index(drop=True)
        periodos = sorted(df.periodo.unique())
        cv = CountVectorizer(token_pattern=r"\S+", lowercase=False)
        X = cv.fit_transform(df["texto_lematizado"]).toarray().astype(float)
        ix = {t: i for i, t in enumerate(cv.get_feature_names_out())}
        ntok = X.sum(axis=1)
        depois = (~df.periodo.isin(ANTES)).to_numpy()
        series = {i: X[:, [ix[t] for t in g.termo if t in ix]].sum(axis=1) if any(t in ix for t in g.termo) else np.zeros(len(df))
                  for i, g in lex.groupby("ods")}
        series["todos os ODS"] = X[:, sorted({ix[t] for t in lex.termo if t in ix})].sum(axis=1)

        for i, s in series.items():
            for p in periodos:
                m = (df.periodo == p).to_numpy()
                taxas.append({"corpus": nome, "ods": i, "periodo": p, "taxa_por_mil": round(s[m].sum() / ntok[m].sum() * 1000, 2)})
            r_a = s[~depois].sum() / ntok[~depois].sum() * 1000
            r_d = s[depois].sum() / ntok[depois].sum() * 1000
            obs, cont = r_d - r_a, 0
            for _ in range(3000):
                pm = RNG.permutation(depois)
                cont += abs(s[pm].sum() / ntok[pm].sum() - s[~pm].sum() / ntok[~pm].sum()) * 1000 >= abs(obs)
            testes.append({"corpus": nome, "ods": i, "titulo": titulos.get(i, "") if i != "todos os ODS" else "",
                           "ocorrencias": int(s.sum()), "taxa_2004_2015": round(r_a, 2), "taxa_2016_2027": round(r_d, 2),
                           "diferenca": round(obs, 2), "p_perm": round((1 + cont) / 3001, 4)})

        # semântica: ODS mais próximo de cada programa
        tem = np.array([nlp.vocab[t].has_vector for t in cv.get_feature_names_out()])
        W = np.array([nlp.vocab[t].vector if h else np.zeros(300) for t, h in zip(cv.get_feature_names_out(), tem)])
        mu = (X[:, tem].sum(axis=0)[:, None] * W[tem]).sum(axis=0) / X[:, tem].sum()
        Wc = np.where(tem[:, None], W - mu, 0)
        P = X @ Wc
        P = P / np.maximum(np.linalg.norm(P, axis=1, keepdims=True), 1e-9)
        O = []
        for i in sorted(docs_lem):
            v = np.array([nlp.vocab[t].vector - mu for t in docs_lem[i].split() if nlp.vocab[t].has_vector]).mean(axis=0)
            O.append(v / np.linalg.norm(v))
        sim = P @ np.array(O).T                                  # programas x 17 ODS
        prox = sim.argmax(axis=1) + 1
        for k in range(len(df)):
            sem_rows.append({"corpus": nome, "periodo": df.periodo.iloc[k], "codigo": df.codigo.iloc[k],
                             "nome": str(df.nome.iloc[k])[:80], "ods_mais_proximo": int(prox[k]),
                             "cosseno": round(float(sim[k].max()), 3)})

    t1, t2, t3 = pd.DataFrame(taxas), pd.DataFrame(testes), pd.DataFrame(sem_rows)
    t1.to_csv(S / "ods_taxas.csv", index=False, encoding="utf-8")
    t2.to_csv(S / "ods_antes_depois.csv", index=False, encoding="utf-8")
    t3.to_csv(S / "ods_semantico_programas.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    for nome in corpora:
        print(f"\n=== {nome}: antes (2004-2015) x depois (2016-2027), taxa por mil lemas ===")
        print(t2[t2.corpus == nome].drop(columns=["corpus"]).to_string(index=False))
    print("\n=== Semântica: nº de programas cujo ODS mais próximo é cada um, por período (PPA inteiro) ===")
    sp = t3[t3.corpus == "PPA inteiro"]
    print(pd.crosstab(sp.ods_mais_proximo, sp.periodo).to_string())
    si = t3[t3.corpus == "política industrial"]
    print("\n=== Semântica: ODS mais próximo dos 42 programas de política industrial ===")
    print(pd.crosstab(si.ods_mais_proximo, si.periodo).to_string())

    # ---------------- figura 1: mapa ODS x período (PPA inteiro)
    tt = t1[(t1.corpus == "PPA inteiro") & (t1.ods != "todos os ODS")].copy()
    tt["ods"] = tt["ods"].astype(int)
    mapa = tt.pivot(index="ods", columns="periodo", values="taxa_por_mil").sort_index()
    fig, ax = plt.subplots(figsize=(9.5, 7.6))
    ax.imshow(mapa.values, cmap="Blues", aspect="auto", vmin=0)
    for a in range(mapa.shape[0]):
        for c in range(mapa.shape[1]):
            v = mapa.values[a, c]
            ax.text(c, a, f"{v:.1f}".replace(".", ","), ha="center", va="center", fontsize=8,
                    color="white" if v > mapa.values.max() * 0.6 else TINTA)
    ax.set_xticks(range(mapa.shape[1]))
    ax.set_xticklabels(mapa.columns, fontsize=8.5)
    ax.set_yticks(range(mapa.shape[0]))
    ax.set_yticklabels([f"{i}. {titulos[i]}" for i in mapa.index], fontsize=8.5)
    ax.axvline(2.5, color=TINTA2, lw=1, ls="--")
    ax.text(2.55, -0.9, "Agenda 2030 (set. 2015)", fontsize=8, color=TINTA2, va="bottom")
    ax.tick_params(length=0)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    titulo(ax, "Vocabulário dos ODS no PPA inteiro", "ocorrências dos termos característicos de cada ODS por mil lemas")
    salvar(fig, "ods_mapa_ppa.png")

    # ---------------- figura 2: antes x depois, PPA inteiro e política industrial
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.4), sharey=True)
    for ax, nome in zip(axes, corpora):
        g = t2[(t2.corpus == nome) & (t2.ods != "todos os ODS")].copy()
        g["ods"] = g["ods"].astype(int)
        g = g.sort_values("ods")
        y = np.arange(len(g))
        ax.barh(y, g["diferenca"], color=[SERIES[0] if p < 0.05 else CINZA for p in g["p_perm"]], height=0.7)
        ax.axvline(0, color=TINTA2, lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels([f"{i}. {titulos[i]}" for i in g["ods"]], fontsize=8.5)
        ax.invert_yaxis()
        eixo_limpo(ax, grade="x")
        ax.set_xlabel("diferença na taxa por mil lemas (2016-2027 menos 2004-2015)", fontsize=8.5)
        titulo(ax, nome, "azul: diferença com p < 0,05 (permutação); cinza: não significativa")
    salvar(fig, "ods_antes_depois.png")


if __name__ == "__main__":
    main()
