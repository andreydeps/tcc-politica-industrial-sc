# Política industrial nos PPAs de Santa Catarina (2004-2027)

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/andreydeps/tcc-politica-industrial-sc/blob/main/notebooks/TCC.ipynb)

TCC de Andrey de Paula e Silva (Ciências Econômicas, UFSC). Orientação: Prof. Dominik Hartmann; coorientação: Lukas Pezzini.

Mineração de texto sobre os Planos Plurianuais (PPAs) de Santa Catarina para medir como o discurso de política industrial mudou entre 2004 e 2027: extração dos programas de cada PPA, seleção manual dos programas de política industrial, léxico por dimensão com testes contra o acaso, instrumentos e valores orçados nas ações e comparação com o vocabulário dos ODS.

## Como abrir

- **Colab:** clique no botão acima. O notebook já vem com as saídas salvas; para rodar de novo, *Ambiente de execução > Executar tudo* (a primeira célula instala as dependências, alguns minutos).
- **Resultados para a reunião de 13/11/2026 (só leitura dos resultados salvos):** [abrir no Colab](https://colab.research.google.com/github/andreydeps/tcc-politica-industrial-sc/blob/main/notebooks/reuniao_2026-11-13.ipynb).
- **Estado atual do trabalho:** [`saidas/estado_do_trabalho_2026-11-12_v7.docx`](saidas/estado_do_trabalho_2026-11-12_v7.docx).

## Estrutura

```
notebooks/TCC.ipynb   pipeline principal: extração, seleção, TF-IDF, similaridade, LDA, resultados complementares
scripts/              análises complementares (léxico, circularidade, robustez, instrumentos, orçamento, ODS, figuras)
dados/ppa/            PDFs dos Anexos Únicos dos PPAs (documentos públicos da SEF/SC)
dados/ods/            metas dos ODS (ONU Brasil) e léxico derivado
docs/                 regras de seleção, pipeline, achados, decisões, próximos passos, rascunho de metodologia
saidas/               figuras, tabelas e documentos gerados
```

## Rodar localmente

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```

Os scripts rodam a partir da raiz, por exemplo `python scripts/robustez_competitividade.py`.
