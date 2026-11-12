# Histórico de decisões

Registro curto do que foi decidido e por quê. Adicionar novas entradas no topo.

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
- 2008-2011 com regex próprio (`padrao_2008`), nome e órgão travados em uma linha para não vazar para tabelas de ações. Resultado: 50 blocos limpos.
- Limpeza de cabeçalho/rodapé do 2008-2011 (`rodape_2008`) antes da extração. Contaminação zerada.
- 2020-2023: abandonado o recorte de colunas; usada versão alternativa do PDF em coluna única (`ppa_2020_2023_v2.pdf`), 108 blocos limpos.
- Curadoria de `codigos_industria` para os 5 períodos. Incluídos por julgamento: 0212 (comércio exterior) e 0354 (emprego). Excluídos: 0211, 0343, 0220. 0250 pendente de confirmação.
- 2016-2019: 0210 e 0212 estavam faltando por esquecimento na curadoria; detectado pelo buraco na tabela de continuidade e corrigido.
- Lematização com filtro POS (NOUN, VERB, ADJ).
- TF-IDF agregado por período; bigramas em análise separada porque sumiam no corte de `max_features` junto com unigramas.
- LDA por programa (não por período) por falta de documentos.
- Bugs recorrentes de célula fora de ordem (`ordem_periodos`, `continuidade` usados antes de definidos). Regra: rodar do zero após reorganizar.
