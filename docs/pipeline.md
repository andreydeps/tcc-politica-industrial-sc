# Pipeline técnico

Referência das etapas do `notebooks/TCC.ipynb`, com as decisões técnicas e as armadilhas já encontradas.

## 1. Fontes

Arquivos esperados em `dados/ppa/`:

| Período | Arquivo | Observação |
|---|---|---|
| 2008-2011 | ppa_2008_2011.pdf | formato próprio (rótulos em Título Case), 283 páginas |
| 2012-2015 | ppa_2012_2015.pdf | formato padrão |
| 2016-2019 | ppa_2016_2019.pdf | formato padrão |
| 2020-2023 | ppa_2020_2023_v2.pdf | usar a v2. A versão original era Diário Oficial em 3 colunas e não parseava |
| 2024-2027 | ppa_2024_2027.pdf | formato padrão, usa UNIDADE RESPONSÁVEL em vez de ÓRGÃO RESPONSÁVEL |

Links oficiais (o conteúdo útil está sempre no Anexo Único / Anexo I, não na lei):
- 2008-2011: sef.sc.gov.br/api-portal/Documento/ver/284
- 2012-2015: sef.sc.gov.br/api-portal/Documento/ver/303
- 2016-2019: alesc.sc.gov.br/sites/default/files/arquivos_orcamento/anexoUnicoPPA2016-2019_gerado_redacaoFinal.pdf
- 2020-2023: sef.sc.gov.br/api-portal/Documento/ver/702 (o arquivo v2 em uso veio de outra fonte, de layout em coluna única)
- 2024-2027: Lei_n_18.835_PPA_2024_2027_e_anexos.pdf

## 2. Extração (pdfplumber + regex)

Por que regex e não NLP aqui: o Anexo Único é um documento semi-estruturado com rótulos fixos. Separar campos é problema de parsing de documento, não de linguagem natural. NLP entra depois, sobre o conteúdo dos campos.

Regex geral (2012-2015 em diante):

```python
padrao = re.compile(
    r"PROGRAMA\s+(?P<codigo>\d{4})\s+(?P<nome>.*?)\s+"
    r"(?:ÓRGÃO|UNIDADE) RESPONSÁVEL\s+(?P<orgao>.*?)\s+"
    r"OBJETIVO\s+(?P<objetivo>.*?)\s+"
    r"JUSTIFICATIVA\s+(?P<justificativa>.*?)\s+"
    r"PÚBLICO-ALVO",
    re.DOTALL
)
```

Regex 2008-2011 (sem a palavra PROGRAMA, rótulos em Título Case).

**Substituído em 13/11/2026:** o regex abaixo pegava só 50 dos 65 programas (falha com "Tipo" de várias palavras, como "Gestão de Políticas Públicas", e com nome ou órgão em duas linhas). O notebook agora faz `padrao_2008 = padrao_2004` (regex do 2004-2007, mais abaixo), que pega os 65; os 50 antigos saem idênticos. O `rodape_2008` continua igual. Versão antiga, só para registro:

```python
padrao_2008 = re.compile(
    r"(?P<codigo>\d{4})\s+(?P<nome>[^\n]+?)\s*Tipo\s+\S+\s*\n"
    r"Órgão Responsável\s+(?P<orgao>[^\n]+?)\s*Horizonte Temporal.*?\n"
    r"Objetivo\s+(?P<objetivo>.*?)"
    r"Justificativa\s+(?P<justificativa>.*?)"
    r"Público Alvo",
    re.DOTALL,
)

rodape_2008 = re.compile(r"Página:\s*\d+\s*de\s*283.*?OGE\s*OF", re.DOTALL)
```

Regex 2004-2007 (mesma família do 2008-2011, mas com `Tipo` de várias palavras, nome de programa e de órgão que quebram em duas linhas, e linhas só com espaços entre rótulos). Testado em 06-09/11/2026 sobre texto do pdfplumber: 118 de 118 blocos, boilerplate 0, sem vazamento entre programas. NÃO testado com o `processa_ppa` do notebook ainda:

```python
rodape_2004 = re.compile(
    r"Página:\s*\d+\s*de\s*433"
    r"|ESTADO DE SANTA CATARINA\s+ANEXO ÚNICO\s+Plano Plurianual 2004 - 2007\s+\d{4}/\d{4}\s+\d{4}/\d{4}\s+"
    r"PROGRAMA/AÇÕES/SUBAÇÕES\s+PRODUTO UNIDADE FÍSICO\s+OGE\s+OF"
)
padrao_2004 = re.compile(
    r"(?m)^[ \t]*(?P<codigo>\d{4})[ \t]+(?P<nome>[^\n]+?)[ \t]+Tipo[ \t]+(?P<tipo>[^\n]+?)[ \t]*\n"
    r"(?P<nome2>(?![ \t]*Órgão Responsável)[^\n]*\n)?\s*"
    r"Órgão Responsável[ \t]+(?P<orgao>[^\n]+?)[ \t]+Horizonte Temporal[^\n]*\n"
    r"(?P<orgao2>(?![ \t]*Objetivo)[^\n]*\n)?\s*"
    r"Objetivo\s+(?P<objetivo>.*?)"
    r"Justificativa\s+(?P<justificativa>.*?)"
    r"Público Alvo",
    re.DOTALL,
)
# depois do finditer: nome = nome + nome2; orgao = orgao + orgao2 (campos opcionais de continuação)
```

Atenção ao incorporar no notebook: o grupo `tipo` e os grupos `nome2`/`orgao2` não existem nos outros regex; juntar `nome2` ao `nome` e `orgao2` ao `orgao` antes de montar o DataFrame. Com o pypdfium2 o texto sai fora de ordem (rótulo "Objetivo" depois do texto): usar pdfplumber.

Numeração de códigos: em 2004-2007 a numeração é outra (0200 = Agrorredes, 0230 = Pesquisa Agropecuária, 0250 = Acesso à Terra; Inclusão Digital = 0410; Competitividade = 0580; Fomento à Pesquisa, Tecnologia e Inovação = 0490). A tabela de continuidade por código NÃO vale para este período sem uma tabela de equivalência.

`processa_ppa(caminho, periodo, duas_colunas=False, regex=None, limpar_regex=None)`: lê o PDF, aplica `limpar_regex` (se houver), roda o regex, remove duplicatas por (codigo, objetivo) e filtra pelos códigos de `codigos_industria[periodo]`.

### Armadilhas conhecidas

- `.*?` com `re.DOTALL` vaza entre blocos. No 2008-2011, números de 4 dígitos soltos em tabelas de ações/subações eram capturados como código. Solução: travar em uma linha (`[^\n]+?`) os campos que são de uma linha só (nome, órgão) e deixar DOTALL só para objetivo/justificativa.
- Cabeçalho/rodapé de página contamina campos que atravessam virada de página. Solução: limpar o texto com um regex de rodapé ANTES de extrair. Checagem padrão: contar matches com "Página" dentro de objetivo/justificativa (tem que dar 0).
- Layout em múltiplas colunas quebra a ordem do texto. O recorte em 2 colunas (`duas_colunas`) existe no código mas não resolveu 3 colunas; a saída foi achar outra versão do PDF. Antes de escrever código de recorte, procurar versão alternativa do documento.
- Duplicatas: o mesmo programa pode aparecer mais de uma vez no anexo. Deduplicar por (codigo, objetivo).
- Rótulo "Público Alvo:" dentro da justificativa (visto no 0310 de 2024-2027): o `processa_ppa` corta a justificativa nesse rótulo. Checagem: nenhuma justificativa deve conter "público alvo".
- Filtro de classe gramatical: palavras com inicial maiúscula no meio do texto podem ser marcadas como nome próprio (PROPN) pelo spaCy e descartadas. Bom para listas de público-alvo, mas pode descartar termos legítimos escritos em maiúscula.
- Curadoria incompleta passa despercebida: em 2016-2019, 0210 e 0212 existiam no PDF mas não estavam na lista. Foi detectado pelo "buraco" na tabela de continuidade. Sempre olhar a continuidade depois de mudar a lista.

### Checagens de sanidade ao processar um período

1. Rótulos presentes no texto (`"PROGRAMA" in texto`, etc.) para escolher o regex.
2. Número de matches plausível (2008-2011: 50; 2020-2023 v2: 108; 2012-2015: ~115).
3. Contaminação de rodapé = 0.
4. Todos os códigos esperados de `codigos_industria[periodo]` presentes nos matches.
5. Imprimir codigo + nome de todos os programas para curadoria.

## 3. Pré-processamento

- Texto = objetivo + " " + justificativa.
- spaCy `pt_core_news_lg`: lematização, minúsculas, remove stopwords, pontuação, espaços e não-alfabéticos, mantém só NOUN, VERB e ADJ.
- Achado colateral: vários programas têm texto idêntico entre períodos (reaproveitamento). Isso é dado, não erro, mas infla a similaridade entre períodos vizinhos.

## 4. Análises

| Análise | Unidade de documento | Configuração | Saída |
|---|---|---|---|
| TF-IDF unigramas | período (textos agregados) | `TfidfVectorizer(max_features=200)` | `df_tfidf`, `matriz_tfidf`, top 15 por período |
| TF-IDF bigramas | período | `ngram_range=(2,2)`, `max_features=100` | `df_bigramas` (célula separada: misturar com unigramas fazia os bigramas sumirem no corte de `max_features`) |
| Wordcloud | período | pesos do `df_tfidf` | figura |
| Evolução de termos-chave | período | lista fixa manual | gráfico de linha |
| Similaridade de cosseno | período | sobre `matriz_tfidf` | heatmap 5x5, valores em [0,1] |
| Continuidade | código | groupby código, lista de períodos | tabela |
| LDA | programa individual | `CountVectorizer(max_features=200)`, 5 tópicos, `random_state=42` | tópicos e média por período (barra empilhada) |

Por que TF-IDF por período e LDA por programa: a pergunta é comparar períodos, então o TF-IDF agrega por período. LDA precisa de mais documentos que 5 para achar tópicos, então roda por programa e depois agrega.

Sobre os valores de TF-IDF: não são frequência bruta. É frequência no período vezes raridade nos outros períodos, com normalização L2 por linha. Comparar termos dentro do mesmo período é direto; comparar o mesmo termo entre períodos exige cuidado.

Cosseno não é correlação: correlação de Pearson é o cosseno de vetores centrados na média. Como TF-IDF é não negativo, o cosseno aqui fica entre 0 e 1.

## 5. Ambiente

- No Colab houve conflito Pillow x wordcloud (`ImportError: cannot import name '_Ink' from 'PIL._typing'`), resolvido com `pillow<11.3`. Em ambiente local novo, instalar versões recentes de ambos costuma resolver; se o erro voltar, fixar `pillow<11.3`.
- Reiniciar o kernel apaga tudo da memória: rodar o notebook do início.
