# Histórico de decisões

Registro curto do que foi decidido e por quê. Adicionar novas entradas no topo.

## 2026-11-13 (redes: aprovação PRELIMINAR do Andrey, a revisar)
Direção nova: olhar todos os programas (coocorrências, comparação de subações, oferta e demanda pelo público-alvo, redes), possivelmente sem ponte com o ICE. Notebook `notebooks/redes_ppa.ipynb`; regras em `scripts/redes_regras.py`; funções em `scripts/redes.py`. `networkx` acrescentado ao requirements.

Regras propostas pelo assistente e aprovadas de forma preliminar:
1. Rede de termos: frase como unidade; lema com 4 ou mais frases; ligação com 2 ou mais frases juntas; peso = proximidade phi = C_ij / max(N_i, N_j); comunidades por Louvain (semente 42); desenho = árvore geradora máxima + ligações mais fortes até grau médio 4.
2. Decisão do assistente depois de ver os dados: as comunidades de termos são instáveis (ARI 0,23 nas reamostragens de frases; 0,22 a 0,26 com 7 combinações de limiares), então só as vizinhanças de cada termo são interpretadas, com estabilidade por 200 reamostragens; a figura pinta os temas aprovados, não as comunidades.
3. Rede de programas: lemas em mais de 20% dos programas do PPA saem como formato; 3 vizinhos mais parecidos com cosseno de pelo menos 0,10; homofilia e Mantel com 2.000 permutações; densidade = soma da similaridade com os selecionados / soma com todos. Subações representadas pelos lemas dos nomes, sem repetir nome igual.
4. Público-alvo ampliado: + setor público, estudantes e escolas, grupos vulneráveis, sem definição. Ajustes depois de ver os casos: "pequen" solto saiu de micro e pequenas empresas (pegava "pequenos agricultores"); erros do PDF ("pode legislativo", "promoteres"); "membros" saiu de setor público (pegava "famílias ... e seus membros"); clientes de Celesc/SCGás, moradores, comunidades e gerações futuras em sociedade em geral. Precedência: sociedade em geral só se nada mais casar; micro e pequenas substitui empresas. Exceção explícita: "Cidadãos, investidores, turistas e consumidores" (comunicação institucional) = sociedade em geral. Valor de programa com mais de um público dividido em partes iguais. Peso = valor sem pessoal e emendas.
5. Genealogia: pai = herança de pelo menos 20% do valor das subações ou dos lemas. Decisão do assistente depois de ver os dados: subação herdada exige mesmo código E nome parecido (SequenceMatcher de 0,6 ou mais), porque de 2004-2007 para 2008-2011 os códigos foram renumerados (só 1% dos códigos repetidos tem nome parecido; de 2012 em diante, 86% a 98%). Consequência: 2004 → 2008 só tem herança de texto.
6. Mesmo dono: coeficiente de sobreposição de pelo menos 0,5 nas palavras distintivas dos nomes dos órgãos (sem sigla, sem "desenvolvimento"); testado em 12 pares conhecidos. Caso ambíguo: "Desenvolvimento Sustentável" (2008-2011) x "Desenvolvimento Econômico Sustentável" conta como mesmo dono [verificar].

## 2026-11-13 (pós-reunião com o Dominik)
Decidido na reunião: medida principal passa a ser contagem e % sobre o total de lemas, sem TF-IDF; nada por CNAE. Análise do PPA inteiro em `notebooks/analise_ppa_inteiro.ipynb`; regras em `scripts/ppa_inteiro_listas.py`.

Aprovado pelo Andrey antes de rodar:
- Educação: versão "núcleo" (educação, ensino, estudante, escolar, escola, professor, educacional, aprendizagem, aluno, universidade, curso, educativo). Fora: formação, capacitação, qualificação, técnico, conhecimento, pesquisa.
- Indústria: versão "ampliada" (indústria, industrial, agroindústria, agroindustrial + produtivo, cadeia, setorial). Empresa: empresa, empresarial, empreendedor, empreendimento, microempresa, empresário, empreendedorismo.
- Público-alvo: só as 7 categorias propostas pelo Andrey (empresas, micro e pequenas empresas, trabalhadores, produtores rurais, municípios, instituições de pesquisa, sociedade em geral) + "outros".
- Regras de subações de inovação e de indústria e empresa (com exclusões) e áreas por órgão (oferta no público-alvo e temas do orçamento).

Decisões do assistente (todas APROVADAS pelo Andrey em 13/11/2026, "tá tudo autorizado"; revisáveis depois):
1. Extração de 2008-2011: o `padrao_2008` pega 50 dos 65 programas do PDF (falha com "Tipo" de várias palavras e nome/órgão em duas linhas). Nos scripts novos o 2008-2011 usa o `padrao_2004`, que pega os 65 (os 50 antigos saem idênticos; os 15 novos não são selecionados). APLICADO no `TCC.ipynb` (`padrao_2008 = padrao_2004`); rodados de novo o notebook, blocos_programas, corpus_acoes, indice_lexico (ações), valores_acoes, orcamento_ajustado, classificador, cenario_curadoria, robustez_competitividade, ods, figuras_doc, a v7 e os dois notebooks. Efeito nos resultados antigos: a parcela dos selecionados em 2008-2011 cai de 3,16% para 2,16% do PPA (subações do 0220 e outros eram somadas ao 0210). Número de controle passa a ser "2008-2011 com 65 blocos".
2. Ajustes nas regras aprovadas depois de ver os casos: público "empresas" sem `client` (pegava 13 programas da Celesc, consumidores de energia) e sem `\bpj\b` (pegava "pf, pj sem fins lucrativos"); `polpula` acrescentado (erro de digitação do PDF). Subações: `\bciencia` (sem a fronteira casava "deficiência" e "eficiência") e `subvenc\w* econom` ("subvenc" pegava subvenção a organizações sociais da saúde e a bombeiros).
3. Temas "inovação" e "competitividade" do item 1 = dimensões do léxico atual (4 termos cada); "política industrial" = léxico inteiro (20 termos). No item 2 foram usadas as palavras soltas "competitividade" e "inovação".
4. Texto copiado (item 5): frases cortadas por pontuação; similaridade SequenceMatcher sobre texto sem acento e pontuação; "quase igual" = 0,9 ou mais; comparação com qualquer frase do PPA anterior (não só do mesmo programa); 2004-2007 conta como texto novo.
5. Tipo de transição: 2007 e 2015 reeleição; 2011, 2019 e 2023 troca de governador (tudo [verificar]; 2011 trata Colombo como troca, embora possa ser continuidade de coalizão).
6. Áreas por órgão: primeira regra que casa vale. Casos de fronteira: Metrologia e SC Participações em desenvolvimento econômico; DETRAN em segurança; Agência de Regulação em infraestrutura; SUDESC e SDRs em gestão; Fundação Escola de Governo em gestão; UDESC em educação.
7. Orçamento por área sem pessoal e emendas: mesmos padrões de `orcamento_ajustado.py`, retirados do numerador e do denominador. Dívida não foi separada (não havia regra aprovada); fica dentro de "gestão".
8. Teste de permutação (3.000 sorteios) acrescentado ao item 1, não pedido.
9. Bigramas: lemas vizinhos dentro da frase depois de tirar stopwords. Coocorrência: nº de frases, top 6. Treemap: 25 lemas mais frequentes, sem filtro de palavras genéricas. Similaridade: cosseno das contagens brutas por PPA.
10. Mudança de subações dentro do programa: comparação pelo código de 6 dígitos (subestima continuidade se houver renumeração). Unidade responsável: sigla no fim do nome da subação (cobertura de 33% a 62% das subações).
11. Fichas: "o que não faz" deixado em branco para a leitura qualitativa.

## 2026-11-12
- Orientação corrigida: Dominik Hartmann é o orientador e Lukas Pezzini o coorientador (Marcelo Arend não é o orientador).
- Léxico validado pelo Andrey seguindo a proposta do assistente: 20 termos aceitos (16 entram + 4 variantes) em 5 dimensões; 9 "talvez" e 9 "não entra" ficam fora. Arquivo: `saidas/lexico_validado.csv`.

## 2026-11-10
- 0530 Geração de Emprego e Renda incluído em 2004-2007 (decisão do Andrey); 9 programas nesse período, 42 no total. Série proposta: 0354 (a validar).
- Valores orçados das subações extraídos (`scripts/valores_acoes.py`) e validados contra o TOTAL GERAL oficial de cada PPA quadrienal. Comparação entre períodos por participação, porque 2004-2007 e 2008-2011 trazem valores de um ano só.
- Leitura anterior "crédito ampliado em 2020-2027" corrigida: o crédito persiste mas perde peso relativo.
- Falha de processo registrada: na curadoria de 2004-2007 o assistente não listou os 14 programas que só passaram a ser extraídos na última versão do regex; entre eles o 0530 Geração de Emprego e Renda, candidato relevante. Decisão pendente do Andrey.

## 2026-11-09
- PPA 2004-2007 incluído (118 blocos extraídos, regex `padrao_2004`). Lista de 8 programas decidida pelo Andrey: 0580, 0490, 0230, 0540, 0570, 0410, 0510, 0970. Equivalência de códigos com os períodos seguintes é proposta (a validar com o orientador).
- Ensaios de léxico refeitos com 6 períodos: o léxico quase não muda (textos de 2004-2007 curtos e genéricos). Embeddings do spaCy rendem candidatos mais úteis que coocorrência por janela.
- Checagem de circularidade feita: só "competitividade" excede o acaso e os controles de mesma frequência.
- Correção na extração: justificativa cortada no rótulo "Público Alvo:" quando ele aparece dentro do campo (caso do 0310 de 2024-2027). Sem efeito nas análises lematizadas (palavras eram nomes próprios para o spaCy); a busca de menções passou de 18 para 17.
- Instrumentos concretos (crédito, APL, incubadoras) procurados no bloco completo do programa (ações e subações), não só em objetivo e justificativa, porque nesses campos eles quase não aparecem.
- Lição de ambiente: execução longa do notebook falhou porque o notebook do Andrey entrou em espera (bateria). Rodar na tomada e não em paralelo com outra extração pesada.

## 2026-11-06
- 0210 incluído em 2020-2023 em `codigos_industria` (existia no PDF e estava fora). Decisão do Andrey: manter a continuidade nos cinco períodos; a lista inteira será revisada depois com o léxico. Também confirmado: nome do 0212 em 2020-2023 e ausência de menções a ODS nos 5 anexos.

## 2026-11-05
- Migração do Colab para VS Code + Claude Code, para eliminar o copia e cola e acelerar. A partir daqui o Claude pode escrever e editar código direto.
- Notebook migrado para rodar local: removidos `!pip`, `drive.mount` e `spacy download`; caminhos via `pathlib` apontando para `dados/ppa/`; imports e `ordem_periodos` definidos uma vez no topo; gráficos salvos em `saidas/` (PNG). Rodado do zero sem erros; blocos extraídos (50, 115, 107, 108, 104), programas por período (4, 8, 7, 6, 7), continuidade e top termos do TF-IDF conferem com `achados.md`.
- Ambiente: venv fora do OneDrive em `C:\Users\andre\venvs\tcc` (Python 3.13.5 do Anaconda), kernel Jupyter `tcc`. PDFs copiados de `PPA/` para `dados/ppa/`.
- Saídas do Colab estavam desatualizadas (continuidade sem 0210/0212 em 2016-2019; "bigramas" imprimindo unigramas). A execução local corrigiu os dois casos, sem mudança de lista.

## 2026-09-30
- Reunião com o Prof. Dominik. Próximos passos registrados em `proximos-passos.md`.
- Planilha de validação dos programas montada (`programas_industria_por_periodo.xlsx`), com aba de casos em debate.
- Título do heatmap trocado para "Similaridade de vocabulário entre os PPAs (TF-IDF)".

## Setembro de 2026 (construção do pipeline)
- Extração por regex por período em vez de NLP: o problema é parsing de documento semi-estruturado.
- 2008-2011 com regex próprio (`padrao_2008`), nome e órgão travados em uma linha para não vazar para tabelas de ações. Resultado: 50 blocos limpos. (Corrigido em 13/11/2026: eram 65 programas; ver entrada daquele dia.)
- Limpeza de cabeçalho/rodapé do 2008-2011 (`rodape_2008`) antes da extração. Contaminação zerada.
- 2020-2023: abandonado o recorte de colunas; usada versão alternativa do PDF em coluna única (`ppa_2020_2023_v2.pdf`), 108 blocos limpos.
- Curadoria de `codigos_industria` para os 5 períodos. Incluídos por julgamento: 0212 (comércio exterior) e 0354 (emprego). Excluídos: 0211, 0343, 0220. 0250 pendente de confirmação.
- 2016-2019: 0210 e 0212 estavam faltando por esquecimento na curadoria; detectado pelo buraco na tabela de continuidade e corrigido.
- Lematização com filtro POS (NOUN, VERB, ADJ).
- TF-IDF agregado por período; bigramas em análise separada porque sumiam no corte de `max_features` junto com unigramas.
- LDA por programa (não por período) por falta de documentos.
- Bugs recorrentes de célula fora de ordem (`ordem_periodos`, `continuidade` usados antes de definidos). Regra: rodar do zero após reorganizar.
