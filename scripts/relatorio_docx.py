"""Gera o relatório de andamento em .docx (ABNT simplificada, Arial 12, espaço 1,5).

Saída: saidas/relatorio_andamento_2026-11-12.docx
Os números das tabelas são lidos dos arquivos de resultado em saidas/.
"""
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

RAIZ = Path(__file__).resolve().parent.parent
S = RAIZ / "saidas"
SAIDA = S / "relatorio_andamento_2026-11-12.docx"


def num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


# ------------------------------------------------------------------ dados
corpus = pd.read_csv(S / "corpus_programas.csv", encoding="utf-8")
corpus["n"] = corpus["texto_lematizado"].fillna("").str.split().str.len()
por_per = corpus.groupby("periodo").agg(sel=("codigo", "size"), lemas=("n", "sum"))
blocos = {"2004-2007": 118, "2008-2011": 50, "2012-2015": 115, "2016-2019": 107, "2020-2023": 108, "2024-2027": 104}
lex = pd.read_csv(S / "lexico_validado.csv", encoding="utf-8")
lex = lex[lex.decisao.isin(["entra", "variante"])]
val = pd.read_csv(S / "valores_instrumentos.csv", encoding="utf-8").set_index("periodo")

# ------------------------------------------------------------------ documento e estilos
doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
sec.top_margin, sec.left_margin, sec.bottom_margin, sec.right_margin = Cm(3), Cm(3), Cm(2), Cm(2)

st = doc.styles["Normal"]
st.font.name, st.font.size = "Arial", Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(0)
for nome, tam in (("Heading 1", 12), ("Heading 2", 12)):
    h = doc.styles[nome]
    h.font.name, h.font.size, h.font.bold = "Arial", Pt(tam), True
    h.font.color.rgb = None
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    h.element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    h.element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        h.element.rPr.rFonts.attrib.pop(qn(att), None)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.line_spacing = 1.5
doc.styles["Heading 1"].font.all_caps = True
for nome in ("Heading 1", "Heading 2"):    # tira a cor azul do tema
    rpr = doc.styles[nome].element.rPr
    for c in rpr.findall(qn("w:color")):
        rpr.remove(c)


def numero_pagina(section):
    p = section.header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = texto
        run._r.append(el)
    run.font.size = Pt(10)


def par(texto, recuo=True, alin=WD_ALIGN_PARAGRAPH.JUSTIFY, negrito=False, tam=None, depois=0):
    p = doc.add_paragraph()
    p.alignment = alin
    if recuo:
        p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_after = Pt(depois)
    r = p.add_run(texto)
    r.bold = negrito
    if tam:
        r.font.size = Pt(tam)
    return p


def legenda(texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(texto)
    r.font.size = Pt(10)


def fonte(texto="Fonte: elaboração própria a partir dos PPAs de Santa Catarina (2004-2027)."):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run(texto)
    r.font.size = Pt(10)


def figura(arquivo, titulo_fig, largura=16):
    legenda(titulo_fig)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(str(S / arquivo), width=Cm(largura))
    fonte()


def tabela(cabecalho, linhas, larguras, titulo_tab):
    legenda(titulo_tab)
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for i, txt in enumerate(cabecalho):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(txt)
        r.bold, r.font.size = True, Pt(10)
    for linha in linhas:
        cells = t.add_row().cells
        for i, txt in enumerate(linha):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(txt))
            r.font.size = Pt(10)
    for row in t.rows:
        for i, w in enumerate(larguras):
            row.cells[i].width = Cm(w)
            for p in row.cells[i].paragraphs:
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.first_line_indent = Cm(0)
    fonte()


numero_pagina(sec)

# ------------------------------------------------------------------ identificação
for linha in ("UNIVERSIDADE FEDERAL DE SANTA CATARINA", "CURSO DE CIÊNCIAS ECONÔMICAS"):
    par(linha, recuo=False, alin=WD_ALIGN_PARAGRAPH.CENTER, negrito=True)
par("", recuo=False)
par("ANDREY DE PAULA E SILVA", recuo=False, alin=WD_ALIGN_PARAGRAPH.CENTER)
par("", recuo=False)
par("COMPLEXIDADE ECONÔMICA E POLÍTICA INDUSTRIAL NAS MICRORREGIÕES DE SANTA CATARINA",
    recuo=False, alin=WD_ALIGN_PARAGRAPH.CENTER, negrito=True)
par("Relatório de andamento: análise textual dos Planos Plurianuais de Santa Catarina (2004-2027)",
    recuo=False, alin=WD_ALIGN_PARAGRAPH.CENTER)
par("", recuo=False)
par("Orientador: Prof. Dominik Hartmann", recuo=False, alin=WD_ALIGN_PARAGRAPH.CENTER)
par("Coorientador: Lukas Pezzini", recuo=False, alin=WD_ALIGN_PARAGRAPH.CENTER)
par("Florianópolis, 12 de novembro de 2026", recuo=False, alin=WD_ALIGN_PARAGRAPH.CENTER, depois=12)

# ------------------------------------------------------------------ 1
doc.add_heading("1 Introdução", level=1)
par("Este relatório resume o andamento da etapa de análise textual do trabalho desde a reunião de 30 de setembro "
    "de 2026. A pergunta desta etapa é como o discurso de política industrial do governo de Santa Catarina mudou "
    "entre os Planos Plurianuais (PPAs) de 2004-2007 e de 2024-2027. O texto apresenta os dados e o método, os "
    "principais resultados, os testes de robustez, as limitações e os pontos que dependem de decisão dos orientadores.")
par("O resultado central é que a única mudança de discurso que resiste a todos os testes é o crescimento da "
    "linguagem de competitividade, concentrado em 2024-2027. Os demais movimentos observados dependem de poucos "
    "programas ou da composição da lista de programas analisados.")

# ------------------------------------------------------------------ 2
doc.add_heading("2 Dados e método", level=1)
doc.add_heading("2.1 Corpus e seleção dos programas", level=2)
par("Os dados são os Anexos Únicos dos seis PPAs de Santa Catarina entre 2004-2007 e 2024-2027. A extração, feita "
    "por expressões regulares ajustadas ao formato de cada ciclo, recuperou todos os programas de cada anexo. A seleção "
    "dos programas de política industrial é manual e segue a definição de ação de governo voltada a alterar a "
    "estrutura setorial da produção ou a elevar a competitividade e a capacidade tecnológica de atividades "
    "específicas (CHANG, 1994; RODRIK, 2004, 2008). O texto analisado de cada programa é a concatenação de objetivo "
    "e justificativa, lematizada com o modelo pt_core_news_lg da biblioteca spaCy, mantidos apenas substantivos, "
    "verbos e adjetivos (Tabela 1).")
linhas = [[p, blocos[p], int(por_per.loc[p, "sel"]), f"{int(por_per.loc[p, 'lemas']):,}".replace(",", ".")]
          for p in por_per.index]
linhas.append(["Total", sum(blocos.values()), int(por_per.sel.sum()), f"{int(por_per.lemas.sum()):,}".replace(",", ".")])
tabela(["PPA", "Programas no anexo", "Programas selecionados", "Lemas analisados"], linhas, [3.5, 4, 4.5, 4],
       "Tabela 1 – Programas extraídos e selecionados por PPA")
par("O PPA 2004-2007 usa uma numeração de códigos parcialmente diferente da dos ciclos seguintes. A continuidade "
    "dos programas entre ciclos foi estabelecida por uma tabela de equivalência proposta, ainda a validar.")

doc.add_heading("2.2 Léxico", level=2)
par("O léxico partiu de cinco termos escolhidos por interesse teórico (inovação, competitividade, internacional, "
    "emprego e digital) e foi expandido a partir dos próprios dados, por similaridade entre vetores de palavras do "
    "spaCy e por coocorrência (informação mútua pontual). Dos 38 termos avaliados, 20 foram aceitos e organizados em "
    "cinco dimensões (Quadro 1); termos genéricos, ambíguos ou de outras agendas ficaram de fora.")
ordem = ["competitividade e produção", "inovação e tecnologia", "inserção internacional", "trabalho e renda", "digital"]
linhas = [[d.capitalize(), ", ".join(lex[lex.dimensao == d].termo)] for d in ordem]
tabela(["Dimensão", "Termos"], linhas, [5, 11], "Quadro 1 – Léxico validado")

doc.add_heading("2.3 Testes de robustez", level=2)
par("Para responder à crítica de circularidade, isto é, de que a escolha prévia das palavras produza o resultado, "
    "cada termo e cada dimensão foram comparados com três referências: a trajetória obtida quando os programas são "
    "sorteados entre os períodos (teste de permutação), a de 25 termos de frequência semelhante e a de 1.000 léxicos "
    "aleatórios do mesmo tamanho. Os intervalos de confiança foram obtidos por reamostragem de programas dentro de cada "
    "período. A seleção manual foi conferida com um classificador de texto inspirado em Juhász et al. (2025).")

# ------------------------------------------------------------------ 3
doc.add_heading("3 Resultados", level=1)
doc.add_heading("3.1 Competitividade é a única mudança robusta", level=2)
par("A dimensão competitividade e produção é a única cuja trajetória supera o acaso (p = 0,004 no teste de "
    "permutação) e 99,7% dos léxicos aleatórios de mesma frequência. A taxa passa de zero em 2004-2007 para 14 a 22 "
    "ocorrências por mil lemas entre 2008 e 2023 e chega a 44 por mil em 2024-2027 (Figura 1). As demais dimensões não "
    "se distinguem do acaso: o pico de inserção internacional em 2020-2023 decorre da reescrita de um único programa "
    "(0212), e a queda de digital acompanha o fim do programa de inclusão digital.")
figura("indice_lexico_programas.png", "Figura 1 – Dimensões do léxico por PPA, com intervalo de confiança e faixa de "
       "léxicos aleatórios")
par("A leitura das 28 frases que usam esses termos mostra uma mudança de sentido. Em 2008-2011, competitividade é a "
    "meta de um programa econômico (fomentar a produção e diversificar o padrão tecnológico). Entre 2012 e 2019, "
    "refere-se a cadeias específicas, como o agronegócio e as micro e pequenas empresas. Em 2020-2023, passa a ser a "
    "competitividade das empresas catarinenses. Em 2024-2027, aparece em seis programas, inclusive de ciência e "
    "tecnologia e de qualificação de trabalhadores, e surge pela primeira vez a referência a setores estratégicos da "
    "indústria, do comércio e dos serviços.")

doc.add_heading("3.2 Composição e reescrita", level=2)
par("A mudança de vocabulário entre ciclos alterna entre entrada e saída de programas e reescrita do texto dos "
    "programas que continuam. Entre 2008-2011 e 2012-2015 predomina a entrada de programas; entre 2016-2019 e "
    "2020-2023, apenas a reescrita; entre 2020-2023 e 2024-2027, as duas. Sete de 31 pares de ciclos consecutivos de "
    "um mesmo programa têm texto idêntico, o que indica herança textual relevante entre os planos.")

doc.add_heading("3.3 Instrumentos e orçamento", level=2)
cred_ini = val.loc["2008-2011", "crédito / financiamento | % documento"]
cred_fim = val.loc["2024-2027", "crédito / financiamento | % documento"]
sel_pct = 100 * val["total_programas_selecionados"] / val["total_documento"]
par("Os instrumentos concretos quase não aparecem em objetivo e justificativa, mas aparecem nas ações e subações. "
    "O crédito, operado sobretudo pela Agência de Fomento do Estado (BADESC), está presente em todos os ciclos, mas "
    f"perde peso: representa {num(cred_ini)}% do valor do PPA em 2008-2011 e {num(cred_fim)}% em 2024-2027 (Figura 2). "
    "Arranjos produtivos locais aparecem como ação sobretudo até 2012-2015, e incubadoras e parques tecnológicos até 2016-2019. "
    f"Incentivos fiscais não aparecem em nenhum ciclo. Os programas selecionados somam entre {num(sel_pct.min())}% e "
    f"{num(sel_pct.max())}% do valor do PPA. Nas ações, a competitividade quase não aparece (cinco ocorrências, nenhuma "
    "depois de 2015), o que sugere distância entre o discurso e os instrumentos.")
figura("instrumentos_participacao_ppa.png", "Figura 2 – Participação dos programas selecionados e dos instrumentos no "
       "valor total do PPA")
par("Os valores são nominais. Nos anexos de 2004-2007 e 2008-2011, os valores referem-se a um único ano; por isso a "
    "comparação entre ciclos é feita pela participação no total do próprio plano. Nos demais ciclos, a soma das "
    "subações coincide com o total geral oficial do PPA, com diferença inferior a 0,4%.")

doc.add_heading("3.4 Robustez do resultado central", level=2)
par("O resultado de competitividade se manteve em todos os testes realizados (Quadro 2). O classificador de texto, "
    "uma regressão logística sobre TF-IDF treinada com a seleção manual, alcançou precisão média de 0,44, contra 0,08 "
    "ao acaso, e apontou como frágeis os mesmos programas já em debate. Ele também indicou programas não selecionados "
    "semelhantes aos selecionados, que foram testados em um cenário alternativo.")
tabela(["Teste", "Resultado"], [
    ["Termo isolado, contra o acaso (permutação)", "p = 0,002"],
    ["Termo isolado, contra 25 termos de mesma frequência", "acima de 96% dos controles"],
    ["Léxico expandido (dimensão), contra 1.000 léxicos aleatórios", "p = 0,004; acima de 99,7%"],
    ["Sem textos repetidos entre ciclos", "p = 0,014"],
    ["Retirando um programa de cada vez (42 casos)", "p abaixo de 0,03 em todos"],
    ["Acrescentando 8 programas indicados pelo classificador", "p = 0,003 (termo) e 0,004 (dimensão)"],
], [10, 6], "Quadro 2 – Testes de robustez do resultado de competitividade")
par("No cenário com os oito programas adicionais, outras conclusões mudam (Figura 3). A dimensão trabalho e renda "
    "deixa de ter um pico isolado em 2024-2027, que vinha da exclusão do programa 0530 entre 2008 e 2019, e o peso "
    "orçamentário da política industrial em 2012-2015 sobe de 2,1% para 5,5% do PPA. Essas conclusões dependem, "
    "portanto, da decisão sobre a lista de programas.")
figura("cenario_antes_depois.png", "Figura 3 – Resultados com a lista oficial (antes) e com oito programas "
       "adicionais (depois)")

doc.add_heading("3.5 Análises que não se sustentaram", level=2)
par("O modelo de tópicos (LDA) é instável: trocar a semente aleatória muda a maior parte do vocabulário dos tópicos "
    "(similaridade de Jaccard média entre 0,29 e 0,42). A clusterização de termos antes do LDA estabilizou os tópicos "
    "entre sementes, mas mudou por inteiro com a inclusão de um único programa. Os termos distintivos entre o início e "
    "o fim da série, estimados por log-odds com prior informativo (MONROE; COLARESI; QUINN, 2008), têm direção coerente "
    "com os demais resultados, mas só o termo rural é estatisticamente significativo. Os anexos dos PPAs não mencionam os "
    "Objetivos de Desenvolvimento Sustentável.")

# ------------------------------------------------------------------ 4
doc.add_heading("4 Limitações", level=1)
par("O PPA registra a intenção declarada de política, e não a política executada. O corpus é pequeno: de 4 a 9 "
    "programas e de 146 a 326 lemas por ciclo, o que limita a inferência estatística e inviabiliza modelos de tópicos. "
    "A seleção dos programas é manual e feita por uma única pessoa, e parte dos resultados depende dela. Vários "
    "programas repetem o texto de um ciclo para o outro. O PPA 2004-2007 já está dentro do ciclo de alta das "
    "commodities; o contraste com o período anterior depende do PPA 2000-2003, solicitado à Secretaria de Estado da "
    "Fazenda.")

# ------------------------------------------------------------------ 5
doc.add_heading("5 Pontos para discussão", level=1)
for i, txt in enumerate([
    "Lista de programas: confirmar os casos em debate (0250 Inclusão Digital, 0212 Comércio Exterior, 0354 Trabalho, "
    "Emprego e Renda), a permanência do 0210, que em 2024-2027 é dominado por emendas parlamentares, e a inclusão dos "
    "programas indicados pelo classificador (0530 em 2008-2019, 0101 Acelera Santa Catarina e 0204 Missões "
    "Internacionais).",
    "Tabela de equivalência de 2004-2007: validar as correspondências, considerando que o código 0530 se mantém até "
    "2016-2019.",
    "Léxico: manter os 20 termos validados ou fazer nova rodada de expansão.",
    "Modelo de tópicos: retirar dos resultados ou manter apenas como registro metodológico.",
    "Próxima fase: ligar os resultados ao índice de complexidade econômica das microrregiões, por exemplo pelo gasto "
    "regionalizado das subações (2004-2015) ou pelos setores visados e sua vantagem comparativa, como em Juhász et al. "
    "(2025).",
    "Classificador de texto: avaliar se vale ampliar com anotação independente por mais de um codificador.",
], start=1):
    par(f"{chr(96 + i)}) {txt}", recuo=False)

# ------------------------------------------------------------------ referências
doc.add_heading("Referências", level=1)
for ref in [
    "ASH, E.; HANSEN, S. Text algorithms in economics. **Annual Review of Economics**, v. 15, p. 659-688, 2023.",
    "CHANG, H.-J. **The political economy of industrial policy**. London: Macmillan, 1994.",
    "GENTZKOW, M.; KELLY, B. T.; TADDY, M. **Text as data**. Cambridge, MA: National Bureau of Economic Research, 2017. "
    "(NBER Working Paper, 23276).",
    "JUHÁSZ, R.; LANE, N.; OEHLSEN, E.; PÉREZ, V. C. **Measuring industrial policy**: a text-based approach. [S. l.], 2025. "
    "Versão de junho de 2025.",
    "MONROE, B. L.; COLARESI, M. P.; QUINN, K. M. Fightin' words: lexical feature selection and evaluation for "
    "identifying the content of political conflict. **Political Analysis**, v. 16, n. 4, p. 372-403, 2008.",
    "RODRIK, D. **Industrial policy for the twenty-first century**. Cambridge, MA: Harvard University, 2004.",
    "RODRIK, D. **Normalizing industrial policy**. Washington, DC: World Bank, 2008. (Commission on Growth and "
    "Development Working Paper, 3).",
    "SANTA CATARINA. **Plano Plurianual**: anexo único. Florianópolis: Secretaria de Estado da Fazenda, 2004-2024. "
    "Ciclos 2004-2007, 2008-2011, 2012-2015, 2016-2019, 2020-2023 e 2024-2027.",
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    for k, trecho in enumerate(ref.split("**")):
        p.add_run(trecho).bold = (k % 2 == 1)

doc.save(SAIDA)
print("ok:", SAIDA)


