"""Listas e regras de seleção da análise do PPA inteiro (rodada pós-reunião de 13/11/2026).

Todas aprovadas pelo Andrey em 13/11/2026, antes de rodar a análise (ver docs/decisoes.md).
Nada aqui é escolhido à mão depois: o notebook notebooks/analise_ppa_inteiro.ipynb só aplica
estas regras. Para mudar uma regra, mudar aqui e registrar em docs/decisoes.md.

Medida principal: contagem e % sobre o total de lemas (sem TF-IDF).
"""
import re
import unicodedata

import pandas as pd

# ---------------------------------------------------------------- temas (lemas)
# Lemas de objetivo + justificativa (spaCy pt_core_news_lg, substantivos, verbos e adjetivos).
LEXICO_ATUAL = {   # léxico validado (saidas/lexico_validado.csv, decisão "entra" ou "variante")
    "inovação e tecnologia": ["inovação", "tecnologia", "modernização", "tecnológico"],
    "competitividade e produção": ["competitividade", "produtividade", "competitivo", "diversificação"],
    "inserção internacional": ["internacional", "exportação", "mundial", "global", "comercial"],
    "trabalho e renda": ["emprego", "qualificação", "trabalhador", "empregar", "trabalho", "renda"],
    "digital": ["computador"],
}
TEMAS = {
    "inovação": LEXICO_ATUAL["inovação e tecnologia"],
    "competitividade": LEXICO_ATUAL["competitividade e produção"],
    # educação: versão "núcleo" (aprovada); ficaram fora formação, capacitação, qualificação,
    # técnico, conhecimento e pesquisa, por ambiguidade
    "educação": ["educação", "ensino", "estudante", "escolar", "escola", "professor", "educacional",
                 "aprendizagem", "aluno", "universidade", "curso", "educativo"],
    # indústria: versão "ampliada" (aprovada) = estrita + produtivo, cadeia, setorial
    "indústria": ["indústria", "industrial", "agroindústria", "agroindustrial",
                  "produtivo", "cadeia", "setorial"],
    "empresa": ["empresa", "empresarial", "empreendedor", "empreendimento", "microempresa",
                "empresário", "empreendedorismo"],
    "política industrial (léxico atual)": sorted({t for ts in LEXICO_ATUAL.values() for t in ts}),
}
PALAVRAS_SOLTAS = ["inovação", "competitividade", "empresa", "indústria", "industrial", "tecnologia",
                   "educação"]

# ---------------------------------------------------------------- público-alvo (demanda)
# Aplicado ao campo PÚBLICO-ALVO, sem acento e em minúsculas. Um programa pode ter mais de
# uma categoria; o que não casa com nenhuma vai para "outros". Versão aprovada: só as 7
# categorias propostas pelo Andrey.
# Correção feita depois de ver os casos (a aprovar): saíram "client" (pegava os 13 programas da
# Celesc, "clientes atuais e potenciais", consumidores de energia) e "\bpj\b" (pegava "pf, pj sem
# fins lucrativos"); "polpula" cobre o erro de digitação "polpulação" que aparece no PDF.
PUBLICO = {
    "empresas": r"empres|empreend|investidor|industri|pessoa juridica",
    "micro e pequenas empresas": r"\bmicro|pequen|individua",
    "trabalhadores": r"trabalhador|desempreg",
    "produtores rurais": r"agricult|produtor|pescador|aquicult|pecuarist|do campo|rura|agro",
    "municípios": r"municipi|prefeit",
    "instituições de pesquisa": r"\bcti\b|universidade|pesquis",
    "sociedade em geral": r"popula|polpula|cidad|sociedade|usuario|consumidor|geral|turist",
}

# ---------------------------------------------------------------- subações (item 4)
# (inclusão, exclusão), sem acento. Correções depois de ver os casos (a aprovar): "\bciencia" (sem a
# fronteira casava "deficiencia" e "eficiencia") e "subvenc\w* econom" (só "subvenção econômica";
# "subvenc" pegava subvenção a organizações sociais da saúde e a bombeiros comunitários).
SUBACAO_TEMA = {
    "inovação": (r"inova|cientific|\bciencia|\bcti\b|pesquisa e desenvolvimento|desenvolvimento tecnologic"
                 r"|incubad|parques? tecnologic|startup|base tecnologica|bolsas? de pesquisa"
                 r"|pesquisa agropecuaria",
                 r"tecnologia da informac|informatica"),
    "indústria e empresa": (r"industri|empresa|empreend|\bapls?\b|arranjos? produtiv|cadeias? produtiv"
                            r"|exporta|microcredito|fundo de aval|subvenc\w* econom",
                            r"amortizac|encargos|co-?financ|penitenciaria|municipi|usina|\bpch"),
}

# ---------------------------------------------------------------- áreas por órgão
# Oferta (quem executa) no item 3 e temas do orçamento no item 6. Aplicado ao nome do órgão
# responsável do programa, sem acento e em minúsculas; vale a PRIMEIRA área que casar.
AREAS = [
    ("outros poderes", r"assemble|tribunal|ministerio publico|defensoria"),
    ("CT&I", r"amparo a pesquisa|ciencia, tecnologia e inovacao"),
    ("desenvolvimento econômico e indústria",
     r"desenvolvimento economico|desenvolvimento sustentavel|industria do comercio|agencia de fomento"
     r"|sc participacoes|metrologia"),
    ("agricultura e pesca", r"agricultura|desenvolvimento agricola"),
    ("educação", r"educacao|universidade"),
    ("saúde", r"saude"),
    ("segurança, justiça e prisional", r"seguranca|justica|prisional|transito"),
    ("infraestrutura, energia e saneamento",
     r"infra-?estrutura|centrais eletricas|aguas e saneamento|gas de santa|portos|regulacao"),
    ("assistência, trabalho e habitação", r"assistencia social|desenvolvimento social"),
    ("cultura, turismo e esporte", r"cultura|turismo|esporte"),
    ("meio ambiente e defesa civil", r"meio ambiente|defesa civil"),
    ("gestão (administração, fazenda, planejamento, governo)",
     r"administracao|fazenda|planejamento|governador|casa civil|controladoria|procuradoria|comunicacao"
     r"|previdencia|escola de governo|informatica|desenvolvimento regional|regiao metropolitana"),
]

# ---------------------------------------------------------------- governos (item 5 e 6)
# Fatos políticos NÃO saem dos PPAs: tudo marcado [verificar] (fonte a conferir: TRE-SC/TSE).
# Órgão coordenador do PPA: informação da SEF repassada pelo Andrey.
GOVERNOS = pd.DataFrame([
    ("2004-2007", 2003, "Luiz Henrique da Silveira (PMDB), 1º mandato [verificar]", "Planejamento"),
    ("2008-2011", 2007, "Luiz Henrique da Silveira (PMDB), 2º mandato [verificar]", "Planejamento"),
    ("2012-2015", 2011, "Raimundo Colombo (DEM, depois PSD), 1º mandato [verificar]", "Fazenda"),
    ("2016-2019", 2015, "Raimundo Colombo (PSD), 2º mandato [verificar]", "Fazenda"),
    ("2020-2023", 2019, "Carlos Moisés da Silva (PSL), 1º mandato [verificar]", "Fazenda"),
    ("2024-2027", 2023, "Jorginho Mello (PL), 1º mandato [verificar]", "Fazenda"),
], columns=["periodo", "ano_elaboracao", "governo", "orgao_coordenador_ppa"])
# Tipo de transição entre PPAs consecutivos, segundo quem elaborou cada um [verificar todos]
TRANSICOES = {
    "2004-2007 → 2008-2011": "reeleição (mesmo governador) [verificar]",
    "2008-2011 → 2012-2015": "troca de governador [verificar]",
    "2012-2015 → 2016-2019": "reeleição (mesmo governador) [verificar]",
    "2016-2019 → 2020-2023": "troca de governador [verificar]",
    "2020-2023 → 2024-2027": "troca de governador [verificar]",
}


# ---------------------------------------------------------------- funções de aplicação
def sem_acento(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()


def categorias_publico(texto):
    t = sem_acento(texto)
    cats = [c for c, p in PUBLICO.items() if re.search(p, t)]
    return cats or ["outros"]


def tema_subacao(texto):
    t = sem_acento(texto)
    return [tema for tema, (inc, exc) in SUBACAO_TEMA.items() if re.search(inc, t) and not re.search(exc, t)]


def area_orgao(orgao):
    t = sem_acento(orgao)
    for area, p in AREAS:
        if re.search(p, t):
            return area
    return "sem área"
