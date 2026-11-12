# Regras de negócio

## Conceito de política industrial adotado

Política industrial é a ação de governo voltada a alterar a estrutura setorial da produção, seja realocando recursos entre setores, seja elevando a competitividade e a capacidade tecnológica de atividades específicas, com objetivo de mudança estrutural (Chang, 1994; Rodrik, 2004, 2008). Distingue-se política horizontal (atua sobre toda a economia) de vertical ou seletiva (mira setores e atividades).

No enquadramento da tese (complexidade econômica, linha Hausmann, Hidalgo e Hartmann), o interesse está na política que ajuda a economia a se diversificar em direção a atividades mais complexas: fomento à produção, inovação, tecnologia, competitividade empresarial, inserção internacional, diversificação produtiva. Política social, gestão pública, saúde, segurança e educação básica ficam de fora.

## Unidades e termos

- Período: um ciclo de PPA (2008-2011, 2012-2015, 2016-2019, 2020-2023, 2024-2027).
- Programa (ou "política"): unidade de planejamento do PPA, identificada por um código de 4 dígitos (ex: 0200). O mesmo código costuma se repetir entre períodos, às vezes com nome diferente.
- Campo (ou "seção"): parte estruturada do bloco de cada programa no PDF (nome, órgão, objetivo, justificativa, público-alvo). Campo é estrutura do documento; ser ou não ser política industrial é classificação analítica. Não misturar as duas coisas na metodologia.
- Texto analisado: objetivo + justificativa concatenados. O nome não entra na análise textual (é curto demais), só na curadoria.

## Como os programas são selecionados

1. O regex extrai TODOS os programas do Anexo Único. Ele não decide nada sobre conteúdo: usa os rótulos (PROGRAMA, OBJETIVO, JUSTIFICATIVA, PÚBLICO-ALVO) só como delimitadores.
2. A seleção é MANUAL: leitura do nome (triagem) e do objetivo (confirmação e desempate) de cada programa, aplicando o conceito acima. A justificativa não foi usada como critério de inclusão.
3. Casos de fronteira entram na lista de debate e precisam de validação do orientador.
4. Nenhuma alteração em `codigos_industria` sem confirmação do Andrey.

## Lista atual (`codigos_industria`)

```python
codigos_industria = {
    "2004-2007": ["0410", "0490", "0510", "0530", "0540", "0570", "0580", "0230", "0970"],  # numeração própria, ver equivalência abaixo
    "2008-2011": ["0200", "0210", "0230", "0250"],
    "2012-2015": ["0200", "0210", "0212", "0230", "0250", "0310", "0342", "0346"],
    "2016-2019": ["0200", "0210", "0212", "0230", "0310", "0342", "0346"],
    "2020-2023": ["0200", "0210", "0212", "0230", "0310", "0342", "0346"],
    "2024-2027": ["0200", "0210", "0230", "0310", "0342", "0353", "0354"],
}
```

### PPA 2004-2007 (adicionado em 09/11/2026)

Lista decidida pelo Andrey em 09/11/2026 (revisão futura com o léxico): 0580, 0490, 0230, 0540 (programas claros) e 0570, 0410, 0510, 0970 (equivalentes de casos em debate dos outros períodos).

Esse PPA usa OUTRA numeração de códigos. Para a continuidade, o notebook usa uma tabela de equivalência (coluna `serie`). É uma PROPOSTA, a validar com o orientador:

| Código 2004-2007 | Programa (2004-2007) | Série (equivalente nos períodos seguintes) | Confiança |
|---|---|---|---|
| 0580 | Promoção da Competitividade da Economia Catarinense | 0200 Competitividade e Excelência Econômica | alta (mesmo órgão de origem, objetivo "fomentar a atividade produtiva") |
| 0490 | Fomento à Pesquisa, Tecnologia e Inovação | 0230 INOVAR / CTI | alta |
| 0570 | Comércio Exterior e Relações Internacionais | 0212 | alta (caso em debate) |
| 0410 | Inclusão Digital | 0250 | alta (caso em debate; mesmo nome e órgão da educação) |
| 0230 | Pesquisa Agropecuária e Aquícola, Assistência Técnica e Extensão Rural e Pesqueira | 0310 Agronegócio Competitivo | média (mesma função: base tecnológica do agro) |
| 0510 | Gerenciamento de Informações para o Desenvolvimento Catarinense | 0210 Estudos, Projetos e Informações Estratégicas | média (mesmo órgão, Planejamento) |
| 0540 | Desenvolvimento da Micro e Pequena Empresa Catarinense (Pró-Emprego) | 0342 PREC | baixa (PREC cita micro e pequenas empresas, mas o escopo mudou) |
| 0970 | Desenvolvimento Regional e Municipal | série própria (0970-2004) | sem equivalente claro; objetivo muito vago |
| 0530 | Geração de Emprego e Renda | 0354 Promoção de Políticas de Trabalho, Emprego e Renda | baixa a média (função parecida; as linhas de crédito dele lembram o 0200) |

INCLUÍDO em 10/11/2026 (decisão do Andrey): 0530. Histórico: ficou fora da primeira revisão por falha na listagem. Descrição: 0530 Geração de Emprego e Renda (Secretaria do Desenvolvimento Social, Trabalho e Renda; objetivo "Aumentar postos de trabalho"). Contém linhas de crédito a empresas (80 mi) e microcrédito (10 mi), qualificação profissional e intermediação de mão de obra. Argumento a favor: equivalente ao crédito BADESC do 0200 e ao 0354 (incluído em 2024-2027). Argumento contra: política de trabalho e renda, horizontal. Também revisado e deixado de fora: 0265 Abastecimento Urbano (zona cinzenta fraca); 0340, 0350, 0360, 0370, 0372, 0373, 0375, 0390 (habitação e assistência social); 0680 (porto); 0850, 0860, 0870 (segurança).

Zona cinzenta de 2004-2007 deixada de fora por enquanto: 0226, 0212, 0235, 0200 (Agrorredes), 0215, 0214 (agro setorial), 0780 e 0710 (turismo), 0508 (parcerias de investimento). Excluídos relacionados: 0280 (metrologia, coerente com 0211), 0460 e 0502 (TI do governo), 0685, 0690 e 0695 (energia e gás).

Nomes por período (como aparecem nos PDFs; a tabela abaixo cobre 2008-2011 em diante):

| Código | 2008-2011 | 2012-2015 | 2016-2019 | 2020-2023 | 2024-2027 |
|---|---|---|---|---|---|
| 0200 | Competitividade e Excelência Econômica | idem | idem | idem | idem |
| 0210 | Estudos, Projetos e Informações Estratégicas | idem | Estudos e Projetos para o Desenvolvimento Regional | Estudos e Projetos para o Desenvolvimento Regional | Desenvolvimento Regional Integrado |
| 0212 | | Estratégias de Comércio Exterior e Relações Internacionais | Promoção e Articulação das Relações Internacionais | Promoção e Articulação das Relações Internacionais | |
| 0230 | Inovar - Fomento à Pesquisa ao Desenvolvimento e à Inovação | INOVAR - Fomento à Pesquisa, ao Desenvolvimento e à Inovação | CTI - Fomento à Ciência, Tecnologia e Inovação | idem | idem |
| 0250 | Inclusão Digital | Inclusão Digital | | | |
| 0310 | | Agronegócio Competitivo | Desenvolvimento Agropecuário e Pesqueiro | idem | idem |
| 0342 | | Revitalização da Economia Catarinense - PREC | idem | idem | idem |
| 0346 | | Tecnologia e Inovação para o Desenvolvimento Sustentável | idem | idem | |
| 0353 | | | | | Incentivo à Competitividade da Indústria, do Comércio e do Serviço |
| 0354 | | | | | Promoção de Políticas de Trabalho, Emprego e Renda |

Os nomes de 2020-2023 foram conferidos no PDF em 06/11/2026 (0212 confirmado, Casa Civil).

Observação sobre 0210 em 2020-2023: o código EXISTE no PDF ("Estudos e Projetos para o Desenvolvimento Regional", Secretaria de Estado do Desenvolvimento Econômico Sustentável, objetivo "Promover e realizar estudos e projetos visando o desenvolvimento regional", dotação fiscal de cerca de 206 milhões) e não está na lista. DECIDIDO em 06/11/2026 (Andrey): incluído em 2020-2023, para manter a continuidade nos cinco períodos. Programa genérico (estudos e projetos de desenvolvimento regional); a lista toda será revisada depois com o léxico em construção. No 2020-2023 também existem 0211 (Metrologia) e 0220 (Governança Eletrônica), ambos excluídos.

## Casos em debate (validar com o orientador)

Incluídos, mas discutíveis:
- 0250 Inclusão Digital (2008-2011, 2012-2015): mais política de inclusão digital/social que industrial em sentido estrito. Pendente de confirmação desde o início.
- 0212 Comércio exterior/relações internacionais (2012-2015, 2016-2019, 2020-2023): defensável pela ótica de complexidade (inserção internacional, diversificação exportadora), mas também classificável como política comercial separada.
- 0354 Trabalho, Emprego e Renda (2024-2027): o mais frágil dos três, é política horizontal/social. Candidato mais provável a sair num recorte estrito.

Excluídos, mas vale reconfirmar:
- 0211 Metrologia e Qualidade de Produtos e Serviços.
- 0343 Fomento à Economia Solidária.
- 0220 Governança Eletrônica / Transformação Digital (nome varia por período).

## Termos-chave do gráfico de evolução

A lista `["inovação", "competitividade", "digital", "internacional", "emprego"]` foi escolhida manualmente por interesse teórico, não derivada estatisticamente. Na metodologia, apresentar como checagem dirigida de hipóteses (deslocamento de agenda: digital para internacional/emprego), não como descoberta do algoritmo. A expansão do léxico (ver próximos passos) existe justamente para responder a essa fragilidade.
