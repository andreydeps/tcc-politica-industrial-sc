"""Menções concretas a tipos de política (APL, cluster, crédito, incentivo fiscal, pequenos
produtores, educação tecnológica, instrumentos de inovação) nos programas selecionados.

Entrada : saidas/corpus_programas.csv (texto ORIGINAL de objetivo e justificativa)
Saída   : saidas/mencoes_politicas.csv (uma linha por menção, com trecho, período e programa)
          + resumos no terminal

Método: busca por expressões regulares sobre o texto sem acento (insensível a acento e
maiúscula), por frase. Para cada frase com menção, o spaCy identifica os VERBOS da frase,
que mostram COMO a política é promovida (apoiar, fomentar, financiar...). Como vários
programas repetem o texto entre períodos, cada menção é marcada como "repetida" quando a
mesma frase já apareceu em período anterior (herança textual, não reescrita).

Escopo: só os programas selecionados (codigos_industria). Não busca nos demais programas do PPA.
"""
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import spacy

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"

CATEGORIAS = {
    "APL / arranjo produtivo": r"\bapls?\b|arranjos? produtivos?",
    "cluster / polo": r"\bclusters?\b|\bpolos?\b|aglomerad",
    "crédito / financiamento": r"credito|financiament|emprestimo",
    # "tributári" foi retirado em 10/11/2026: pegava "Combate à Sonegação de Tributos / Receita Tributária"
    "incentivo fiscal": r"incentivos? fiscai|beneficios? fiscai|isencao|isencoes|renuncia fiscal|\bicms\b",
    "pequeno produtor rural": r"pequenos? produtores?|agricultura familiar|agricultores? familiares?|agroindustrias? familiares?|produtores? rurais?|agricultores?|pescadores?",
    "educação tecnológica / qualificação": r"educacao tecnologica|ensino tecnico|escolas? tecnicas?|educacao profissional|formacao tecnica|qualificacao profissional|capacitacao|qualificacao",
    "instrumento de inovação": r"incubadoras?|parques? tecnologic|centros? de inovacao|condominios? empresariais?|empresas? de base tecnologica",
}


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def frases(texto):
    return [" ".join(f.split()) for f in re.split(r"(?<=[.;!?])\s+", str(texto)) if f.strip()]


def main():
    df = pd.read_csv(SAIDAS / "corpus_programas.csv", encoding="utf-8", dtype={"codigo": str})
    df["nome"] = df["nome"].str.split().str.join(" ")
    nlp = spacy.load("pt_core_news_lg", disable=["ner"])
    periodos = sorted(df["periodo"].unique())
    vistas = {}                               # frase normalizada -> primeiro período em que apareceu
    linhas = []
    for per in periodos:
        for _, r in df[df.periodo == per].iterrows():
            for campo in ("objetivo", "justificativa"):
                for fr in frases(r[campo]):
                    fn = sem_acento(fr)
                    achou = [(cat, m.group(0)) for cat, pat in CATEGORIAS.items() for m in [re.search(pat, fn)] if m]
                    if not achou:
                        vistas.setdefault(fn, per)
                        continue
                    origem = vistas.get(fn)
                    repetida = origem if (origem and origem != per) else ""
                    vistas.setdefault(fn, per)
                    verbos = sorted({t.lemma_.lower() for t in nlp(fr) if t.pos_ == "VERB" and not t.is_stop})
                    for cat, termo in achou:
                        linhas.append({"categoria": cat, "termo": termo, "periodo": per, "codigo": r["codigo"],
                                       "programa": r["nome"], "campo": campo, "trecho": fr,
                                       "repetida_de": repetida, "verbos": ", ".join(verbos)})
    m = pd.DataFrame(linhas)
    m.to_csv(SAIDAS / "mencoes_politicas.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    print(f"Menções (frase x categoria): {len(m)} | frases distintas: {m['trecho'].nunique()}")

    print("\n=== Programas distintos que mencionam, por categoria e período (todas as menções) ===")
    t1 = m.groupby(["categoria", "periodo"])["codigo"].nunique().unstack(fill_value=0).reindex(columns=periodos, fill_value=0)
    print(t1.to_string())
    print("\n=== Só menções NOVAS (frase não vista em período anterior) ===")
    novas = m[m["repetida_de"] == ""]
    t2 = novas.groupby(["categoria", "periodo"])["trecho"].nunique().unstack(fill_value=0).reindex(columns=periodos, fill_value=0)
    print(t2.to_string())

    print("\n=== COMO são promovidos: verbos mais frequentes nas frases de cada categoria ===")
    for cat in CATEGORIAS:
        c = Counter(v for vs in m[m.categoria == cat].drop_duplicates("trecho")["verbos"] for v in vs.split(", ") if v)
        print(f"  {cat}: {', '.join(f'{v}({n})' for v, n in c.most_common(8))}")

    print("\n=== Exemplos (frases distintas, mais antiga e mais recente por categoria) ===")
    for cat in CATEGORIAS:
        sub = m[m.categoria == cat].drop_duplicates("trecho").sort_values("periodo")
        if sub.empty:
            print(f"\n[{cat}] nenhuma menção"); continue
        for _, r in pd.concat([sub.head(1), sub.tail(1)]).drop_duplicates("trecho").iterrows():
            print(f"\n[{cat}] {r['periodo']} / {r['codigo']} {r['programa'][:40]} ({r['campo']}):\n   {r['trecho'][:300]}")


if __name__ == "__main__":
    main()
