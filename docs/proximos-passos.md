# Próximos passos

Origem: reunião com o Prof. Dominik em 30/09/2026. Resumo dele: expandir e validar o léxico, aumentar os anos considerando o contexto político, cruzar co-ocorrência com clusterização e topic modeling.

Status: [ ] a fazer, [~] em andamento, [x] feito. Atualizar aqui conforme avançar.

## 0. Infra

- [x] Migrar o notebook do Colab para rodar local (ver CLAUDE.md). Feito em 05/11/2026: roda do zero, números conferem com `achados.md`.
- [ ] Considerar quebrar o notebook em módulos `.py` (extração, pré-processamento, análises) importados por um notebook enxuto de resultados.

## 1. Prioridade alta (sem dado novo, custo previsível)

- [~] Expansão do léxico por co-ocorrência (snowballing): partir dos termos-chave atuais, medir com quais termos eles coocorrem (janela ou mesmo programa), propor candidatos a novos termos, validar com o Andrey, repetir. Rodada 1 feita em 09/11/2026 com dois métodos (`scripts/snowball.py`, coocorrência por janela e PMI; `scripts/embeddings_candidatos.py`, similaridade por embeddings do spaCy). Coocorrência rendeu pouco (26 textos distintos, ruído de frases-padrão); embeddings rendeu candidatos mais úteis. Validado em 12/11/2026 (`saidas/lexico_validado.csv`); índice por dimensão em `scripts/indice_lexico.py`. Próximo: nova rodada de candidatos a partir dos 20 termos aceitos, se o orientador quiser expandir mais.
- [x] Responder a crítica de circularidade: comparar termos-chave contra o vocabulário completo (quanto pesam e como variam em relação a todas as palavras). Mostrar que o resultado não é artefato da escolha inicial. Feito em 09/11/2026 (`scripts/circularidade.py`; resultado em `achados.md`): só "competitividade" excede claramente o acaso; os demais dependem de poucos programas. Falta decidir como apresentar isso na monografia.
- [x] Checar se os PPAs de SC citam os ODS; se sim, usar o vocabulário dos ODS como léxico externo de comparação. Checado em 06/11/2026: zero menções (ODS, Agenda 2030, ODM, ONU) nos 5 anexos em `dados/ppa/`. Não viável a partir desses PDFs; o texto das leis não foi verificado. Revisitado em 12/11/2026 com o vocabulário das 169 metas (`scripts/ods.py`): sem aumento depois de 2015 em nenhum ODS; ver `achados.md`.
- [x] Figura conceitual de como o texto é classificado: PDF, programa (código), campo (nome/objetivo/justificativa), tratamento (lematização), análise. Feita em 09/11/2026: `saidas/figura_conceitual_metodo.png` (script `scripts/figura_conceitual.py`).
- [~] Deixar explícita na metodologia a distinção programa ("política") versus campo ("seção"). Rascunho em `docs/metodologia-rascunho.md`; falta revisão do Andrey e confirmação dos trechos entre colchetes.

## 2. Prioridade média (trabalho novo, sem dado novo)

- [~] Clusterizar termos (por co-ocorrência ou embeddings do spaCy) antes do topic modeling, para tópicos mais estáveis. Feito em 09/11/2026 (`scripts/clusters_termos.py`): LDA sobre campos é mais estável entre sementes, mas em 10/11/2026 a clusterização mudou por inteiro ao entrar um único programa (0530). Não sustenta interpretação com este corpus; manter só como registro metodológico, a menos que o corpus cresça.
- [x] Separar mudança de discurso de mudança de composição (`scripts/composicao_discurso.py`, 10/11/2026).
- [x] Termos distintivos início x fim por log-odds (`scripts/termos_distintivos.py`, 10/11/2026): só "rural" significativo.
- [x] Medir coaparência dos termos que mudaram com tipos de instrumento (crédito, clusters, APLs, incentivo fiscal). Busca feita em 09/11/2026 (`scripts/mencoes.py`): APL e incentivo fiscal têm zero menções em objetivo e justificativa. Nas ações e subações (`scripts/blocos_programas.py`) os instrumentos aparecem: crédito BADESC em todos os períodos, APL de 2004 a 2015, incubadoras e parques até 2019. Valores orçados extraídos em 10/11/2026 (`scripts/valores_acoes.py`, validados contra o TOTAL GERAL): crédito cai de 0,8-1,3% para 0,4% do PPA. Falta só cruzar com o contexto histórico.
- [~] Leitura fechada dos programas selecionados atrás de: clusterização de pequenos produtores rurais, APLs, clusters, educação tecnológica. Escopo: só os programas já selecionados. Busca automática feita (`mencoes.py`, `blocos_programas.py`) e frases de competitividade lidas (`competitividade.py`); falta a leitura humana das frases e ações sobre pequenos produtores, APL e educação tecnológica.
- [~] Contexto histórico: cenário econômico-político do Brasil e de SC em cada PPA, governo e orientação de quem formulou cada plano. Trabalho de leitura, não de código. Esqueleto em `docs/contexto-historico.md` (10/11/2026), com fatos marcados [verificar]; falta conferir em fonte.
- [x] Decidir se o 0530 Geração de Emprego e Renda entra em 2004-2007: incluído em 10/11/2026. O 0530 de 2008-2019 (mesmo código) foi testado só em cenário (`scripts/cenario_curadoria.py`); decisão pendente.
- [ ] Discutir com o orientador se o 0210 continua na lista: em 2024-2027 ele é dominado por emendas parlamentares do Fundo Social (1,43 bi), e em 2020-2027 o 0310 é dominado por folha da EPAGRI.

## 3. Risco alto (dado novo, formato desconhecido)

- [~] PPAs anteriores a 2008 (antes do boom das commodities). PPA 2004-2007 incluído em 09/11/2026; o 2000-2003 (o único realmente anterior ao boom, Lei 11.357/2000) não está disponível na SEF; solicitado à ALESC. Fazer CEDO, para sobrar tempo se o PDF exigir regex novo. Usar a skill `/novo-periodo`.
- [ ] Benchmark para comparar SC com outras UFs. O de maior risco (outro estado, outro template). Se não couber no prazo, vira "trabalho futuro" no texto.

## Feito além da lista de 30/09 (09-12/11/2026)

- [x] Léxico validado (20 termos, 5 dimensões) e índice por dimensão com teste contra 1.000 léxicos aleatórios (`scripts/indice_lexico.py`).
- [x] Corpus complementar com nomes de ações e subações (`scripts/corpus_acoes.py`).
- [x] Robustez do achado de competitividade: tira um programa (42 casos) e leitura das frases (`scripts/competitividade.py`).
- [x] Classificador de texto para conferir a curadoria, inspirado em Juhász et al. (2025) (`scripts/classificador.py`), e cenário antes x depois com 8 programas a mais (`scripts/cenario_curadoria.py`).
- [x] Documento de status para os orientadores (`saidas/estado_do_trabalho_2026-11-12_v7.docx`), com testes de viés de seleção e orçamento ajustado (`robustez_competitividade.py`, `orcamento_ajustado.py`).
- [ ] Renúncia de ICMS (demonstrativo da LDO) como série complementar; conferir crédito do BADESC fora do orçamento (demonstrativos do banco).
- [ ] Segunda pessoa avaliando os 38 candidatos do léxico (concordância).

## Prazo

Cerca de 2 a 3 semanas a partir de 30/09/2026 para o conjunto. Ordem sugerida: migração, PPAs antigos (descobrir cedo se dá problema), léxico, figura e metodologia, co-ocorrência e clusterização, contexto histórico em paralelo, benchmark de UFs por último se houver tempo.

## Fase seguinte da tese (fora deste ciclo)

Regressão ligando política industrial a complexidade econômica por microrregião (ICE DataViva 2006-2024), provavelmente painel com efeitos fixos. Variáveis candidatas: dummies de regime discursivo por período, execução orçamentária dos programas selecionados por microrregião. Desenhar com o orientador.

