"""Documento informal de status do trabalho (para os orientadores), em .docx.

Saída: saidas/estado_do_trabalho_2026-11-12_v7.docx
Figuras: as versões no tamanho de impressão (saidas/doc_*.png, geradas por scripts/figuras_doc.py).
Dados: lexico_validado.csv, valores_instrumentos.csv, orcamento_ajustado.csv (scripts/orcamento_ajustado.py),
       robustez_competitividade.csv (scripts/robustez_competitividade.py).
"""
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

RAIZ = Path(__file__).resolve().parent.parent
S = RAIZ / "saidas"
SAIDA = S / "estado_do_trabalho_2026-11-12_v7.docx"

lex_all = pd.read_csv(S / "lexico_validado.csv", encoding="utf-8")
val = pd.read_csv(S / "valores_instrumentos.csv", encoding="utf-8").set_index("periodo")
aj = pd.read_csv(S / "orcamento_ajustado.csv", encoding="utf-8").set_index("periodo")
rob = pd.read_csv(S / "robustez_competitividade.csv", encoding="utf-8").set_index("teste")

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
for lado in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(sec, lado, Cm(2.2))


def arial(estilo, tam, negrito=False):
    st = doc.styles[estilo]
    st.font.name, st.font.size, st.font.bold = "Arial", Pt(tam), negrito
    rf = st.element.rPr.rFonts
    for att in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(att), "Arial")
    for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rf.attrib.pop(qn(att), None)
    for c in st.element.rPr.findall(qn("w:color")):
        st.element.rPr.remove(c)
    return st


arial("Normal", 11).paragraph_format.line_spacing = 1.15
doc.styles["Normal"].paragraph_format.space_after = Pt(6)
arial("List Bullet", 11)
for nome, tam in (("Title", 18), ("Heading 1", 13), ("Heading 2", 11.5)):
    st = arial(nome, tam, True)
    st.paragraph_format.space_before = Pt(14 if nome == "Heading 1" else 8)
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.keep_with_next = True
for pbdr in doc.styles["Title"].element.findall(".//" + qn("w:pBdr")):
    pbdr.getparent().remove(pbdr)


def p(texto, tam=None, italico=False):
    par = doc.add_paragraph()
    r = par.add_run(texto)
    r.italic = italico
    if tam:
        r.font.size = Pt(tam)
    return par


def b(texto, destaque=None):
    par = doc.add_paragraph(style="List Bullet")
    if destaque:
        par.add_run(destaque).bold = True
    par.add_run(texto)
    par.paragraph_format.space_after = Pt(3)
    return par


def fig(arquivo, legenda, largura=16.5):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.keep_with_next = True
    par.add_run().add_picture(str(S / arquivo), width=Cm(largura))
    leg = doc.add_paragraph()
    leg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = leg.add_run(legenda)
    r.italic, r.font.size = True, Pt(9)


def tabela(cabecalho, linhas, larguras, tam=9.5):
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.style = "Table Grid"
    for i, txt in enumerate(cabecalho):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(txt)
        r.bold, r.font.size = True, Pt(tam)
    for linha in linhas:
        cells = t.add_row().cells
        for i, txt in enumerate(linha):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(txt)).font.size = Pt(tam)
    for row in t.rows:
        for i, w in enumerate(larguras):
            row.cells[i].width = Cm(w)
            for pp in row.cells[i].paragraphs:
                pp.paragraph_format.space_after = Pt(1)
                pp.paragraph_format.line_spacing = 1.0
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


br = lambda x, c=1: f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")
pv = lambda x: "< 0,001" if x < 0.001 else br(x, 3)
cred = lambda per: val.loc[per, "crédito / financiamento | % documento"]
sel = lambda per: 100 * val.loc[per, "total_programas_selecionados"] / val.loc[per, "total_documento"]
PER = list(val.index)
r_dim = rob.loc["selecionados | dimensão"]
r_sem = rob.loc["selecionados | só a semente"]
r_nov = rob.loc["selecionados | só os termos novos"]
r_353 = rob.loc["selecionados sem o 0353 | dimensão"]
r_353s = rob.loc["selecionados sem o 0353 | só a semente"]
r_ppa = rob.loc["PPA inteiro | dimensão"]
r_ppas = rob.loc["PPA inteiro | só a semente"]
r_nao = rob.loc["não selecionados | dimensão"]
r_inov = rob.loc["selecionados | inovação + digital"]
oc = lambda r, per: r[f"{per} ocorr/lemas"].split("/")

# ================================================================== cabeçalho
doc.add_paragraph("TCC: estado atual da análise dos PPAs", style="Title")
p("Andrey de Paula e Silva  ·  12/11/2026  ·  para Dominik e Lukas, antes da reunião de 13/11", tam=10)

# ================================================================== resumo
doc.add_heading("Em resumo", level=1)
b(" 6 PPAs de Santa Catarina (2004-2007 a 2024-2027) e 42 pares programa-PPA de política industrial (19 códigos "
  "distintos, 9 deles do 2004-2007, que usa outra numeração).", "Corpus:")
b(" 20 termos em 5 dimensões, expandido a partir dos próprios textos e validado termo a termo.", "Léxico:")
b(" a única dimensão do discurso que muda além do acaso é a de competitividade, com alta no último PPA "
  "(2024-2027). A alta vem da própria palavra \"competitividade\", não dos termos acrescentados na expansão, e se "
  "mantém com mudanças na lista de programas. Ela é concentrada nos programas de política industrial: no restante "
  "do PPA a taxa fica estável. As contagens são pequenas (12 ocorrências no último PPA).", "Achado principal:")
b(" os instrumentos concretos (crédito, APL, incubadoras) aparecem nas ações dos programas, não nos objetivos. "
  "Tirando folha de pessoal e emendas parlamentares, a parcela do PPA que vai para a política industrial cai de "
  f"{br(aj.loc['2008-2011', 'pct_selecionados_sem_pessoal_emendas'])}% (2008-2011) para "
  f"{br(aj.loc['2024-2027', 'pct_selecionados_sem_pessoal_emendas'])}% (2024-2027), e o crédito do BADESC a "
  f"empresas, de {br(aj.loc['2008-2011', 'pct_credito_empresas'], 2)}% para "
  f"{br(aj.loc['2024-2027', 'pct_credito_empresas'], 2)}%. O discurso de competitividade cresce enquanto o "
  "orçamento dos instrumentos encolhe.", "Instrumentos:")
b(" os PPAs não citam os ODS, e o vocabulário das metas dos ODS não cresce depois de 2015.", "ODS:")
b(" o modelo de tópicos (LDA) não é estável com esse corpus e fica fora dos resultados.", "O que não se sustentou:")

# ================================================================== resultados
doc.add_heading("Resultados", level=1)

doc.add_heading("1. Competitividade é a única dimensão que muda", level=2)
p("Para cada dimensão do léxico, a medida é quantos lemas da dimensão aparecem a cada mil lemas do texto (objetivo e "
  "justificativa) dos programas selecionados em cada PPA. Lema é a palavra na forma de dicionário (\"competitivas\" "
  "vira \"competitivo\"); só entram substantivos, verbos e adjetivos. Só \"competitividade e produção\" "
  f"(competitividade, competitivo, produtividade, diversificação) varia mais do que o acaso: p = {pv(r_dim.p_amplitude)} no teste de "
  "permutação, que sorteia os programas entre os PPAs, e variação maior que a de 99,7% de 1.000 léxicos aleatórios "
  "com lemas de frequência parecida. Como foram testadas 5 dimensões, o limite corrigido (Bonferroni) é 0,01, e o "
  "resultado passa. As outras dimensões não se distinguem do acaso.")
fig("doc_lexico.png", "Lemas de cada dimensão do léxico a cada mil lemas analisados, por PPA. Azul: "
    "competitividade e produção, com intervalo de confiança de 95% (faixa clara); cinza: demais dimensões.", largura=12.5)
p(f"O formato da série importa. A taxa é zero em 2004-2007, fica entre 14 e 22 por mil de 2008 a 2023 e vai a 44 por "
  f"mil em 2024-2027. Os números absolutos são pequenos: {oc(r_dim, '2024-2027')[0]} ocorrências em "
  f"{oc(r_dim, '2024-2027')[1]} lemas no último PPA, e o zero de 2004-2007 vem de textos curtos "
  f"({oc(r_dim, '2004-2007')[1]} lemas). Uma tendência contínua no tempo não é significativa "
  f"(p = {br(r_dim.p_tendencia, 2)}), e os intervalos de confiança de 2012-2015 e de 2024-2027 se sobrepõem. O "
  f"teste direto do último PPA contra os cinco anteriores juntos dá {br(r_dim.dif_ultimo_vs_antes, 0)} ocorrências a "
  f"mais por mil lemas (intervalo de 95% de {br(r_dim.dif_ic_inf, 0)} a {br(r_dim.dif_ic_sup, 0)}; "
  f"p = {pv(r_dim.p_ultimo_maior)}). A leitura que os dados sustentam é a de um patamar estável de 2008 a 2023 e uma "
  "alta no último PPA, apoiada em poucas ocorrências.")
p("Semente x expansão. Os termos novos entraram por coocorrência com a semente e poderiam só repetir a trajetória "
  "dela. A tabela separa as duas coisas:")
linhas = []
for nome, r in (("Dimensão (4 termos)", r_dim), ("Só \"competitividade\"", r_sem),
                ("Só os 3 termos novos", r_nov), ("Dimensão, sem o 0353", r_353),
                ("Só \"competitividade\", sem o 0353", r_353s)):
    linhas.append([nome] + [br(r[f"{per} taxa"]) for per in PER] + [pv(r.p_amplitude), pv(r.p_ultimo_maior)])
tabela(["Medida (por mil lemas)"] + [x[2:4] + "-" + x[-2:] for x in PER] + ["p variação", "p último PPA"], linhas,
       [4.6, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.9, 2.3], tam=9)
p(f"A alta vem da própria semente (p = {pv(r_sem.p_amplitude)}); os termos novos, sozinhos, não mudam "
  f"(p = {br(r_nov.p_amplitude, 2)}). A expansão do léxico não está produzindo o resultado. O 0353 (Incentivo à "
  "Competitividade da Indústria, do Comércio e do Serviço), que só existe em 2024-2027 e tem a palavra no nome, "
  "reforça a alta, mas sem ele o resultado continua.")
p("A mudança também é de sentido. Em 2008-2011, competitividade aparece numa frase só, como meta de um programa "
  "econômico (o 0200, Competitividade e Excelência Econômica). Entre 2012 e 2019, ligada a cadeias específicas "
  "(agronegócio, micro e pequenas empresas). Em 2020-2023, como \"competitividade das empresas catarinenses\". Em "
  "2024-2027, aparece em seis programas, inclusive de ciência e tecnologia e de qualificação de trabalhadores, e "
  "surge pela primeira vez a expressão \"setores estratégicos\". O PPA 2024-2027 é o primeiro do governo que "
  "começou em 2023; a relação com a troca de governo ainda precisa ser examinada.")

doc.add_heading("2. Lista de programas e viés de seleção", level=2)
p("Os programas foram escolhidos lendo nome e objetivo, então é preciso saber se o achado vem da escolha.")
b(" continua significativo nos 42 casos (p abaixo de 0,03).", "Retirando um programa de cada vez:")
b(f" continua (p = {br(r_353.p_amplitude, 2)} na dimensão; p = {pv(r_353s.p_amplitude)} só com a semente).",
  "Sem o 0353 (Incentivo à Competitividade da Indústria, do Comércio e do Serviço):")
b(" não muda. São 3 programas apontados pelo classificador como parecidos com os selecionados, que somam 8 pares "
  "programa-PPA: 0530 (Pró-Emprego e Renda) de 2008 a 2019, 0101 (Acelera Santa Catarina) de 2012 a 2027 e 0204 "
  "(Missões, Recepções e Eventos Internacionais) em 2016-2019.", "Acrescentando 3 programas (8 pares):")
b(" o resultado se mantém.", "Contando uma vez só os textos copiados de um PPA para o outro:")
b(f" a dimensão não muda de forma significativa (de {br(r_ppa['2004-2007 taxa'])} a {br(r_ppa['2024-2027 taxa'])} "
  f"por mil; p = {br(r_ppa.p_amplitude, 2)}), e nos {int(r_nao.documentos)} programas fora da lista ela fica "
  f"estável (entre {br(min(r_nao[f'{x} taxa'] for x in PER))} e {br(max(r_nao[f'{x} taxa'] for x in PER))} por mil).",
  f"No PPA inteiro ({int(r_ppa.documentos)} programas):")
p("A alta é específica dos programas de política industrial, e isso tem duas leituras. A favorável: o discurso de "
  "competitividade se concentrou na política industrial, sem virar retórica do plano inteiro. A cautelosa: como a "
  "seleção foi feita lendo os textos, não dá para descartar de todo que ela tenha favorecido programas com esse "
  "vocabulário. Os testes acima mostram que nenhum programa isolado produz o resultado e que a lista é quase a mesma "
  "de 2008 a 2027 (0200, 0210, 0230, 0310 e 0342 atravessam o período), o que reduz, mas não elimina, esse risco.")
p(f"Outras conclusões dependem da lista. Com os 8 pares a mais, o \"pico de emprego em 2024-2027\" desaparece (ele "
  f"vinha de o 0530 (Pró-Emprego e Renda) estar fora entre 2008 e 2019), e a parcela do orçamento do PPA que vai "
  f"para a política industrial em 2012-2015 sobe de {br(sel('2012-2015'))}% para 5,5%.")
fig("doc_cenario.png", "Mesmas medidas com a lista atual (tracejado, 42 pares programa-PPA) e com 3 programas a mais "
    "(azul, 50 pares).")

doc.add_heading("3. Instrumentos: o que os programas fazem e quanto dinheiro planejam", level=2)
p("Aqui a pergunta não é sobre palavras do discurso, e sim sobre as ações. Cada programa do PPA tem ações e subações "
  "(por exemplo, \"Apoio creditício às micro e pequenas empresas - BADESC\"), e cada subação tem um valor orçado em "
  "reais. Os instrumentos foram procurados no nome das ações, e os valores, somados.")
b(" linhas de crédito do BADESC aparecem em todos os PPAs; desde 2020 há também o Microcrédito Juro Zero.", "Crédito:")
b(" APL aparece como ação até 2012-2015; incubadoras, parques e centros de inovação, até 2016-2019.",
  "APL e incubadoras:")
b(" é sobretudo capacitação de gestores públicos e de agricultores (EPAGRI); ensino técnico praticamente não aparece.",
  "Qualificação:")
p("Dois itens não são instrumento de política industrial e foram separados: a folha de pagamento da EPAGRI e as "
  "emendas parlamentares. A folha estava em programas de gestão de pessoal até 2019 (0110, Apoio Administrativo, "
  "em 2004-2007; 0850, Gestão de Pessoas, em 2012-2019) e passou para o 0310 (Desenvolvimento Agropecuário e "
  "Pesqueiro) em 2020. O aumento aparente do orçamento da política industrial em 2020-2027 é, portanto, contábil. "
  "As emendas do Fundo Social e do Fundam entram no 0210 (Desenvolvimento Regional Integrado) desde 2020. No "
  "crédito, a maior linha do BADESC, \"Apoio creditício ao desenvolvimento dos municípios\", é crédito a "
  "prefeituras e foi separada do crédito a empresas.")
linhas = []
for per in PER:
    um_ano = per in ("2004-2007", "2008-2011")
    linhas.append([per + (" *" if um_ano else ""),
                   br(val.loc[per, "total_documento"] / 1e9),
                   f"{br(val.loc[per, 'total_programas_selecionados'] / 1e9, 2)} ({br(sel(per))}%)",
                   f"{br(aj.loc[per, 'pct_selecionados_sem_pessoal_emendas'])}%",
                   f"{br(aj.loc[per, 'credito_total'] / 1e6, 0)} ({br(aj.loc[per, 'pct_credito_total'], 2)}%)",
                   f"{br(aj.loc[per, 'credito_empresas'] / 1e6, 0)} ({br(aj.loc[per, 'pct_credito_empresas'], 2)}%)"])
p("Orçamento planejado (valores nominais, em reais correntes):", tam=10)
tabela(["PPA", "Total do PPA (R$ bi)", "Política industrial (R$ bi e % do PPA)",
        "Política industrial sem pessoal e emendas (% do PPA)", "Crédito total (R$ mi e % do PPA)",
        "Crédito a empresas (R$ mi e % do PPA)"], linhas, [2.3, 2.0, 3.1, 3.0, 3.1, 3.1], tam=9)
p("* Nos anexos de 2004-2007 e 2008-2011 os valores são de um ano só (o último do plano); nos demais, dos quatro anos. "
  "Por isso a comparação entre PPAs é feita pela parcela do orçamento (%), e não pelo valor em reais.", tam=9,
  italico=True)
p(f"Leitura: sem pessoal e emendas, a parcela da política industrial no PPA cai de forma contínua, de "
  f"{br(aj.loc['2008-2011', 'pct_selecionados_sem_pessoal_emendas'])}% em 2008-2011 para "
  f"{br(aj.loc['2024-2027', 'pct_selecionados_sem_pessoal_emendas'])}% em 2024-2027. O crédito a empresas cai de "
  f"R$ {br(aj.loc['2008-2011', 'pct_credito_empresas'], 2)} para R$ {br(aj.loc['2024-2027', 'pct_credito_empresas'], 2)} "
  "a cada R$ 100 do PPA. Em reais correntes ele fica quase estável, o que, com a inflação, significa queda real.")
p("Discurso x instrumento: a competitividade, que cresce no texto dos objetivos, quase não aparece no nome das ações "
  "(a palavra aparece 5 vezes, nenhuma depois de 2015). O discurso sobe enquanto o orçamento dos instrumentos "
  "desce.")
p("Dois limites dessa comparação:")
b(" o PPA registra só o crédito que passa pelo orçamento do Estado. O BADESC também opera com recursos próprios, "
  "fundos e captações externas (por exemplo, BID). A queda da parcela no orçamento não é necessariamente queda do "
  "crédito ofertado; isso precisa ser conferido nos demonstrativos do BADESC.", "Crédito do BADESC:")
b(" não aparece em nenhum PPA. Em Santa Catarina boa parte da política industrial passa pelo ICMS (o PRODEC, por "
  "exemplo), que é renúncia de receita e fica fora do PPA. O demonstrativo de renúncia de receita da LDO pode virar "
  "uma série complementar; se não der tempo, fica como limitação explícita.", "Incentivo fiscal:")

doc.add_heading("4. ODS: o vocabulário da Agenda 2030 não aparece nos PPAs", level=2)
p("A primeira checagem procurou só a sigla (\"ODS\", \"Agenda 2030\") e achou zero. A segunda procurou o conteúdo: a "
  "partir do texto oficial dos 17 objetivos e das 169 metas (ONU Brasil), cada ODS ganhou um conjunto com os termos "
  "mais característicos das suas metas (sem os genéricos, como \"empresa\" ou \"conservação\"), medido em todo o PPA "
  "(529 programas) e nos 42 pares de política industrial, comparando 2004-2015 com 2016-2027.")
b(" nenhum ODS cresce de forma significativa depois de 2015, nem no PPA inteiro nem nos programas de política "
  "industrial. O vocabulário somado dos 17 ODS vai de 42 para 46 por mil lemas (p = 0,34).", "Resultado:")
b(" o ODS 9 (indústria e inovação) vai de 2,6 para 4,8 por mil (p = 0,07), mas, com 17 testes, isso não chega a "
  "ser tendência; o mesmo vale para os ODS 10 e 17. Clima (ODS 13) só aparece a partir de 2020 e com 2 ocorrências; "
  "igualdade de gênero (ODS 5) tem zero em 20 anos.", "Variações pequenas:")
b(" os temas que coincidem com os ODS (educação, cidades e transporte, trabalho, energia) já estavam nos PPAs antes "
  "de 2015 e ficam estáveis.", "Temas antigos:")
b(" pela similaridade de vetores de palavras, os programas de política industrial ficam mais próximos do ODS 9, o "
  "que confirma a seleção de programas por outro caminho.", "Validação da curadoria:")
fig("doc_ods.png", "Lemas de cada ODS a cada mil lemas do PPA inteiro (linha tracejada: Agenda 2030, setembro "
    "de 2015).")

# ================================================================== o que não se sustentou
doc.add_heading("O que não se sustentou", level=1)
doc.add_heading("LDA (modelo de tópicos)", level=2)
p("O LDA procura \"temas\" agrupando palavras que costumam aparecer juntas nos mesmos programas. Para o resultado "
  "valer, rodar de novo deveria dar os mesmos temas. Foram feitos três testes:")
b(" com sementes aleatórias diferentes, só 29% a 42% das palavras de cada tópico se repetem. Os temas mudam a cada "
  "rodada.", "Estabilidade:")
b(" com as palavras agrupadas antes em campos de sentido (vetores do spaCy), o LDA sobre esses campos ficou estável "
  "entre sementes (similaridade de 0,91 a 0,97), o que parecia resolver.", "Clusterização prévia (sugestão do Dominik):")
b(" com um único programa a mais no corpus (o 0530, Geração de Emprego e Renda, de 2004-2007), os campos se "
  "reorganizaram por inteiro e os tópicos mudaram. Um resultado que muda com um programa a mais não sustenta "
  "interpretação.", "O problema:")
p("A causa é o tamanho do corpus: 42 pares programa-PPA e cerca de 1.500 lemas analisados, quando o LDA costuma "
  "precisar de centenas ou milhares de documentos. A proposta é tratar o LDA como teste realizado, e não como "
  "resultado, e usar no lugar o índice por dimensão do léxico, que é mais simples e pode ser testado contra o acaso. "
  "Com um corpus maior (texto das ações e subações, ou o PPA 2000-2003, se for obtido), vale tentar de novo.")
doc.add_heading("Outros", level=2)
b(" a direção bate com o resto, mas só \"rural\" é estatisticamente significativo.",
  "Palavras típicas do início x do fim da série:")
b(" o 2004-2007 parece uma ruptura, mas os textos dele são muito curtos para afirmar isso.",
  "Similaridade entre PPAs:")
b(f" juntar \"computador\" à inovação não muda nada; inovação continua sem variação significativa "
  f"(p = {br(r_inov.p_amplitude, 2)}).", "Dimensão digital:")

# ================================================================== limitações
doc.add_heading("Limitações", level=1)
b(" o PPA registra a intenção declarada de política, não a política executada.", "Intenção, não execução:")
b(" de 4 a 9 programas e de 146 a 326 lemas analisados por PPA, com contagens de um dígito em várias células. "
  "Isso limita os testes estatísticos e inviabiliza modelos de tópicos.", "Corpus pequeno:")
b(" a seleção dos programas é manual e feita por uma pessoa; parte dos resultados (emprego, digital, peso "
  "orçamentário) depende dela. O achado de competitividade resiste às mudanças testadas na lista, mas não aparece "
  "fora dela.", "Seleção manual:")
b(" a validação dos termos também foi feita por uma pessoa só.", "Léxico:")
b(" vários programas repetem o texto de um PPA para o outro (7 de 31 pares de períodos consecutivos têm texto "
  "idêntico), o que infla a semelhança entre PPAs vizinhos.", "Texto herdado:")
b(" os valores orçados são nominais; em 2004-2007 e 2008-2011 os anexos trazem só um ano. O crédito fora do "
  "orçamento do Estado e a renúncia de ICMS não estão no PPA.", "Valores:")
b(" o PPA 2004-2007 já está dentro do ciclo de alta das commodities; o contraste com o período anterior depende do "
  "PPA 2000-2003, que não está disponível na SEF (Lei 11.357/2000) e foi solicitado à ALESC.", "Janela temporal:")
b(" toda a análise até aqui é estadual, e a tese é sobre microrregiões.", "Escala:")

# ================================================================== pontos em aberto
doc.add_heading("Pontos em aberto", level=1)
b(" é a decisão principal. Toda a análise está no nível estadual, e a tese é sobre as 20 microrregiões. O caminho "
  "mais direto parece ser o orçamento regionalizado das SDRs (2004-2015), que permite dar a cada microrregião um "
  "valor de política industrial e relacioná-lo à trajetória do ICE. O caminho setorial, como em Juhász et al. (2025), "
  "é mais difícil, porque os programas raramente nomeiam setores.", "Ponte com o ICE:")
b(" ainda quase não aparece no trabalho. A primeira tarefa é cruzar a alta de 2024-2027 com a troca de governo de "
  "2023 e com o cenário econômico de cada PPA.", "Contexto histórico:")
b(" falta definir os casos em debate, 0250 (Inclusão Digital), 0212 (Comércio Exterior e Relações "
  "Internacionais) e 0354 (Promoção de Políticas de Trabalho, Emprego e Renda); a permanência do 0210 (Desenvolvimento "
  "Regional Integrado), que em 2024-2027 é quase todo emendas parlamentares; e os 3 programas sugeridos pelo "
  "classificador: 0530 (Pró-Emprego e Renda), 0101 (Acelera Santa Catarina) e 0204 (Missões, Recepções e Eventos "
  "Internacionais).",
  "Lista de programas:")
b(" a correspondência dos códigos de 2004-2007 com os PPAs seguintes ainda é uma proposta. O 0530 tem o mesmo "
  "código com dois nomes: Geração de Emprego e Renda em 2004-2007 e Pró-Emprego e Renda de 2008 a 2019.",
  "Tabela de equivalência:")
b(" a dimensão digital, com um termo só (\"computador\"), não funciona como dimensão; a proposta é juntá-la à "
  "inovação. \"Renda\" e \"trabalho\" são genéricas em PPA e podem sair. Também a alinhar se algum dos 9 termos em "
  "espera volta (por exemplo, \"setor\" e \"regional\") e se vale mais uma rodada de expansão.", "Léxico:")
b(" a validação foi feita por uma pessoa. Uma segunda pessoa avaliando os 38 candidatos, e uma amostra de programas "
  "com mais de um codificador, permitiriam medir a concordância, como no artigo de Juhász et al.",
  "Segunda avaliação:")
b(" a alinhar se sai dos resultados ou fica só como registro metodológico.", "LDA:")
b(" pode ficar como trabalho futuro.", "Comparação com outras UFs:")

# ================================================================== registro
doc.add_heading("Registro do que foi feito desde 30/09", level=1)
b(" PPA 2004-2007 incluído; o 2000-2003 não está disponível na SEF (Lei 11.357/2000) e foi solicitado à ALESC.",
  "Janela temporal:")
b(" candidatos a partir das 5 palavras iniciais, por coocorrência e por similaridade de vetores de palavras "
  "(spaCy). Dos 38 termos avaliados, 20 entraram, 9 foram descartados por serem genéricos ou fragmentos e 9 ficaram "
  "em espera por serem ambíguos (lista ao final).", "Léxico (snowballing):")
b(" busca pela sigla e pelo vocabulário das 169 metas oficiais.", "ODS:")
b(" teste de permutação, comparação com palavras de mesma frequência, 1.000 léxicos aleatórios, semente x "
  "expansão, último PPA x anteriores e o mesmo índice no PPA inteiro.", "Circularidade e viés de seleção:")
b(" busca de crédito, APL, cluster, incentivo fiscal, pequenos produtores e qualificação nos objetivos e nas ações "
  "dos programas, com os valores orçados, separando pessoal, emendas e crédito a municípios.", "Tipos de política:")
b(" um classificador simples (TF-IDF e regressão logística), no espírito de Juhász et al. (2025), usado só para "
  "conferir a seleção de programas.", "Conferência da curadoria:")
b(" figura conceitual do método e rascunho da seção de metodologia (programa x seção).", "Metodologia:")

# ================================================================== léxico
doc.add_heading("Léxico", level=1)
p("Regra usada na validação: um candidato entra quando, nas frases dos PPAs em que aparece, se refere a uma das "
  "cinco dimensões e não é palavra genérica de planejamento (que aparece em quase todo programa). Variantes da "
  "mesma palavra entram juntas (competitividade e competitivo). Fica em espera quando o sentido depende da frase; "
  "sai quando é fragmento de expressão, palavra genérica ou de outra agenda.")
doc.add_heading("Termos que entraram (20)", level=2)
p("As sementes são as palavras usadas desde o início; os termos novos vieram da expansão e foram validados um a um. "
  "\"Digital\" ficou em espera (aparece 4 vezes, num programa só), então a dimensão digital ficou só com "
  "\"computador\".")
ordem = ["competitividade e produção", "inovação e tecnologia", "inserção internacional", "trabalho e renda", "digital"]
linhas = []
for d in ordem:
    g = lex_all[(lex_all.dimensao == d) & lex_all.decisao.isin(["entra", "variante"])]
    linhas.append([d.capitalize(), ", ".join(g[g.origem == "semente"].termo) or "(nenhuma)",
                   ", ".join(g[g.origem == "candidato"].termo), str(len(g))])
tabela(["Dimensão", "Sementes (desde o início)", "Termos novos (expansão)", "Nº"], linhas, [4.4, 3.8, 7.2, 1.2], tam=9)

doc.add_heading("Termos que ficaram de fora (18)", level=2)
p("Nove foram descartados por não terem relação real com política industrial nos PPAs (fragmentos de expressões, "
  "palavras genéricas ou de outra agenda). Os outros nove fazem sentido, mas são ambíguos: o significado depende da "
  "frase, e incluí-los aumentaria o ruído. Esses ficaram em espera.")
motivos = {
    "economia": "genérica: aparece em quase todo programa",
    "micro": "fragmento de \"micro e pequenas empresas\"",
    "provedora": "vem de \"provedora de condições\", não tem relação com digital",
    "sustentabilidade": "outra agenda (ambiental)",
    "desenvolvimento": "genérica: aparece em quase todo programa",
    "criação": "genérica (\"criação de...\")",
    "empresa": "genérica: aparece em quase todo programa",
    "nacional": "o modelo a aproxima de \"internacional\" por oposição, não por sentido",
    "governamental": "genérica",
    "digital": "semente original, mas só 4 ocorrências, todas num programa",
    "qualidade": "qualidade de produto ou qualidade de vida?",
    "mercado": "mercado interno ou externo, depende da frase",
    "negócio": "ambiente de negócios; muito próxima de \"empresa\"",
    "investimento": "atração de investimento é política industrial, mas a palavra também é orçamentária",
    "cooperação": "cooperação tecnológica ou internacional",
    "empresarial": "adjetivo pouco específico",
    "setor": "\"setores estratégicos\" indica política vertical, mas \"setor\" sozinho é genérico",
    "regional": "seria outra dimensão; interessante para as microrregiões",
}
fora = lex_all[~lex_all.decisao.isin(["entra", "variante"])]
linhas = []
for dec, rot in (("não entra", "descartado"), ("talvez", "em espera")):
    for t in fora[fora.decisao == dec].termo:
        linhas.append([t, rot, motivos.get(t, "")])
tabela(["Termo", "Situação", "Motivo"], linhas, [2.8, 2.0, 11.8], tam=9)
ultimo = doc.paragraphs[-1]                  # parágrafo vazio após a última tabela: reduzido a 1 pt para não abrir página em branco
ultimo.paragraph_format.space_after = ultimo.paragraph_format.space_before = Pt(0)
ultimo.paragraph_format.line_spacing = Pt(1)
ultimo.add_run("").font.size = Pt(1)

try:
    doc.save(SAIDA)
except PermissionError:                     # arquivo aberto no Word: salva com outro nome
    SAIDA = SAIDA.with_name(SAIDA.stem + "b.docx")
    doc.save(SAIDA)
print("ok:", SAIDA)
