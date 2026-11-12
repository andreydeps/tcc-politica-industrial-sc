"""Menções a instrumentos de política no BLOCO COMPLETO de cada programa selecionado
(público-alvo, ações, subações, produtos), e não só em objetivo e justificativa.

Entradas: PDFs em dados/ppa/ e os regex/listas definidos no notebook (lidos do próprio
          notebooks/TCC.ipynb, para não duplicar código).
Saídas  : saidas/mencoes_blocos.csv (uma linha por linha do PDF com menção)
          saidas/cache_texto/<arquivo>.txt (texto do pdfplumber, para não reextrair)

Como funciona: o regex de cada período acha o início de cada programa. O "resto do bloco"
vai do fim do regex (rótulo de público-alvo) até o início do programa seguinte. Nesse
trecho estão o público-alvo, as ações e as subações, onde instrumentos concretos (crédito,
APL, incentivo) costumam aparecer. A busca é por linha, sem acento, com as mesmas
categorias do scripts/mencoes.py. Linhas repetidas por região (subações "SDR - <cidade>")
são agrupadas numa só linha normalizada.
"""
import re
import sys
import unicodedata
from pathlib import Path

import nbformat
import pandas as pd
import pdfplumber

RAIZ = Path(__file__).resolve().parent.parent
SAIDAS = RAIZ / "saidas"
CACHE = SAIDAS / "cache_texto"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mencoes import CATEGORIAS, sem_acento  # noqa: E402


def definicoes_do_notebook():
    """Executa só as células que definem caminhos, listas e regex."""
    nb = nbformat.read(RAIZ / "notebooks" / "TCC.ipynb", as_version=4)
    ns = {"__file__": str(RAIZ / "notebooks" / "TCC.ipynb")}
    import os
    cwd = os.getcwd()
    os.chdir(RAIZ / "notebooks")
    try:
        for c in nb.cells:
            if c.cell_type != "code":
                continue
            s = c.source
            if ("DIR_SAIDAS.mkdir" in s or "caminhos = {" in s or "codigos_industria = {" in s
                    or "padrao = re.compile(" in s):
                exec(s.replace("import spacy\n", "").replace("from wordcloud import WordCloud\n", ""), ns)
    finally:
        os.chdir(cwd)
    return ns


def texto_pdf(caminho):
    CACHE.mkdir(exist_ok=True)
    arq = CACHE / (Path(caminho).stem + ".txt")
    if arq.exists():
        return arq.read_text(encoding="utf-8")
    with pdfplumber.open(caminho) as pdf:
        t = "".join((p.extract_text() or "") for p in pdf.pages)    # mesmo procedimento do notebook
    arq.write_text(t, encoding="utf-8")
    return t


def normaliza_linha(l):
    """Tira códigos numéricos, valores e o sufixo regional, para agrupar subações repetidas."""
    l = sem_acento(l)
    l = re.sub(r"\s-\s*sdr\s*-.*$", "", l)
    l = re.sub(r"[\d.,/]+", " ", l)
    l = re.sub(r"^\s*[ap]\s+", "", l)
    return " ".join(l.split())


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
        n_blocos = 0
        for k, m in enumerate(ms):
            if m["codigo"] not in sel:
                continue
            fim = ms[k + 1].start() if k + 1 < len(ms) else min(len(t), m.end() + 20000)
            resto = t[m.end():fim]
            n_blocos += 1
            nome = " ".join(m["nome"].split())
            for l in resto.splitlines():
                ln = sem_acento(l)
                for cat, pat in CATEGORIAS.items():
                    mm = re.search(pat, ln)
                    if mm:
                        linhas.append({"categoria": cat, "termo": mm.group(0), "periodo": per, "codigo": m["codigo"],
                                       "programa": nome, "linha": " ".join(l.split()), "linha_norm": normaliza_linha(l)})
        print(f"{per}: {len(ms)} programas no PDF | blocos selecionados lidos: {n_blocos}", flush=True)

    d = pd.DataFrame(linhas)
    d.to_csv(SAIDAS / "mencoes_blocos.csv", index=False, encoding="utf-8")
    periodos = list(caminhos)
    pd.set_option("display.width", 220)
    print(f"\nLinhas com menção: {len(d)} | linhas distintas (normalizadas): {d['linha_norm'].nunique() if len(d) else 0}")
    if d.empty:
        return
    print("\n=== Programas selecionados com menção no bloco (ações, subações, público-alvo), por período ===")
    print(d.groupby(["categoria", "periodo"])["codigo"].nunique().unstack(fill_value=0)
          .reindex(columns=periodos, fill_value=0).to_string())
    print("\n=== Linhas distintas por categoria (até 6 exemplos, com período e programa) ===")
    for cat in CATEGORIAS:
        sub = d[d.categoria == cat].drop_duplicates(["linha_norm", "codigo"])
        if sub.empty:
            print(f"\n[{cat}] nenhuma menção")
            continue
        print(f"\n[{cat}] {sub['linha_norm'].nunique()} linhas distintas")
        for _, r in sub.sort_values("periodo").head(6).iterrows():
            print(f"   {r['periodo']} / {r['codigo']}: {r['linha'][:150]}")


if __name__ == "__main__":
    main()
