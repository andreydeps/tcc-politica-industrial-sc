# Fundamentação teórica e metodológica

Base para o capítulo de metodologia. As referências abaixo são as usadas na argumentação; conferir dados completos (editora, páginas, DOI) antes de citar no texto final.

## Política industrial

- Chang, H.-J. (1994). The Political Economy of Industrial Policy. Definição ampla: política que afeta a estrutura setorial da produção.
- Rodrik, D. (2004). Industrial Policy for the Twenty-First Century. Rodrik, D. (2008). Normalizing Industrial Policy. Política industrial como processo de descoberta (self-discovery) e colaboração Estado e setor privado.
- Pack, H.; Saggi, K. (2006). Is There a Case for Industrial Policy? Distinção horizontal versus vertical.
- Hausmann, R.; Hidalgo, C. et al. Atlas of Economic Complexity / product space. Diversificação em direção a atividades mais complexas.
- Hartmann, D. et al. (2024), Nova Economia; Cardoso et al. (2025), Revista Brasileira de Inovação. Literatura aplicada a SC e Brasil.

## Etapas do pipeline

Extração por regex: extração de informação de documento semi-estruturado. Os rótulos fixos do Anexo Único permitem separar campos de forma determinística e auditável. NLP não é a ferramenta para essa etapa.

Lematização (spaCy): o português é morfologicamente rico (flexão de gênero, número, conjugação). Sem lematizar, "inovar", "inovação", "inovações" contam como termos diferentes. O filtro por classe gramatical (substantivo, verbo, adjetivo) remove palavras funcionais que não carregam conteúdo.

TF-IDF: Spärck Jones (1972) para o IDF; Salton e o modelo de espaço vetorial. Pondera a frequência de um termo pela sua raridade no conjunto, destacando o que é característico de cada documento (aqui, cada período) em vez do que é apenas frequente.

Similaridade de cosseno: medida padrão no modelo vetorial, independente do tamanho do documento (PPAs de períodos diferentes têm volumes de texto diferentes). Não é correlação; é o ângulo entre vetores.

LDA: Blei, Ng e Jordan (2003). Modelo generativo probabilístico que trata cada documento como mistura de tópicos e cada tópico como distribuição de palavras. Captura padrões de co-ocorrência que análise termo a termo não pega.

Triangulação: TF-IDF e LDA partem de pressupostos diferentes. Quando apontam na mesma direção (ex: ganho de vocabulário de negócios e economia internacional), o achado é mais robusto.

Bibliotecas: pdfplumber (extração de texto de PDF com controle de layout e recorte de página), spaCy (modelo pt_core_news_lg com lematizador e POS tagger para português), scikit-learn (implementações de referência de TF-IDF, cosseno e LDA). Divisão: spaCy trata a linguagem, scikit-learn trata a vetorização e os modelos.

## Ressalvas metodológicas que precisam aparecer no texto

- Circularidade de palavra-chave (crítica do orientador): escolher termos e depois "achá-los" no texto. Resposta: expansão de léxico orientada por dados e comparação contra o vocabulário completo.
- Seleção manual de programas: declarar o critério (ver regras de negócio) e os casos de fronteira.
- Mudança de discurso versus mudança de composição da amostra: parte da variação vem de programas que entram e saem.
- Reaproveitamento textual entre ciclos.
- PPA mede intenção declarada, não execução.
- Caráter exploratório da contribuição.
