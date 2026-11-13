"""Regras das redes (notebooks/redes_ppa.ipynb).

APROVAÇÃO PRELIMINAR do Andrey em 13/11/2026 ("aprova tudo de maneira preliminar, depois eu reviso").
Toda regra de seleção e todo limiar das redes estão aqui; o módulo scripts/redes.py só aplica.

Quatro redes:
  1. termos      lemas ligados por aparecerem na mesma frase (proximidade)
  2. programas   programas do mesmo PPA ligados pelo que dizem (objetivo + justificativa)
                 e pelo que fazem (nomes das subações)
  3. oferta e demanda   área do órgão responsável (oferta) x categoria de público-alvo (demanda)
  4. genealogia  programa de um PPA ligado ao do PPA seguinte pelo texto e pelas subações herdadas
"""
import re

from ppa_inteiro_listas import PUBLICO, sem_acento

# ------------------------------------------------------------------ rede 1: termos
TERMOS_MIN_FRASES = 4      # lema entra na rede se aparece em pelo menos 4 frases (corpus inteiro)
COOC_MIN = 2               # ligação só se os dois lemas aparecem juntos em pelo menos 2 frases
# Proximidade entre dois lemas i e j: phi = C_ij / max(N_i, N_j), em que C_ij é o nº de frases com
# os dois e N_i o nº de frases com i. É o mínimo das duas probabilidades condicionais (a mesma
# forma da proximidade entre produtos do espaço de produtos), e por isso não infla palavras
# muito frequentes.
GRAU_MEDIO_DESENHO = 4     # rede desenhada = árvore geradora máxima + ligações mais fortes até grau médio 4
SEMENTE = 42
BOOTSTRAP_TERMOS = 50      # reamostragens de frases para medir a estabilidade das comunidades
ALVOS = ["inovação", "competitividade", "tecnologia", "empresa", "indústria", "tecnológico",
         "produtivo", "emprego"]

# ------------------------------------------------------------------ rede 2: programas
FORMATO_DF = 0.20          # lema presente em mais de 20% dos programas do PPA = palavra de formato, sai
KNN = 3                    # cada programa ligado aos 3 mais parecidos do mesmo PPA
SIM_MIN = 0.10             # ... desde que o cosseno seja pelo menos 0,10
PERM_PROGRAMAS = 2000      # permutações para a homofilia e o teste de Mantel

# ------------------------------------------------------------------ rede 3: oferta e demanda
# Público-alvo ampliado: as 7 categorias aprovadas em 13/11 + 4 propostas (setor público,
# estudantes e escolas, grupos vulneráveis, sem definição). Ajustes depois de ver os casos:
#   - "micro e pequenas empresas" sem o "pequen" solto (pegava "pequenos agricultores");
#   - erros de digitação do PDF: "pode legislativo", "promoteres";
#   - clientes de Celesc e SCGás, moradores, comunidades e gerações futuras em sociedade em geral.
PUBLICO_REDE = {
    "empresas": PUBLICO["empresas"],
    "micro e pequenas empresas": r"\bmicro|pequenas? (?:e medias? )?empresas|empreendedores? individua"
                                 r"|pequenas agroindustrias",
    "trabalhadores": PUBLICO["trabalhadores"],
    "produtores rurais": PUBLICO["produtores rurais"],
    "municípios": PUBLICO["municípios"],
    "instituições de pesquisa": PUBLICO["instituições de pesquisa"],
    "setor público": r"servidor|\borgaos?\b|gestor|administra|\bpoder|\bpode legislativo|legislativ|judiciari"
                     r"|agentes? public|tesouro|magistrad|promot|conselheir|colaboradores|dirigentes"
                     r"|titulares|profissionais (?:da|de) (?:seguranca|saude|educacao)|governo|mpsc|detran"
                     r"|equipe tecnica|pension|beneficiadas definidas por lei",
    "estudantes e escolas": r"estudante|aluno|professor|escola|escolar|educacao|ensino|jovens|criancas de",
    "grupos vulneráveis": r"vulner|baixa renda|carente|hipossuficiente|carcer|apenado|infrator|infracional"
                          r"|necessidades especiais|deficien|sem moradia|necessitem de habitacao"
                          r"|seguranca alimentar|criancas e adolescentes|minori|renda insuficiente"
                          r"|eenda insuficiente|nao alfabetizada|sem terra|desprovidas",
    "sem definição": r"s/defini|n/definido|reserva de contingencia|que se enquadram",
    "sociedade em geral": PUBLICO["sociedade em geral"] + r"|client|morador|comunidade|gerac|famili",
}
# Precedência: o público específico vale sobre o genérico. "sociedade em geral" só conta se nenhuma
# outra categoria casar; "micro e pequenas empresas" substitui "empresas" quando as duas casam.
# O valor de um programa com mais de uma categoria é dividido em partes iguais entre elas.


# Exceções explícitas (texto do público-alvo sem acento -> categorias). Comunicação institucional do
# governo (Casa Civil 2020-2023, 0810 Comunicação do Poder Executivo 2024-2027) declara "Cidadãos,
# investidores, turistas e consumidores": o "investidores" puxaria o programa para empresas.
EXCECOES_PUBLICO = {
    "cidadaos, investidores, turistas e consumidores": ["sociedade em geral"],
}


def categorias_publico_rede(texto):
    t = sem_acento(texto)
    if t.strip(" .") in EXCECOES_PUBLICO:
        return list(EXCECOES_PUBLICO[t.strip(" .")])
    cats = [c for c, p in PUBLICO_REDE.items() if c != "sociedade em geral" and re.search(p, t)]
    if "micro e pequenas empresas" in cats and "empresas" in cats:
        cats.remove("empresas")
    if not cats and re.search(PUBLICO_REDE["sociedade em geral"], t):
        cats = ["sociedade em geral"]
    return cats or ["outros"]


# Peso da ligação oferta -> demanda: valor das subações do programa SEM pessoal e emendas
# (padrões de orcamento_ajustado.py), em % do total do PPA também sem pessoal e emendas.
MIN_LIGACAO_DESENHO = 0.10   # no desenho, só ligações com pelo menos 0,10% do PPA

# ------------------------------------------------------------------ rede 4: genealogia
HERANCA_MIN = 0.20   # A é "pai" de B (PPA seguinte) se B herda de A pelo menos 20% do valor das
                     # subações OU 20% dos lemas (frases com similaridade de 0,9 ou mais, como no
                     # item 5 da análise do PPA inteiro)
SUBACAO_NOME_MIN = 0.6   # subação herdada = mesmo código de 6 dígitos E nome parecido (SequenceMatcher
                         # >= 0,6 no nome sem acento). Motivo (conferido em 13/11/2026): de 2004-2007 para
                         # 2008-2011 os códigos foram renumerados e só 1% dos códigos repetidos tem nome
                         # parecido (coincidência de número); de 2012 em diante, 86% a 98% têm.
# Mesmo dono: coeficiente de sobreposição |A ∩ B| / min(|A|, |B|) de pelo menos 0,5 entre as palavras
# distintivas dos nomes dos órgãos (sem "secretaria", "estado", artigos, preposições, a sigla depois de
# " - " e a palavra genérica "desenvolvimento"; hífen removido, "infra-estrutura" = "infraestrutura").
# Assim renomeações contam como o mesmo dono ("Agricultura e da Pesca" -> "Agricultura - SAR";
# "Desenvolvimento Econômico" -> "Desenvolvimento Econômico Sustentável"), e trocas reais não
# ("Desenvolvimento Econômico Sustentável" -> "Agência de Fomento"; "Educação, Ciência e Tecnologia"
# -> "Desenvolvimento Econômico"). Caso ambíguo conhecido: "Desenvolvimento Sustentável" (2008-2011)
# e "Desenvolvimento Econômico Sustentável" (2012 em diante) contam como o mesmo dono [verificar].
DONO_SOBREPOSICAO = 0.5
_VAZIAS = {"secretaria", "estado", "de", "da", "do", "das", "dos", "e", "a", "o", "s", "sa", "santa", "catarina",
           "sc", "desenvolvimento"}


def tokens_orgao(nome):
    nome = sem_acento(str(nome).split(" - ")[0]).replace("-", "")
    return {w for w in re.findall(r"[a-z]+", nome) if w not in _VAZIAS and len(w) > 2}


def mesmo_dono(a, b):
    ta, tb = tokens_orgao(a), tokens_orgao(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / min(len(ta), len(tb)) >= DONO_SOBREPOSICAO
