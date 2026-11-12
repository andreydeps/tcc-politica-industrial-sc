"""Candidatos a termos do léxico por similaridade semântica (embeddings do spaCy).

Entrada : saidas/corpus_programas.csv (gerado pelo notebook)
Saída   : saidas/embeddings_rodada<N>_candidatos.csv + resumo no terminal

Uso:
    python scripts/embeddings_candidatos.py --rodada 1 --sementes inovação competitividade digital internacional emprego

Diferença para o snowball.py (coocorrência):
- coocorrência pergunta "quem aparece PERTO da semente nos textos?" (depende do volume de texto);
- embeddings perguntam "quem tem SIGNIFICADO parecido com a semente?", usando vetores
  que o modelo pt_core_news_lg aprendeu em um corpus enorme, de fora do seu. Por isso
  funciona mesmo com corpus pequeno e mesmo com semente rara (ex.: "digital").
O candidato continua vindo do SEU corpus (só testamos palavras que aparecem nos PPAs
selecionados). Quem decide o que entra no léxico é o pesquisador.
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import spacy

RAIZ = Path(__file__).resolve().parent.parent
ARQ_CORPUS = RAIZ / "saidas" / "corpus_programas.csv"


def carrega_vocabulario(min_freq):
    """Termos do corpus (já lematizados) com frequência, nº de textos e períodos."""
    df = pd.read_csv(ARQ_CORPUS, encoding="utf-8", dtype={"codigo": str})
    df = df.drop_duplicates(subset="texto_lematizado", keep="first")   # tira texto copiado idêntico
    freq = Counter()
    textos = defaultdict(set)
    periodos = defaultdict(set)
    for i, (txt, per) in enumerate(zip(df["texto_lematizado"].fillna(""), df["periodo"])):
        for t in txt.split():
            freq[t] += 1
            textos[t].add(i)
            periodos[t].add(per)
    vocab = [t for t, f in freq.items() if f >= min_freq]
    return vocab, freq, textos, periodos, len(df)


def unitario(m):
    n = np.linalg.norm(m, axis=-1, keepdims=True)
    n[n == 0] = 1
    return m / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodada", type=int, default=1)
    ap.add_argument("--sementes", nargs="+", required=True)
    ap.add_argument("--min-freq", type=int, default=2, help="frequência mínima do candidato no corpus")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--sem-centrar", action="store_true",
                    help="desliga a centralização dos vetores (veja explicação no código)")
    a = ap.parse_args()

    nlp = spacy.load("pt_core_news_lg", disable=["tagger", "parser", "ner", "lemmatizer", "attribute_ruler"])
    vocab, freq, textos, periodos, n_textos = carrega_vocabulario(a.min_freq)
    sementes = list(dict.fromkeys(a.sementes))

    # Só palavras que o modelo conhece (têm vetor).
    com_vetor = [t for t in vocab if nlp.vocab[t].has_vector]
    sem_vetor = len(vocab) - len(com_vetor)
    print(f"Textos distintos: {n_textos} | vocabulário (freq>={a.min_freq}): {len(vocab)} "
          f"| com vetor: {len(com_vetor)} (sem vetor: {sem_vetor})")
    faltando = [s for s in sementes if not nlp.vocab[s].has_vector]
    if faltando:
        print("AVISO: sementes sem vetor no modelo:", faltando)
        sementes = [s for s in sementes if s not in faltando]

    M = np.array([nlp.vocab[t].vector for t in com_vetor])
    S = np.array([nlp.vocab[s].vector for s in sementes])

    # Centralização: vetores de palavras tendem a apontar todos para uma direção comum
    # ("palavra de texto em português"), o que faz tudo parecer um pouco parecido com tudo.
    # Subtrair o vetor médio do vocabulário remove essa direção comum e deixa a
    # similaridade refletir mais o significado específico.
    if not a.sem_centrar:
        media = M.mean(axis=0)
        M, S = M - media, S - media

    Mn, Sn = unitario(M), unitario(S)
    sim = Mn @ Sn.T                                     # (termos x sementes), cosseno
    centroide = unitario(Sn.mean(axis=0, keepdims=True))[0]
    sim_centroide = Mn @ centroide                      # similaridade com o "conjunto" das sementes

    idx = {t: i for i, t in enumerate(com_vetor)}
    linhas = []
    for j, s in enumerate(sementes):
        for i, t in enumerate(com_vetor):
            if t in sementes:
                continue
            linhas.append({"semente": s, "candidato": t, "cosseno": round(float(sim[i, j]), 3),
                           "freq_no_corpus": freq[t], "textos": len(textos[t]),
                           "periodos": len(periodos[t])})
    por_semente = pd.DataFrame(linhas)

    geral = pd.DataFrame({
        "candidato": [t for t in com_vetor if t not in sementes],
        "cosseno_centroide": [round(float(sim_centroide[idx[t]]), 3) for t in com_vetor if t not in sementes],
        "cosseno_max": [round(float(sim[idx[t]].max()), 3) for t in com_vetor if t not in sementes],
        "semente_mais_proxima": [sementes[int(sim[idx[t]].argmax())] for t in com_vetor if t not in sementes],
        "freq_no_corpus": [freq[t] for t in com_vetor if t not in sementes],
        "textos": [len(textos[t]) for t in com_vetor if t not in sementes],
        "periodos": [", ".join(sorted(periodos[t])) for t in com_vetor if t not in sementes],
    }).sort_values("cosseno_centroide", ascending=False)

    por_semente.sort_values(["semente", "cosseno"], ascending=[True, False]).to_csv(
        RAIZ / "saidas" / f"embeddings_rodada{a.rodada}_por_semente.csv", index=False, encoding="utf-8")
    saida = RAIZ / "saidas" / f"embeddings_rodada{a.rodada}_candidatos.csv"
    geral.to_csv(saida, index=False, encoding="utf-8")

    print(f"\n=== Mais próximos de cada semente (top {a.top}) ===")
    for s in sementes:
        sub = por_semente[por_semente["semente"] == s].sort_values("cosseno", ascending=False).head(a.top)
        print(f"\n[{s}]  (freq da semente no corpus: {freq[s]})")
        for _, r in sub.iterrows():
            print(f"  {r['candidato']:<18} cos={r['cosseno']:<6} freq={r['freq_no_corpus']:<3} "
                  f"textos={r['textos']:<2} periodos={r['periodos']}")

    print(f"\n=== Mais próximos do CONJUNTO das sementes (centroide), top 30 ===")
    print(geral.head(30).drop(columns=["periodos"]).to_string(index=False))
    print(f"\nSalvo em {saida}")


if __name__ == "__main__":
    main()
