# Achados até agora

Situação em 10/11/2026, com a lista de `codigos_industria` atual: 6 períodos (2004-2007 a 2024-2027), 42 programas (9, 4, 8, 7, 7 e 7 por período). 0210 incluído em 2020-2023 (06/11), 2004-2007 incluído com 8 programas (09/11) e 0530 acrescentado em 2004-2007 (10/11). Se a lista mudar, os números mudam. Algumas seções abaixo foram calculadas antes do 0530 e estão marcadas; as diferenças nelas são pequenas, exceto onde indicado.

## Continuidade dos programas

O PPA 2004-2007 usa outra numeração de códigos. A tabela agrupa por "série", com uma equivalência PROPOSTA para 2004-2007 (ver `regras-de-negocio.md`), ainda a validar com o orientador.

| Série | Nome (mais recente) | Períodos | Qtd |
|---|---|---|---|
| 0200 | Competitividade e Excelência Econômica | todos | 6 |
| 0210 | Desenvolvimento Regional Integrado | todos | 6 |
| 0230 | CTI - Fomento à Ciência, Tecnologia e Inovação | todos | 6 |
| 0310 | Desenvolvimento Agropecuário e Pesqueiro | 2004-07 e 2012-15 a 2024-27 | 5 |
| 0342 | Revitalização da Economia Catarinense - PREC | 2004-07 e 2012-15 a 2024-27 (equivalência de 2004-07 incerta) | 5 |
| 0212 | Promoção e Articulação das Relações Internacionais | 2004-07, 2012-15, 2016-19, 2020-23 | 4 |
| 0250 | Inclusão Digital | 2004-07, 2008-11, 2012-15 | 3 |
| 0346 | Tecnologia e Inovação para o Desenvolvimento Sustentável | 2012-15, 2016-19, 2020-23 | 3 |
| 0353 | Incentivo à Competitividade da Indústria, do Comércio e do Serviço | 2024-27 | 1 |
| 0354 | Promoção de Políticas de Trabalho, Emprego e Renda | 2004-07 (0530, equivalência incerta) e 2024-27 | 2 |
| 0970-2004 | Desenvolvimento Regional e Municipal | 2004-07 | 1 |

Leitura: núcleo de três programas (competitividade, estudos e desenvolvimento regional, ciência e tecnologia) atravessando 20 anos; mudança de composição nas pontas da série. A continuidade de 2004-07 depende da tabela de equivalência, que é uma proposta, não um dado.

## Reaproveitamento textual

Vários programas repetem objetivo e justificativa quase palavra por palavra entre ciclos (0200 é o caso mais claro: o texto de 2008-2011 reaparece em 2012-2015). Parte do discurso é herdada, não reescrita. Isso explica parte da similaridade alta entre períodos vizinhos.

## TF-IDF (unigramas, top termos)

- 2004-2007: participação, social, rural, disponibilizar, tecnologia, desenvolvimento, estimular, criação, informação. Atenção: são só 8 programas e textos curtos (mediana de 15,5 lemas por programa, contra 35 a 48 nos outros períodos). "participação" (0,48) vem de poucas ocorrências em 3 textos, com destaque para o 0570 (participação das empresas no mercado internacional). Não ler como vocabulário dominante do período.
- 2008-2011: acesso, rural, população, tecnológico, informação, digital, pescador. Vocabulário de inclusão e acesso, puxado pelo 0250.
- 2012-2015: inovação, acesso, tecnológico, catarinense, economia, rural, empresa. Transição.
- 2016-2019: inovação, catarinense, tecnológico, economia, empresa, conhecimento, produto, empreendedor, negócio. Inovação e ambiente de negócios.
- 2020-2023: inovação, internacional (empatados), empresa, catarinense, econômico, tecnológico, desenvolvimento, pesquisa. Ganho de inserção internacional. Com o 0210 entram "promoção" e "visar" no top 15 (ruído de um programa genérico).
- 2024-2027: catarinense, competitividade, econômico, estimular, desenvolvimento, capacitação, emprego. Competitividade e emprego. "setor" saiu do top 15 com a inclusão do 0210 em 2020-2023 (efeito do IDF).

Nota: como o IDF é calculado sobre todos os períodos, mudar a lista de um período altera levemente os pesos dos outros (2ª ou 3ª casa decimal). Com o 2004-2007 incluído, o top 10 dos outros períodos mudou em no máximo um termo cada: 2008-11 troca "pescador" por "base", 2016-19 troca "desenvolvimento" por "empreendedor", 2020-23 troca "social" por "buscar", 2024-27 troca "capacitação" por "qualificação" (variantes da mesma ideia), 2012-15 não muda. A leitura das progressões abaixo se mantém.

Progressão: inclusão/acesso rural, depois inovação/tecnologia, depois internacional/empresa, depois competitividade/emprego. O 2004-2007 não acrescenta um estágio claro: seu vocabulário é tecnologia, rural, social e participação, mas com poucos textos e muito curtos.

## Evolução de termos-chave

- "inovação", "competitividade" e "digital" têm peso ZERO em 2004-2007. Duas leituras, que o dado atual não separa: (a) o vocabulário ainda não era usado; (b) os textos de 2004-2007 são curtos e genéricos (ex.: objetivo do 0580 é "Fomentar a atividade produtiva no estado."; o do 0490 é "Estimular a criação e utilização de novas tecnologias."). O 0410 Inclusão Digital de 2004-2007 fala em "computador" e "rede mundial de computadores", sem usar a palavra "digital": um caso concreto de tema presente com vocabulário diferente, o que justifica expandir o léxico (ver ensaios de léxico).
- "digital" alto só em 2008-2015 e depois some (acompanha o fim do 0250).
- "internacional" ganha peso nos períodos com 0212, pico em 2020-2023.
- "emprego" forte só em 2024-2027 (puxado pelo 0354, que está em debate).

Atenção: parte dessas trajetórias é efeito direto de qual programa entrou ou saiu da lista. Separar "mudança de discurso" de "mudança de composição da amostra" é uma ressalva necessária.

## Similaridade de cosseno

De 2008-2011 em diante: períodos vizinhos mais parecidos entre si do que períodos distantes (0,76; 0,90; 0,81; 0,70), mudança gradual, coerente com o reaproveitamento textual (pico de 0,90 entre 2012-15 e 2016-19).

Com o 2004-2007: ele é o período mais isolado (0,29 com 2008-11; 0,35 com 2012-15 e 2016-19; 0,44 com 2020-23; 0,42 com 2024-27). A transição 2004-07 para 2008-11 seria a maior ruptura da série, mas a leitura exige cautela: os textos de 2004-07 são curtos e esparsos (menos de metade do tamanho dos demais), o que reduz o cosseno por construção, e o 2004-07 fica mais parecido com 2020-24 do que com 2008-11, o que sugere vocabulário genérico comum e não continuidade ou ruptura de discurso. Não afirmar ruptura pré-2008 com base só nisso.

## LDA

5 tópicos, por programa, agregados por período. Um tópico mostrou formato em U ao longo do tempo, mas com vocabulário misturado e corpus pequeno (poucos programas por período). Tratar como hipótese, não como achado.

Instabilidade confirmada em 06/11/2026: ao acrescentar UM programa (0210 em 2020-2023), os tópicos mudaram de composição e de numeração, e as proporções médias por período mudaram bastante, inclusive em períodos que não receberam programa novo (ex.: 2008-2011). A trajetória em U registrada antes não se reproduz com a mesma leitura. Não usar o LDA atual como resultado na monografia sem um procedimento de estabilidade (várias sementes, comparação de tópicos).

Medida de estabilidade (09/11/2026): Jaccard médio dos 10 termos de cada tópico entre a semente 42 e as sementes 1 a 10 (1,00 = tópicos idênticos): 0,42 com 5 períodos (mín 0,33, máx 0,54) e 0,29 com 6 períodos (mín 0,23, máx 0,38). Ou seja, mesmo sem mudar o corpus, trocar a semente já muda a maior parte do vocabulário dos tópicos, e acrescentar o 2004-2007 (textos curtos) piora. O LDA atual não sustenta interpretação.

## Circularidade dos termos-chave (09/11/2026)

Script: `scripts/circularidade.py`; figura `saidas/circularidade_termos_chave_vs_controles.png`; tabelas `saidas/circularidade_resumo.csv` e `circularidade_ranking.csv` (versões `_dedup` sem textos idênticos). Três testes por termo, lexical (taxa por 1000 lemas) e semântica (cosseno com vetores do spaCy, termo removido do texto): permutação do período dos programas, comparação com 25 termos de controle de frequência mais próxima, bootstrap de programas dentro do período.

Resultado (todos os programas / sem duplicatas):
- competitividade: único termo cuja trajetória excede claramente o acaso. Lexical: p de permutação 0,002 / 0,011; acima de 96% / 84% dos controles; tendência crescente com salto em 2024-27 (29 por mil lemas contra 7 a 10 antes; IC 95% de 2024-27 quase não toca os dos períodos anteriores). Está espalhada por 15 programas, não vem de um só.
- digital: lexical frequente demais para testar (4 ocorrências, todas no 0250, em 2008-11 e 2012-15). Semântica: p 0,007 / 0,041, queda desde 2008-11, mínimo em 2024-27. Indício, não prova.
- inovação, internacional, emprego: trajetória NÃO distinguível do que um sorteio de programas produziria (p de permutação de 0,40 a 0,91). Inovação é termo persistente (1º lugar no vocabulário em 2012-15, 2016-19 e 2020-23; 31 ocorrências, concentradas no 0346 e no 0230), sem tendência. O pico de "internacional" em 2020-23 vem sobretudo de um programa (0212: 6 das 18 ocorrências). O pico de "emprego" em 2024-27 vem de 3 ocorrências, 2 delas no 0354 (o caso em debate).
- Correção para 10 testes (limiar 0,005): só competitividade lexical passa na versão completa.

Leitura: a escolha dos termos não produz sozinha o resultado de competitividade, mas as narrativas de "internacional em 2020-23" e "emprego em 2024-27" dependem de 1 a 3 programas e não devem ser apresentadas como mudança de discurso. Com o corpus atual (41 programas, 160 a 326 lemas por período) o teste tem pouco poder.

## Menções a tipos de política (09/11/2026)

Script: `scripts/mencoes.py`; tabela `saidas/mencoes_politicas.csv` (uma linha por menção, com frase, período, programa, campo, verbos da frase e marca de frase repetida de período anterior). Busca nos textos de objetivo e justificativa dos programas selecionados.

- Poucas menções: 18 (14 frases distintas) em 41 programas.
- APL / arranjo produtivo: zero. Incentivo fiscal: zero. Crédito: uma menção (0540 de 2004-2007, "concessão de linhas de crédito a microempresa").
- Cluster / polo: só o 0342 (PREC), 2012-2015 a 2024-2027, com texto repetido ("fortalecimento de polos produtivos já existentes, criação de polos econômicos em regiões de baixo IDH").
- Instrumentos de inovação: 0230, 2008-2011 a 2016-2019 (centros de inovação, incubadoras, condomínios empresariais).
- Educação tecnológica / qualificação: só em 2024-2027 (0353 e 0354).
- Pequeno produtor rural / agricultores: 2004-2007, 2008-2011, 2012-2015 e 2024-2027.
- Nos PDFs inteiros (todos os programas, todos os campos), APL aparece de 0 a 6 vezes por PPA e incentivo fiscal de 1 a 5. "Crédito/financiamento" aparece de 27 a 163 vezes, mas em boa parte são tabelas orçamentárias (fonte de recursos), não política.
- Leitura: a hipótese do Dominik sobre APL, clusters e instrumentos concretos não encontra suporte nos campos objetivo e justificativa. Esses instrumentos, se existem, tendem a estar nas ações e subações (campo não extraído) ou em programas não selecionados. Próximo passo possível: extrair as ações dos programas selecionados e repetir a busca.
- Extração: no 0310 de 2024-2027 o "Público Alvo:" ficava dentro da justificativa (1 de 41 programas). Corrigido em 09/11/2026 no `processa_ppa` (corte da justificativa nesse rótulo). Efeito: a busca de menções passou de 18 para 17 (a menção a agricultores de 2024-2027 vinha daí). As análises sobre o texto lematizado não mudaram, porque as palavras contaminadas estavam com inicial maiúscula e o spaCy as tratou como nome próprio, descartado pelo filtro de classe gramatical.

## Instrumentos nas ações e subações (09/11/2026)

Script: `scripts/blocos_programas.py`; tabela `saidas/mencoes_blocos.csv`. Busca no restante do bloco de cada programa selecionado (público-alvo, ações, subações, indicadores), com as mesmas categorias do `mencoes.py`. Os instrumentos que não aparecem em objetivo e justificativa aparecem aqui.

- Crédito é o instrumento mais persistente: linhas do BADESC no 0200 em todos os períodos de 2008-2011 a 2024-2027 (apoio creditício a micro e pequenas, a médias e grandes empresas, ao microcrédito e aos municípios). Em 2004-2007, linha de crédito a micro e pequena empresa (0540) e empréstimos (0580). Em 2020-2023 e 2024-2027 surge o "Microcrédito Juro Zero" (0342 e 0353).
- APL aparece como ação de 2004-2007 a 2012-2015 (0490 pesquisa em arranjos produtivos; 0580 estruturação e organização de APLs; 0200 desenvolvimento de APL; 0310 estruturação de APLs pelo FDR; 0342 diagnóstico de potencialidades regionais) e praticamente some depois (nenhuma em 2016-2019; uma menção em 2024-2027).
- Incubadoras, parques e centros de inovação: concentrados de 2004-2007 a 2016-2019 (0490, 0230, 0346); em 2020-2027 restam ações genéricas de "empresa de base tecnológica".
- Polos: implantação de polos e parques tecnológicos (0230, 2008-2011), polo tecnológico regional (0342, 2012-2015), polo de tecnologia nas indústrias (0346, 2016-2019).
- Qualificação: majoritariamente capacitação de gestores públicos e de agricultores e pescadores (EPAGRI, 0310). Educação tecnológica no sentido de ensino técnico praticamente não aparece.
- Incentivo fiscal: zero também nos blocos. Hipótese a checar: incentivos fiscais são renúncia de receita e não programas orçamentários, por isso não aparecem no PPA (provavelmente estão no demonstrativo de renúncia da LDO).
- Cautelas: a busca é por linha e por expressão; linhas de indicadores (a partir de 2020-2023) e de subações regionais repetidas foram agrupadas, mas a contagem é de presença, não de valor orçado. Os valores das ações estão nas mesmas linhas e podem ser extraídos depois.

Leitura (revista em 10/11/2026 com os valores, ver abaixo): APL, incubadoras e parques recuam depois de 2015-2019. O crédito persiste como ação em todos os períodos, mas NÃO se amplia: seu peso relativo cai (ver valores orçados).

## Valores orçados dos instrumentos (10/11/2026)

Script: `scripts/valores_acoes.py`; saídas `saidas/valores_subacoes.csv` e `saidas/valores_instrumentos.csv`. Validação: a soma das subações de cada PPA quadrienal bate com o "TOTAL GERAL" oficial (2012-15: 127,76 contra 127,36 bi; 2016-19: 136,78 contra 136,78; 2020-23: 186,58 contra 186,41; 2024-27: 266,31 contra 266,31). Em 2004-2007 e 2008-2011 os valores do anexo são de UM ano (cabeçalhos "2007/2007" e "2011/2011") e não há total oficial no arquivo para validar. Valores nominais, sem correção pela inflação; por isso a comparação entre períodos usa participações.

Participação no valor total do PPA:
| Período | Programas selecionados | Crédito | APL | Incubadoras, parques, base tecnológica |
|---|---|---|---|---|
| 2004-2007 (1 ano) | 3,07% | 0,81% | 0,02% | 0,01% |
| 2008-2011 (1 ano) | 3,16% | 1,27% | 0,00% | 0,01% |
| 2012-2015 | 2,08% | 1,12% | 0,06% | 0,04% |
| 2016-2019 | 1,78% | 0,98% | 0,00% | 0,02% |
| 2020-2023 | 2,41% | 0,71% | 0,00% | 0,00% |
| 2024-2027 | 2,50% | 0,43% | 0,01% | 0,06% |

- Os programas selecionados somam de 1,8% a 3,2% do valor do PPA: política industrial é uma fatia pequena do plano.
- Crédito (quase todo BADESC, no 0200) cai de 1,1-1,3% do PPA (2008-2015) para 0,4% (2024-27). Em valores nominais fica estável (1,43 bi em 2012-15; 1,15 bi em 2024-27), o que significa queda real.
- O crescimento do valor dos programas selecionados em 2020-2027 vem de itens que não são instrumentos de política industrial: folha de pessoal da EPAGRI no 0310 (1,48 bi em 2020-23; 2,0 bi em 2024-27), emendas parlamentares impositivas do Fundo Social no 0210 (0,31 bi; 1,43 bi) e o programa emergencial Covid-19 no 0342 (0,19 bi em 2020-23). Isso pesa na discussão sobre manter o 0210 na lista.
- APL e incubadoras têm valores pequenos em todos os períodos (dezenas de milhões). Em 2024-2027 aparecem 129 mi para projetos de empresas de base tecnológica e inovação (0230) e 38 mi para infraestrutura e inovação de empresas e APLs com recursos do Fundo Social (0200).
- Em 2004-2007 as linhas de crédito a empresas (80 mi) e microcrédito (10 mi) estão no programa 0530 Geração de Emprego e Renda, incluído em 10/11/2026. Com ele, o crédito de 2004-2007 fica em 0,81% do PPA e a série completa mostra queda: 0,8-1,3% (2004-2015) para 0,4% (2024-27). Figura: `saidas/instrumentos_participacao_ppa.png`.

## Tópicos do LDA sobre campos (10/11/2026; SUPERADO, ver nota)

NOTA (10/11/2026, depois do 0530): ao acrescentar um único programa, a clusterização de termos mudou por inteiro (outros agrupamentos, ARI 0,46) e os tópicos abaixo deixaram de existir na forma descrita. A estabilidade entre sementes do LDA sobre campos continua alta (0,91 a 0,97), mas a solução não é robusta a pequenas mudanças no corpus. Conclusão: campos semânticos e LDA sobre campos não sustentam interpretação substantiva com este corpus. A figura de campos foi retirada dos resultados. O texto abaixo fica só como registro.

`scripts/clusters_termos.py`, 4 tópicos sobre os 12 campos semânticos; `saidas/lda_campos_por_periodo.csv`. Estabilidade de cada tópico entre 10 sementes (cosseno dos tópicos casados): T0 0,98; T1 0,81 (mín 0,63); T2 0,96; T3 0,94. Os tópicos podem ser lidos, com a ressalva de que dependem de UMA solução de clusters (ARI 0,39 entre sementes do KMeans).

- T0 "empresa e empreendedorismo" (empresa, economia, produtivo, empreendedor; catarinense, pequeno, individual): estável no tempo (0,15 a 0,34).
- T1 "economia e escala territorial" (econômico, internacional, nacional, regional, mundial): sobe de 0,07-0,19 (2004-2019) para 0,28-0,31 (2020-2027). Tópico menos estável.
- T2 "planejamento e projetos" (desenvolvimento, conhecimento, projeto, estudo): cai de 0,24-0,25 (2004-2011) para 0,13 (2024-27).
- T3 "inovação, tecnologia e acesso" (inovação, tecnológico, competitividade, tecnologia; acesso, informação, serviço): pico em 2008-2011 (0,54) e queda até 0,25 em 2024-2027.
- Cautela: o campo C05 junta "inovação" (estável no teste de circularidade) e "competitividade" (em alta); a queda de T3 vem mais de "acesso/informação/digital" e de inovação do que de competitividade. Campos misturam termos com trajetórias diferentes.

## Campos semânticos e estabilidade do LDA (09/11/2026)

Script: `scripts/clusters_termos.py`; saídas `saidas/clusters_termos.csv` e `saidas/clusters_por_periodo.csv`. Os 245 termos de frequência 2 ou mais foram agrupados em 12 clusters por KMeans sobre vetores do spaCy.

- A estrutura de clusters é fraca: silhueta de 0,09 a 0,14 e ARI médio de 0,39 entre sementes. Parte dos clusters agrupa por classe gramatical (verbos de promoção, adjetivos de escala), não por tema.
- Clusters com sentido temático: inovação, tecnologia, competitividade, qualidade, diversificação, pesquisa (C05); empresa, economia, empreendedor, emprego, renda, agropecuário (C08); acesso, informação, digital, serviço (C10).
- Participação por período: C05 sobe de 8,5% (2004-07) para 12,0% (2024-27); C08 de 12,3% para 17,9%; C10 cai de 15,4% (2008-11) para 3,8% (2024-27). Coerente com a leitura anterior (acesso e digital perdem espaço; economia e competitividade ganham), com a cautela de composição da amostra e textos curtos.
- LDA sobre campos é mais estável que LDA sobre palavras (cosseno médio dos tópicos casados entre sementes): 3 tópicos 0,81 contra 0,74; 4 tópicos 0,92 contra 0,74; 5 tópicos 0,91 contra 0,69. Parte do ganho é mecânica (12 variáveis em vez de 200) e depende de uma solução de clusters ela mesma moderadamente instável. Ainda não se examinou o conteúdo dos tópicos do LDA sobre campos.

## Composição x reescrita (10/11/2026)

Script: `scripts/composicao_discurso.py`; figura `saidas/composicao_vs_reescrita.png`; tabelas `saidas/composicao_transicoes.csv`, `composicao_series.csv`, `composicao_termos_chave.csv`. Para cada transição entre períodos, separa o efeito de programas que entram e saem (composição) do efeito de programas que continuam e mudam o texto (reescrita), com distância de cosseno sobre TF-IDF. As duas parcelas não são aditivas; indicam qual força domina.

| Transição | Mudança total | Composição | Reescrita | Leitura |
|---|---|---|---|---|
| 2004-07 → 2008-11 | 0,77 | 0,37 | 0,82 | reescrita quase total dos mesmos programas (similaridade da mesma série 0,04 a 0,25); parte é formato, pois os textos de 2004-07 são curtos |
| 2008-11 → 2012-15 | 0,30 | 0,21 | 0,06 | composição: entram 0212, 0310, 0342, 0346; quem continua copia o texto (0200 0,95; 0210 e 0250 1,00) |
| 2012-15 → 2016-19 | 0,17 | 0,06 | 0,13 | pouca mudança; reescrita do 0230 |
| 2016-19 → 2020-23 | 0,30 | 0,00 | 0,30 | só reescrita: mesmos programas, texto novo (0200 0,30; 0230 0,24; 0212 0,48) |
| 2020-23 → 2024-27 | 0,43 | 0,20 | 0,22 | as duas: entram 0353 e 0354, saem 0212 e 0346, e quem continua reescreve |

- 7 de 31 pares de períodos consecutivos da mesma série têm texto idêntico (herança literal), concentrados entre 2012 e 2020.
- De onde vem a variação dos termos-chave: o pico de "internacional" em 2020-23 vem de REESCRITA dentro dos programas que continuam (de 3 para 8 ocorrências, sobretudo o 0212). A queda de "inovação" em 2024-27 vem de COMPOSIÇÃO (saída do 0346, que tinha 5 ocorrências). A alta de "competitividade" em 2024-27 vem das duas (continuam: 3 para 5; entram: 3, do 0353). "Emprego" em 2024-27 vem de composição (3 ocorrências dos programas que entram).
- Implicação: "mudança de discurso" e "mudança de composição" se alternam ao longo da série. Os resultados por termo precisam dizer qual das duas está em jogo.

## Termos distintivos início x fim (10/11/2026)

Script: `scripts/termos_distintivos.py` (log-odds com prior de Dirichlet informativo, Monroe, Colaresi e Quinn, 2008); figura `saidas/termos_distintivos_inicio_fim.png`; tabela `saidas/termos_distintivos.csv`. Início = 2004-2011 (13 textos distintos, 314 lemas); fim = 2020-2027 (14 textos, 601 lemas).

- Só um termo passa de |z| > 1,96: "rural" (típico do início; 6 ocorrências contra 0).
- Direção coerente com o TF-IDF, mas sem significância: início com rural, informação, participação, acesso, pescador, população (inclusão e acesso); fim com competitividade (1 para 11, z = 1,33), agropecuário, setor, negócio, individual, polo, internacional, investimento, empreendedor (empresa, setor e competitividade).
- Robusto à força do prior: o top 15 de cada lado coincide em 30 de 30 termos (prior 100) e 29 de 30 (prior 2000).
- Leitura: com 27 textos curtos, o corpus não tem poder para afirmar diferenças lexicais significativas entre as pontas da série, exceto "rural". Serve como descrição, não como teste.

## Índice por dimensão do léxico (12/11/2026, léxico VALIDADO pelo Andrey: `saidas/lexico_validado.csv`)

Scripts: `scripts/indice_lexico.py` (taxa por dimensão, bootstrap, permutação e 1000 léxicos aleatórios de mesma frequência) e `scripts/corpus_acoes.py` (corpus complementar com os nomes das ações e subações, 3.349 lemas contra 1.530 de objetivo e justificativa). Léxico: `saidas/lexico_validado.csv` (20 termos aceitos em 5 dimensões; os 9 "talvez" ficam fora). Rodado com `--lexico ../saidas/lexico_validado.csv`. Figuras: `saidas/indice_lexico_programas.png` e `saidas/indice_lexico_acoes.png`.

- Objetivo e justificativa: "competitividade e produção" (competitividade, competitivo, produtividade, diversificação) é a única dimensão que excede o acaso (p de permutação 0,004) e os léxicos aleatórios (acima de 99,7%). Cresce de 0 (2004-07) para 14-22 por mil (2008-2023) e 44 por mil (2024-27). O resultado do termo isolado se mantém com o léxico expandido.
- Inovação e tecnologia, inserção internacional e trabalho e renda: sem diferença do acaso. "Digital" ficou só com "computador" (a semente foi marcada "talvez"): não interpretável.
- Léxico inteiro: sobe de forma monotônica (77 para 127 por mil; ρ = 1,00, p = 0,002), mas quase todo o salto é 2004-07 para 2008-11, período de textos curtos; acima de só 34% dos léxicos aleatórios em amplitude.
- Ações e subações: "competitividade e produção" quase não aparece (5 ocorrências, nenhuma depois de 2015). A competitividade cresce no discurso (objetivo e justificativa), mas não no nome das ações: indício de distância entre discurso e instrumento. Trabalho e renda sobe nas ações em 2020-27 (24 por mil) e inserção internacional cai, ambos sem significância.
- Armadilha corrigida no corpus de ações: nomes em Título eram lidos como nome próprio pelo spaCy e descartados; o texto das ações é passado em minúsculas antes de lematizar.

## Classificador de texto para conferir a curadoria (12/11/2026)

Inspirado em Juhász, Lane, Oehlsen e Pérez (2025), "Measuring Industrial Policy: A Text-Based Approach". Script `scripts/classificador.py`; saídas `saidas/programas_todos.csv` (514 programas distintos dos 6 PPAs), `saidas/classificador_programas.csv` (probabilidade fora da amostra por programa), `saidas/classificador_palavras.csv`. TF-IDF de unigramas e bigramas + regressão logística L1 com pesos balanceados, treinada com a seleção manual (42 positivos); validação cruzada por série (o mesmo programa em outro período nunca está no treino). Não é regressão econométrica.

- Desempenho fora da amostra: precisão 0,38, revocação 0,48, F1 0,42; precisão média 0,44 contra 0,08 do acaso. O modelo aprende algo (5 vezes o acaso), mas não substitui a curadoria manual: com 42 positivos, textos curtos e texto copiado entre ciclos, serve como ferramenta de revisão.
- Palavras que mais pesam (30 termos, todos positivos): tecnológico, empresa, internacional, econômico, "fomentar atividade", produtivo, conhecimento, inovação. Parte é artefato de programas específicos ("exclusão", "pescador" vêm do 0250; "estudo projeto" do 0210).
- Selecionados com probabilidade baixa: todos os de 2004-2007 (textos curtos, o equivalente à classe "informação insuficiente" do artigo), 0210 (genérico), 0212 e 0250 (casos em debate). Coincide com a lista de casos frágeis já conhecida.
- Não selecionados com probabilidade alta, para revisão: 0530 "Pró-Emprego e Renda" de 2008-2011 (objetivo "ampliar a geração de empregos"; é a continuação do 0530 de 2004-2007, incluído, e parente do 0354 de 2024-2027, incluído: questão de coerência); 0101 "Acelera Santa Catarina" (2012-2023; objetivo cita "competitividade das empresas catarinenses"); 0204 "Missões, Recepções e Eventos Internacionais" (2016-2019; promoção internacional do estado, parente do 0212). Falsos positivos evidentes: 0619 "Elaborar estudos e projetos" de infraestrutura (parecido com o 0210, o que reforça que o 0210 é genérico), 0932 Transformação Digital do Tribunal de Justiça, programas de segurança e saúde.
- Proporção de programas previstos como política industrial por período (10, 5, 8, 9, 11, 10) fica próxima da seleção manual (9, 4, 8, 7, 7, 7); o modelo sugere um pouco mais em 2020-2027.

## Cenário de curadoria: antes x depois (12/11/2026)

Script `scripts/cenario_curadoria.py` (+ `figura_cenario.py`); comparação em `saidas/cenario_curadoria_comparacao.csv`, figura `saidas/cenario_antes_depois.png`. A lista oficial NÃO mudou: o cenário acrescenta os 8 programas apontados pelo classificador (0530 Pró-Emprego e Renda em 2008-2019, 0101 Acelera SC em 2012-2027, 0204 Missões Internacionais em 2016-2019), passando de 42 para 50.

- Descoberta: o código 0530 continua de 2004-2007 até 2016-2019 com o mesmo número ("Pró-Emprego e Renda"). A série dele é o próprio 0530, não o 0354 da tabela de equivalência proposta. Rever a equivalência.
- Robusto: "competitividade" e a dimensão "competitividade e produção" não mudam (p de permutação 0,002 e 0,004 nas duas versões; salto em 2024-27 mantido).
- Sensível à curadoria: "trabalho e renda". Com o 0530 em 2008-2019, a dimensão fica alta também em 2008-2019 (36, 29, 26 por mil); o "pico de emprego em 2024-27" da versão oficial vinha de o 0530 estar fora em 2008-2019 e o 0354 dentro em 2024-27. Também perde significância a medida semântica de "digital" (p 0,008 para 0,079).
- Valores: o peso dos programas selecionados no PPA sobe em 2012-15 (2,1% para 5,5%, por causa do 0101 Acelera SC, programa de investimento) e o crédito sobe em 2008-15 (1,3% para 2,2% e 1,1% para 1,8%, pelas linhas de crédito do 0530). A queda do crédito até 0,4% em 2024-27 fica mais forte.
- Leitura: o achado central (competitividade) não depende dessas escolhas; afirmações sobre trabalho e renda, digital e tamanho orçamentário da política industrial dependem, e precisam da decisão de curadoria antes de ir para o texto.

## Competitividade: que competitividade é essa, e ela depende de algum programa? (12/11/2026)

Script `scripts/competitividade.py`; saídas `saidas/competitividade_frases.csv` e `saidas/competitividade_tira_um.csv`. Lista oficial (42 programas).

Que competitividade é essa (28 frases com competitividade, competitivo, produtividade ou diversificação; 19 novas e 9 herdadas de ciclo anterior):
- 2004-2007: nenhuma.
- 2008-2011: uma frase, no 0200: competitividade "nacional e internacional" como resultado de fomentar a produção e diversificar o padrão tecnológico. Competitividade como meta de um programa econômico.
- 2012-2019: competitividade de cadeias específicas: agronegócio (0310, "capacidade competitiva das cadeias produtivas do agronegócio"; produtividade agropecuária para competir no mercado mundial), micro e pequenas empresas e polos produtivos (0342), atração de investimento internacional (0212). 2016-2019 só herda texto de 2012-2015.
- 2020-2023: o 0200 é reescrito e a competitividade passa a ser "das empresas catarinenses", ligada a diminuir barreiras, fomentar investimentos e facilitar a abertura de empresas.
- 2024-2027: 10 frases, 8 novas, espalhadas por 6 programas. A competitividade vira justificativa transversal: aparece em ciência e tecnologia (0230, "aumentando a produtividade e a competitividade da economia de Santa Catarina"), em qualificação de trabalhadores (0354, "competitividade global do Estado"), no agro (0310, permanência das famílias no campo) e no programa novo 0353, que traz linguagem de política vertical: "setores estratégicos", "indústria, comércio e serviços", modernização, produtividade, diversificação econômica.
- Leitura: a competitividade passa de meta de um programa econômico (2008) e de cadeias específicas (2012-2019) para uma justificativa comum a vários programas e para a linguagem de setores estratégicos (2024-2027). A classificação "de quem" é feita por expressões e é aproximada; a leitura das frases é a evidência.

Tira um programa (refaz o teste de permutação 42 vezes, retirando um programa de cada vez):
- Dimensão "competitividade e produção": p fica entre 0,0005 e 0,027; abaixo de 0,05 nos 42 casos. A taxa de 2024-2027 fica entre 36,9 e 48,5 por mil. O programa que mais pesa é o 0353 (sem ele: 36,9 por mil, p = 0,027).
- Termo "competitividade": p entre 0,0005 e 0,009, abaixo de 0,05 nos 42 casos; taxa de 2024-2027 entre 24,5 e 31,9 por mil. O que mais pesa é o 0200 (sem ele: 24,5, p = 0,009).
- Leitura: o salto de 2024-2027 não depende de nenhum programa isolado.

## ODS revisitado: o conteúdo dos 17 ODS, e não só a sigla (12/11/2026)

Script `scripts/ods.py`; texto oficial dos 17 objetivos e 169 metas (ONU Brasil, brasil.un.org/pt-br/sdgs, baixado em 12/11/2026) em `dados/ods/ods_metas_onu_brasil.csv`; léxico de cada ODS em `dados/ods/lexico_ods.csv` (coluna `mantido`: 0 = termo genérico retirado na revisão); saídas `saidas/ods_taxas.csv`, `ods_antes_depois.csv`, `ods_semantico_programas.csv`, figuras `ods_mapa_ppa.png` e `ods_antes_depois.png`.

Método: léxico de cada ODS = lemas mais característicos das metas daquele ODS (TF-IDF contra os outros 16, presentes em no máximo 3 ODS e repetidos nas metas), com remoção manual de termos genéricos ou ambíguos nos PPAs ("conservação" de rodovias, "mudança", "empresa", "banco" etc.). Taxa por mil lemas em dois corpora (PPA inteiro, 514 programas; política industrial, 42) e comparação 2004-2015 x 2016-2027 com teste de permutação. Medida semântica complementar: ODS cujo texto é mais próximo de cada programa (vetores do spaCy).

- Nenhum ODS tem mudança significativa depois da Agenda 2030 (setembro de 2015), nem no PPA inteiro nem nos programas de política industrial. O vocabulário somado dos 17 ODS vai de 42 para 46 por mil lemas no PPA inteiro (p = 0,34).
- Tendências fracas de alta no PPA inteiro, sem significância: ODS 9 indústria, inovação e infraestrutura (2,7 para 4,8 por mil; p = 0,09), ODS 10 desigualdades (p = 0,07), ODS 17 parcerias (p = 0,08). ODS 13 clima aparece só a partir de 2020-2023 (2 ocorrências). ODS 5 igualdade de gênero: zero ocorrências em todo o período.
- Os temas mais presentes no PPA inteiro são estáveis e anteriores a 2015: educação (ODS 4), cidades e transporte (ODS 11), trabalho e crescimento (ODS 8), energia (ODS 7).
- Semântica: o ODS mais próximo dos programas de política industrial com maior similaridade é o ODS 9 (0212, 0353, 0200, 0230, 0310), uma validação independente da curadoria. Defesa civil e mobilidade urbana aproximam-se do ODS 13 a partir de 2020-2023. A medida é ruidosa (similaridade máxima mediana 0,31).
- Leitura: os PPAs de SC não citam os ODS e também não mostram aumento do vocabulário dos ODS depois de 2015. Não há sinal de alinhamento de linguagem com a Agenda 2030; os temas que coincidem com ODS já estavam nos planos antes dela. Ressalva: o texto das leis do PPA (fora do anexo) não foi verificado, e o léxico de cada ODS depende da revisão manual de termos genéricos.

## Figuras de resultados (10/11/2026)

Geradas por `scripts/figuras_resultados.py`, `composicao_discurso.py` e `termos_distintivos.py`, todas em `saidas/`: `instrumentos_participacao_ppa.png`, `instrumentos_presenca_acoes.png`, `continuidade_series.png`, `composicao_vs_reescrita.png`, `termos_distintivos_inicio_fim.png`, além de `circularidade_termos_chave_vs_controles.png` e `figura_conceitual_metodo.png`. A seção final do notebook mostra todas.

Correção (10/11/2026): a busca de "incentivo fiscal" tinha um falso positivo em 2004-2007 ("Receita Tributária", em ação de combate à sonegação do 0530). O padrão foi corrigido; incentivo fiscal tem zero menções em todos os períodos.

## Limitações a declarar

- PPA é intenção declarada, não política executada.
- Corpus pequeno (4 a 8 programas por período), o que limita LDA e qualquer inferência estatística.
- Seleção de programas é manual; resultados dependem dela.
- Termos-chave do gráfico de evolução escolhidos a dedo.

## Revisão de 12/11/2026 (noite): viés de seleção, semente x expansão, orçamento ajustado

Scripts: `scripts/robustez_competitividade.py` (saída `saidas/robustez_competitividade.csv`) e `scripts/orcamento_ajustado.py` (saídas `saidas/orcamento_ajustado.csv`, `saidas/orcamento_pessoal_epagri.csv`).

- Semente x expansão: só "competitividade" já dá a alta (p de variação 0,002; último PPA x anteriores p < 0,001). Os 3 termos novos sozinhos não variam (p = 0,62). A expansão não produz o resultado.
- Sem o 0353 (Incentivo à Competitividade, só em 2024-2027): continua (p = 0,022 dimensão; 0,006 só semente).
- PPA inteiro (514 programas): a dimensão não muda (3,0 a 6,4 por mil; p = 0,72). Não selecionados (472): estável, 2,2 a 4,7 por mil. A alta é específica dos programas de política industrial; o viés de seleção fica reduzido (leave-one-out, sem 0353, lista estável), não eliminado.
- Forma da série: tendência monotônica não significativa (Spearman p = 0,10). Significativos: amplitude (p = 0,005, passa Bonferroni para 5 dimensões, limite 0,01) e último PPA x cinco anteriores (+27 por mil, IC 95% 8 a 43, p = 0,003). Leitura: patamar 2008-2023 e alta em 2024-2027 com 12 ocorrências em 275 lemas. Não chamar de "tendência crescente".
- Inovação + "computador": sem variação significativa (p = 0,92). A dimensão digital de um termo não se sustenta.
- Orçamento: a folha da EPAGRI estava no 0110 (2004-2007) e no 0850 Gestão de Pessoas (2012-2019) e foi para o 0310 em 2020: o aumento de 2020-2027 é contábil. Sem pessoal e emendas, a parcela dos selecionados no PPA é 3,1 / 3,2 / 2,1 / 1,8 / 1,4 / 1,2%. Crédito a empresas (sem o crédito a municípios do BADESC): 0,52 / 0,80 / 0,52 / 0,65 / 0,39 / 0,30%.
- BADESC opera também com recursos próprios, fundos institucionais e captações externas (BID); o PPA só mostra a parte orçamentária. ICMS (PRODEC) fica fora do PPA.
- ODS 9 p = 0,09 entre 17 testes: não é tendência.
- PPA 2000-2003: não disponível na SEF (Lei 11.357/2000); solicitado à ALESC.

## PPA inteiro, contagem simples (13/11/2026, pós-reunião)

Notebook `notebooks/analise_ppa_inteiro.ipynb`; scripts `scripts/ppa_inteiro_*.py`; saídas `saidas/ppa_inteiro_*`. Medida: % dos lemas (sem TF-IDF). Corpus: 529 programas (2008-2011 com 65 programas, ver decisões de 13/11/2026), 15.685 lemas.

- Extração de 2008-2011 incompleta no pipeline principal (50 de 65 programas). Com os 65, a parcela dos selecionados em 2008-2011 cai de 3,16% para 2,16% do PPA; a série sem pessoal e emendas fica 3,07 / 2,16 / 2,08 / 1,78 / 1,37 / 1,21% e cai em todos os PPAs. Crédito a empresas não muda.
- PPA inteiro: nenhum tema muda além do acaso (permutação, p de 0,67 a 0,998). Inovação perto de 1,1% dos lemas de 2008 a 2023 e 0,9% em 2024-2027; educação 1,0% a 1,25%; indústria (ampliada) 0,2% a 0,4%. "Indústria" aparece 4 vezes e "industrial" 7 em todo o corpus. Nos selecionados só competitividade varia (p = 0,006); educação não aparece neles a partir de 2012.
- Competitividade x inovação (palavras soltas), selecionados, 2020-2023 para 2024-2027: inovação 8 para 3, competitividade 3 para 8, soma 11 para 11. PPA inteiro: 10 para 6, 7 para 10. O 0200 tinha as duas e passa a ter só competitividade. Sinal de substituição, contagens pequenas. Em 2024-2027 "inovação" coocorre com público e serviço (DETRAN Digital, compliance), não mais com "tecnológico".
- Público-alvo (campo cortado em 50 caracteres no PDF): trabalhadores nunca são público-alvo, nem no 0354. Empresas são o público de 44% (2004-2007) a 71% dos selecionados. O 0200 passa de "Empreendedores e empresas" (2020-2023) para "Municípios atendidos" (2024-2027).
- Subações (todas, em % do PPA): indústria e empresa 0,61 / 1,79 / 1,39 / 0,94 / 0,66 / 0,54%; inovação 0,88 / 0,64 / 0,53 / 0,61 / 0,44 / 0,41%. Em 2008-2015 boa parte das de indústria e empresa está no 0530 Pró-Emprego e Renda, fora da lista nesses PPAs.
- Texto copiado do PPA anterior (frases com similaridade de 0,9 ou mais, % dos lemas): 20 / 43 / 83 / 25 / 74% no PPA inteiro; 21 / 46 / 80 / 33 / 31% nos selecionados. Não segue reeleição x troca [verificar governos]. Em 2024-2027 o plano copia 74% e a política industrial só 31%, junto com a passagem dos programas para novas secretarias (SICOS, SECTI) [verificar criação]. Só com frases reescritas, a competitividade nos selecionados vai de 1,8% (2020-2023) para 5,3% dos lemas (2024-2027): a alta está no texto novo.
- Renovação de programas por código: 36,5% (2011), 12,6% (2015), 27,3% (2019), 10,5% (2023). Órgãos responsáveis distintos: 22, 19, 21, 19, 38, 41.
- Orçamento por área (sem pessoal e emendas): infraestrutura de 31% para 13%; saúde e educação perto de 12% cada em 2024-2027; desenvolvimento econômico e indústria 0,8 / 2,7 / 2,9 / 2,5 / 1,7 / 1,3%; CT&I 0,4% a 0,5%.
- Contagem reproduz o TF-IDF: similaridade entre vizinhos nos selecionados 0,77 / 0,90 / 0,81 / 0,70 (TF-IDF 0,76 / 0,90 / 0,81 / 0,70); PPA inteiro 0,80 a 0,97.
- Rascunhos: `docs/rascunho-governos-planejamento.md`, `docs/rascunho-teorico-agentes.md`; fichas em `saidas/fichas_programas_selecionados.md`.
- Correção de 2008-2011 aplicada ao pipeline principal (13/11/2026). Números das seções anteriores com "514 programas" e "3,16% em 2008-2011" ficam superados. Re-rodado: testes de competitividade nos selecionados idênticos (p 0,0046; último PPA 0,0028); PPA inteiro p amplitude 0,72 para 0,68 e p tendência 0,24 para 0,056 (abaixo de 0,10, acima do limite corrigido); não selecionados 0,74 para 0,95. ODS 9 no PPA inteiro p 0,09 para 0,07; semântica 43% x 8% mantida. Classificador: precisão média 0,44 para 0,47 (F1 0,42 para 0,41); 0530 de 2008-2011 e 0101 seguem entre os mais prováveis fora da lista.
