"""Clusterização de termos (campos semânticos) antes do topic modeling, com teste de estabilidade.

Entrada : saidas/corpus_programas.csv
Saída   : saidas/clusters_termos.csv (termo, cluster, frequência)
          saidas/clusters_por_periodo.csv (participação de cada campo semântico por período)
          resumos no terminal

Ideia: em vez de dar ao LDA ~200 palavras soltas (muitas raras, com 41 documentos), agrupamos
as palavras em CAMPOS SEMÂNTICOS usando os vetores do spaCy (palavras de sentido parecido
caem no mesmo cluster) e passamos a contar CAMPOS por programa. Isso reduz a dimensão, junta
sinônimos e variantes (competitivo/competitividade) e tende a dar tópicos mais estáveis.

Estabilidade (o que importa para poder usar o resultado):
- clusters: ARI (índice de Rand ajustado) entre execuções do KMeans com sementes diferentes.
  1,00 = agrupamentos idênticos; ~0 = sem relação.
- LDA: para cada semente, casa os tópicos com os da semente 42 (algoritmo húngaro) e mede o
  cosseno médio entre os pares casados. 1,00 = tópicos idênticos.
  Compara LDA sobre PALAVRAS (como no notebook) com LDA sobre CAMPOS (clusters).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import adjusted_rand_score, silhouette_score

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"


def unitario(m):
    n = np.linalg.norm(m, axis=-1, keepdims=True)
    n[n == 0] = 1
    return m / n


def estabilidade_lda(X, n_top, sementes=range(1, 11)):
    """Cosseno médio dos tópicos casados (húngaro) entre a semente 42 e as demais."""
    def comps(seed):
        c = LatentDirichletAllocation(n_components=n_top, random_state=seed, max_iter=50).fit(X).components_
        return unitario(c / c.sum(axis=1, keepdims=True))
    ref = comps(42)
    out = []
    for sd in sementes:
        o = comps(sd)
        sim = ref @ o.T
        i, j = linear_sum_assignment(-sim)
        out.append(sim[i, j].mean())
    return np.mean(out), np.min(out), np.max(out)


def main():
    df = pd.read_csv(SAIDAS / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str})
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    periodos = sorted(df["periodo"].unique())
    nlp = spacy.load("pt_core_news_lg", disable=["tagger", "parser", "ner", "lemmatizer", "attribute_ruler"])

    # vocabulário: lemas com frequência >= 2 e vetor
    cv = CountVectorizer(token_pattern=r"\S+", lowercase=False)
    Xp = cv.fit_transform(df["texto_lematizado"]).toarray()
    vocab = np.array(cv.get_feature_names_out())
    freq = Xp.sum(axis=0)
    tem = np.array([nlp.vocab[t].has_vector for t in vocab])
    keep = (freq >= 2) & tem
    termos, ftermos = vocab[keep], freq[keep]
    W = np.array([nlp.vocab[t].vector for t in termos])
    W = unitario(W - W.mean(axis=0))                        # centraliza e normaliza
    print(f"Programas: {len(df)} | termos agrupados (freq>=2, com vetor): {len(termos)}")

    # escolha de k por silhueta (cosseno); em corpus pequeno, a silhueta é baixa em geral
    print("\nSilhueta por k (maior = grupos mais separados):")
    sil = {}
    for k in range(6, 25, 2):
        lab = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(W)
        sil[k] = silhouette_score(W, lab, metric="cosine")
    print("  " + " | ".join(f"k={k}: {v:.3f}" for k, v in sil.items()))
    k = 12            # fixo: interpretabilidade (campos legíveis); ver estabilidade abaixo
    print(f"  k escolhido = {k} (fixado por interpretabilidade; melhor silhueta = k={max(sil, key=sil.get)})")

    labs = [KMeans(n_clusters=k, n_init=10, random_state=s).fit_predict(W) for s in range(10)]
    aris = [adjusted_rand_score(labs[0], l) for l in labs[1:]]
    print(f"Estabilidade dos clusters (ARI entre 10 sementes): média {np.mean(aris):.2f} (mín {np.min(aris):.2f})")
    lab = labs[0]

    # conteúdo dos clusters
    cl = pd.DataFrame({"termo": termos, "cluster": lab, "freq": ftermos}).sort_values(["cluster", "freq"], ascending=[True, False])
    cl.to_csv(SAIDAS / "clusters_termos.csv", index=False, encoding="utf-8")
    print("\n=== Campos semânticos (termos mais frequentes de cada cluster) ===")
    for c in range(k):
        sub = cl[cl.cluster == c]
        print(f"  C{c:02d} ({len(sub):>2} termos, {int(sub.freq.sum()):>3} ocorr.): " + ", ".join(sub.termo.head(9)))

    # programa x cluster
    idx = {t: i for i, t in enumerate(vocab)}
    colunas = [[idx[t] for t in termos[lab == c]] for c in range(k)]
    Xc = np.column_stack([Xp[:, cols].sum(axis=1) for cols in colunas])        # programa x cluster
    pidx = df["periodo"].map({p: i for i, p in enumerate(periodos)}).to_numpy()
    por = pd.DataFrame(np.vstack([Xc[pidx == i].sum(axis=0) / Xc[pidx == i].sum() * 100 for i in range(len(periodos))]),
                       index=periodos, columns=[f"C{c:02d}" for c in range(k)])
    por.round(1).to_csv(SAIDAS / "clusters_por_periodo.csv", encoding="utf-8")
    print("\n=== Participação de cada campo no período (% das ocorrências agrupadas) ===")
    pd.set_option("display.width", 220)
    print(por.round(1).T.to_string())

    # estabilidade do LDA: palavras vs campos
    print("\n=== Estabilidade do LDA entre sementes (cosseno médio dos tópicos casados; 1,00 = idênticos) ===")
    Xw = CountVectorizer(max_features=200).fit_transform(df["texto_lematizado"])      # igual ao notebook
    print(f"{'tópicos':<9}{'LDA em palavras (200)':>26}{'LDA em campos (' + str(k) + ')':>22}")
    for n_top in (3, 4, 5):
        a = estabilidade_lda(Xw, n_top)
        b = estabilidade_lda(Xc, n_top)
        print(f"{n_top:<9}{a[0]:>14.2f} (mín {a[1]:.2f}){b[0]:>14.2f} (mín {b[1]:.2f})")

    # Conteúdo dos tópicos do LDA sobre campos (4 tópicos, semente 42) e estabilidade de CADA tópico
    n_top = 4
    lda = LatentDirichletAllocation(n_components=n_top, random_state=42, max_iter=50).fit(Xc)
    comp = lda.components_ / lda.components_.sum(axis=1, keepdims=True)
    ref = unitario(comp)
    por_topico = np.zeros((10, n_top))
    for k_sd, sd in enumerate(range(1, 11)):
        o = LatentDirichletAllocation(n_components=n_top, random_state=sd, max_iter=50).fit(Xc).components_
        o = unitario(o / o.sum(axis=1, keepdims=True))
        sim = ref @ o.T
        i, j = linear_sum_assignment(-sim)
        por_topico[k_sd, i] = sim[i, j]
    resumo_campo = {c: ", ".join(cl[cl.cluster == c].termo.head(5)) for c in range(k)}
    print(f"\n=== Tópicos do LDA sobre campos ({n_top} tópicos, semente 42) ===")
    for t_ in range(n_top):
        top = np.argsort(comp[t_])[::-1][:3]
        print(f"  T{t_} (estabilidade: cosseno mín {por_topico[:, t_].min():.2f}, médio {por_topico[:, t_].mean():.2f})")
        for c in top:
            print(f"      {comp[t_, c]*100:4.0f}%  C{c:02d}: {resumo_campo[c]}")
    theta = lda.transform(Xc)
    medias = pd.DataFrame(theta, columns=[f"T{t_}" for t_ in range(n_top)]).groupby(df["periodo"]).mean().reindex(periodos)
    medias.round(3).to_csv(SAIDAS / "lda_campos_por_periodo.csv", encoding="utf-8")
    print("\nParticipação média de cada tópico nos programas do período:")
    print(medias.round(2).to_string())


if __name__ == "__main__":
    main()
