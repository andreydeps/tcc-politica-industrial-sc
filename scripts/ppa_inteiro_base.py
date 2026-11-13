"""Base do PPA inteiro: todos os programas dos 6 PPAs com órgão e PÚBLICO-ALVO.

Entradas: PDFs em dados/ppa/ (texto em saidas/cache_texto/), regex do notebooks/TCC.ipynb,
          saidas/programas_todos.csv (texto lematizado de objetivo + justificativa).
Saída   : saidas/ppa_inteiro_programas.csv
          colunas: periodo, codigo, nome, orgao, objetivo, justificativa, publico_alvo,
                   selecionado, texto_lematizado

Público-alvo: até aqui o rótulo PÚBLICO-ALVO era só o marcador de fim da justificativa.
Agora o conteúdo do campo é lido do fim do regex até o primeiro destes marcadores
(regra por formato de PPA, conferida no texto de cada PDF em 13/11/2026):
  2004-2007: quebra de linha seguida de código de ação (4 dígitos) ou fim do bloco.
             Atenção: neste PDF o campo vem cortado pela largura da coluna
             (ex.: "Órgãos da Administração Direta, Autarquias e Funda"); não há como recuperar.
  2008-2011: linha "Indicador".
  2012-2027: linha "CUSTO DO PROGRAMA" ou o cabeçalho da tabela de indicadores
             ("REFERÊNCIA" em 2012-2015, "INDICADOR" em 2020-2027).
Em todos os casos o corte também para no início do programa seguinte.

2008-2011: desde 13/11/2026 o padrao_2008 do notebook é o mesmo regex do 2004-2007 e pega
os 65 programas do PDF (antes pegava 50). Ver docs/decisoes.md.
Os programas sem texto lematizado em programas_todos.csv são lematizados aqui, com a mesma regra.
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocos_programas import definicoes_do_notebook, texto_pdf  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
FIM_PUBLICO = {
    "2004-2007": re.compile(r"\n\s*\d{4}\s|Página:"),
    "2008-2011": re.compile(r"\n\s*Indicador\b|\n\s*\d{4}\s|Página:"),
}
FIM_PUBLICO_PADRAO = re.compile(r"\n\s*(?:CUSTO DO PROGRAMA|REFERÊNCIA|INDICADOR)\b|Página:")
CORTE_PUBLICO = re.compile(r"\s*p[úu]blico[\s-]*alvo\s*:", re.IGNORECASE)   # igual ao classificador.py


def limpa(s):
    return " ".join((s or "").split())


def main():
    ns = definicoes_do_notebook()
    regex = {"2004-2007": ns["padrao_2004"], "2008-2011": ns["padrao_2008"]}
    rodape = {"2004-2007": ns["rodape_2004"], "2008-2011": ns["rodape_2008"]}
    linhas = []
    for per, cam in ns["caminhos"].items():
        t = texto_pdf(cam)
        if per in rodape:
            t = rodape[per].sub(" ", t)
        ms = list(regex.get(per, ns["padrao"]).finditer(t))
        for k, m in enumerate(ms):
            d = m.groupdict()
            fim_bloco = ms[k + 1].start() if k + 1 < len(ms) else len(t)
            resto = t[m.end():fim_bloco]
            corte = FIM_PUBLICO.get(per, FIM_PUBLICO_PADRAO).search(resto)
            publico = limpa(resto[:corte.start()] if corte else resto[:300])
            nome = limpa(d["nome"] + " " + (d.get("nome2") or ""))
            orgao = limpa(d["orgao"] + " " + (d.get("orgao2") or ""))
            just = CORTE_PUBLICO.split(d["justificativa"], maxsplit=1)[0]
            linhas.append({"periodo": per, "codigo": d["codigo"], "nome": nome, "orgao": orgao,
                           "objetivo": limpa(d["objetivo"]), "justificativa": limpa(just),
                           "publico_alvo": publico})
    df = pd.DataFrame(linhas).drop_duplicates(["periodo", "codigo", "objetivo"])

    todos = pd.read_csv(SAIDAS / "programas_todos.csv", encoding="utf-8", dtype={"codigo": str})
    df = df.merge(todos[["periodo", "codigo", "objetivo", "selecionado", "texto_lematizado"]],
                  on=["periodo", "codigo", "objetivo"], how="left", validate="one_to_one")
    faltam = df["selecionado"].isna()
    print(f"{len(df)} programas | sem par em programas_todos.csv: {faltam.sum()} "
          f"({', '.join(df.loc[faltam, 'periodo'] + ':' + df.loc[faltam, 'codigo'])})")
    sel = ns["codigos_industria"]
    df["selecionado"] = [int(c in sel.get(p, [])) for p, c in zip(df["periodo"], df["codigo"])]
    if faltam.any():
        import spacy
        nlp = spacy.load("pt_core_news_lg", disable=["ner", "parser"])
        lema = lambda doc: " ".join(tk.lemma_.lower() for tk in doc if not tk.is_stop and not tk.is_punct
                                    and not tk.is_space and tk.is_alpha and tk.pos_ in {"NOUN", "VERB", "ADJ"})
        textos = (df.loc[faltam, "objetivo"] + " " + df.loc[faltam, "justificativa"]).tolist()
        df.loc[faltam, "texto_lematizado"] = [lema(d) for d in nlp.pipe(textos)]
    df["texto_lematizado"] = df["texto_lematizado"].fillna("")
    df.to_csv(SAIDAS / "ppa_inteiro_programas.csv", index=False, encoding="utf-8")
    vazio = df["publico_alvo"].eq("")
    print(df.assign(vazio=vazio).groupby("periodo").agg(programas=("codigo", "size"),
                                                         selecionados=("selecionado", "sum"),
                                                         publico_vazio=("vazio", "sum")))


if __name__ == "__main__":
    main()
