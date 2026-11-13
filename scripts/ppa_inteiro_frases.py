"""Frases de objetivo + justificativa de todos os programas, lematizadas.

Entrada: saidas/ppa_inteiro_programas.csv
Saída  : saidas/ppa_inteiro_frases.csv
         colunas: periodo, codigo, selecionado, campo, n_frase, frase, frase_lematizada

Divisão em frases: ponto, ponto e vírgula, interrogação ou exclamação seguidos de espaço
(regra simples; o spaCy sem parser não separa frases). Lematização igual à de
programas_todos.csv (classificador.py): spaCy pt_core_news_lg, só substantivos, verbos e
adjetivos, sem stopwords. Usada na coocorrência (item 8), nas frases de competitividade e
inovação (item 2) e na medida de texto copiado entre PPAs (item 5).
"""
import re
from pathlib import Path

import pandas as pd
import spacy

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
DIVIDE = re.compile(r"(?<=[.;!?])\s+")


def main():
    d = pd.read_csv(SAIDAS / "ppa_inteiro_programas.csv", encoding="utf-8", dtype={"codigo": str})
    linhas = []
    for _, r in d.iterrows():
        for campo in ("objetivo", "justificativa"):
            for k, f in enumerate(s for s in DIVIDE.split(str(r[campo]) if pd.notna(r[campo]) else "") if s.strip()):
                linhas.append({"periodo": r.periodo, "codigo": r.codigo, "selecionado": r.selecionado,
                               "campo": campo, "n_frase": k, "frase": f.strip()})
    f = pd.DataFrame(linhas)
    nlp = spacy.load("pt_core_news_lg", disable=["ner", "parser"])
    lema = lambda doc: " ".join(tk.lemma_.lower() for tk in doc if not tk.is_stop and not tk.is_punct
                                and not tk.is_space and tk.is_alpha and tk.pos_ in {"NOUN", "VERB", "ADJ"})
    f["frase_lematizada"] = [lema(doc) for doc in nlp.pipe(f["frase"].tolist(), batch_size=64)]
    f.to_csv(SAIDAS / "ppa_inteiro_frases.csv", index=False, encoding="utf-8")
    print(f"{len(f)} frases | lemas: {f.frase_lematizada.str.split().str.len().sum()}")
    print(f.groupby("periodo").size().to_string())


if __name__ == "__main__":
    main()
