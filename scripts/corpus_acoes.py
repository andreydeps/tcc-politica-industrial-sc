"""Corpus complementar: nomes das ações e subações dos programas selecionados, lematizados.

Por quê: o texto de objetivo + justificativa é curto (cerca de 1.500 lemas no total), e isso
limita todos os testes. As ações e subações descrevem o que o programa faz de fato (crédito,
APL, incubadoras, capacitação) e multiplicam o texto disponível. Servem como checagem de
robustez: um resultado que aparece nos dois corpora é mais confiável.

Entrada : PDFs (cache de texto do blocos_programas.py) e definições do notebook
Saída   : saidas/corpus_acoes.csv (periodo, codigo, n_linhas, texto, texto_lematizado)

Limpeza: só linhas que começam com código de ação (4 dígitos, até 2008-2011) ou de subação
(6 dígitos); tira valores, unidades, sufixo regional "SDR - <cidade>" e siglas de órgão no fim;
linhas repetidas (a mesma subação replicada por região) contam uma vez por programa.
Lematização igual à do notebook: spaCy pt_core_news_lg, minúsculas, sem stopwords, só
substantivos, verbos e adjetivos.
"""
import re
import sys
from pathlib import Path

import pandas as pd
import spacy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocos_programas import definicoes_do_notebook, texto_pdf  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
LINHA_CODIGO = re.compile(r"^\s*(?:[AP]\s+)?(\d{4}|\d{6})\s+(\D.*)$")


def limpa(txt):
    txt = re.sub(r"\s-\s*SDR\s*-.*$", "", txt)                       # sufixo regional
    txt = re.sub(r"\s+(unidade|Unidade|%|km|Hectare|hectare)\b.*$", "", txt)   # unidade e valores
    txt = re.sub(r"[\d.,/]+", " ", txt)
    txt = re.sub(r"\s-\s*[A-ZÇÃÕÉÍÓÚ]{2,}(\s.*)?$", "", txt)          # sigla do órgão no fim ("- BADESC")
    return " ".join(txt.split())


def main():
    ns = definicoes_do_notebook()
    caminhos, codigos = ns["caminhos"], ns["codigos_industria"]
    regex = {"2004-2007": ns["padrao_2004"], "2008-2011": ns["padrao_2008"]}
    limpar = {"2004-2007": ns["rodape_2004"], "2008-2011": ns["rodape_2008"]}
    linhas = []
    for per, cam in caminhos.items():
        t = texto_pdf(cam)
        if per in limpar:
            t = limpar[per].sub(" ", t)
        ms = list(regex.get(per, ns["padrao"]).finditer(t))
        sel = set(codigos.get(per, []))
        por_prog = {}
        for k, m in enumerate(ms):
            if m["codigo"] not in sel:
                continue
            fim = ms[k + 1].start() if k + 1 < len(ms) else min(len(t), m.end() + 20000)
            for l in t[m.end():fim].splitlines():
                mm = LINHA_CODIGO.match(l)
                if not mm:
                    continue
                if per not in ("2004-2007", "2008-2011") and len(mm.group(1)) == 4:
                    continue                                   # de 2012 em diante, 4 dígitos = indicador
                txt = limpa(mm.group(2))
                if len(txt) >= 8:
                    por_prog.setdefault(m["codigo"], dict())[txt.lower()] = txt
        for cod, d in por_prog.items():
            linhas.append({"periodo": per, "codigo": cod, "n_linhas": len(d), "texto": ". ".join(d.values())})
        print(f"{per}: {len(por_prog)} programas, {sum(len(d) for d in por_prog.values())} ações/subações distintas", flush=True)

    df = pd.DataFrame(linhas)
    nlp = spacy.load("pt_core_news_lg", disable=["ner", "parser"])
    lema = lambda doc: " ".join(tk.lemma_.lower() for tk in doc if not tk.is_stop and not tk.is_punct
                                and not tk.is_space and tk.is_alpha and tk.pos_ in {"NOUN", "VERB", "ADJ"})
    # Nomes de ação vêm muitas vezes em Título ("Concessão de Linha de Crédito"); o spaCy marca essas
    # palavras como nome próprio (PROPN) e o filtro as descarta. Como são rótulos, não frases, vão em minúsculas.
    df["texto_lematizado"] = [lema(d) for d in nlp.pipe(df["texto"].str.lower(), batch_size=16)]
    df.to_csv(SAIDAS / "corpus_acoes.csv", index=False, encoding="utf-8")
    tot = df.assign(n=df["texto_lematizado"].str.split().str.len()).groupby("periodo")["n"].sum()
    print("\nLemas por período (ações):", tot.to_dict())
    print("Total de lemas:", int(tot.sum()))


if __name__ == "__main__":
    main()
