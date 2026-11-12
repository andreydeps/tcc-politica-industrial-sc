# Procedimentos metodológicos (rascunho)

Rascunho para a seção de metodologia da monografia. Os números refletem o corpus de 09/11/2026 (seis ciclos de PPA, 41 programas selecionados) e devem ser atualizados se a lista de programas ou os PPAs mudarem. Trechos entre colchetes dependem de confirmação.

Figura associada: `saidas/figura_conceitual_metodo.png`.

## Fontes e unidades de análise

Os dados provêm dos Planos Plurianuais (PPAs) do estado de Santa Catarina, nos seis ciclos de 2004-2007 a 2024-2027. De cada plano utilizou-se o Anexo Único, que descreve os programas de governo. Cada programa é identificado por um código de quatro dígitos e organizado em campos: nome, órgão responsável, objetivo, justificativa e público-alvo. Programa e campo são, portanto, categorias da estrutura do documento. A expressão "política industrial", por sua vez, designa uma classificação analítica que o pesquisador atribui aos programas, e não uma propriedade do documento.

## Extração e seleção dos programas

A extração dos programas foi automática, por expressões regulares ajustadas ao formato de cada ciclo. Os rótulos do documento servem apenas como delimitadores de campo e não participam de nenhuma decisão sobre o conteúdo. Como o Anexo Único é um documento semiestruturado, com rótulos fixos, a separação dos campos é um problema de análise da estrutura do documento. O processamento de linguagem natural incide somente sobre o conteúdo dos campos, depois dessa etapa.

A seleção dos programas de política industrial foi manual e seguiu o conceito de ação de governo voltada a alterar a estrutura setorial da produção ou a elevar a competitividade e a capacidade tecnológica de atividades específicas (Chang, 1994; Rodrik, 2004, 2008). Na perspectiva da complexidade econômica adotada no trabalho, interessam os programas que ajudam a economia a se diversificar em direção a atividades mais complexas, como o fomento à produção, à inovação, à competitividade empresarial e à inserção internacional. Política social, gestão pública, saúde, segurança e educação básica ficaram de fora. O nome do programa orientou a triagem e o objetivo confirmou a inclusão. A justificativa não foi usada como critério. Os casos de fronteira [foram submetidos à validação do orientador, confirmar antes de entregar].

A numeração dos códigos não é a mesma em todos os ciclos. No PPA 2004-2007, por exemplo, o código 0200 identifica um programa de agroindústrias familiares, enquanto nos ciclos seguintes identifica o programa de competitividade. Por isso, a continuidade de um programa ao longo do tempo não se apoia no código, e sim em uma tabela de equivalência elaborada pelo pesquisador [validar com o orientador].

## Tratamento do texto

O texto analisado de cada programa é a concatenação de objetivo e justificativa. O nome do programa não entra na análise textual, por ser curto demais, e serve apenas à seleção. O texto foi lematizado com o modelo pt_core_news_lg da biblioteca spaCy, mantendo-se apenas substantivos, verbos e adjetivos, em minúsculas e sem palavras funcionais.

## Análises

A comparação entre ciclos utiliza o TF-IDF calculado sobre o conjunto de textos de cada período e a similaridade de cosseno entre os vetores resultantes. O léxico de termos-chave foi definido inicialmente pelo pesquisador e depois avaliado de duas formas. A primeira é a expansão a partir dos próprios dados, por coocorrência de termos e por proximidade entre vetores de palavras. A segunda é um conjunto de testes que compara a trajetória de cada termo com a que se obteria ao acaso, por permutação dos programas entre períodos, e com a de termos de frequência semelhante. Esses procedimentos respondem ao risco de circularidade, isto é, de que a escolha prévia das palavras determine o resultado.

## Limitações

Algumas limitações condicionam a interpretação dos resultados. O PPA registra a intenção declarada de política, e não a política executada. O corpus é pequeno, com quatro a oito programas por período, o que limita a inferência estatística e a estabilidade dos modelos de tópicos. Vários programas repetem objetivo e justificativa de um ciclo a outro, de modo que parte da similaridade entre ciclos vizinhos reflete herança textual. Os textos do ciclo 2004-2007 são mais curtos que os dos demais, o que reduz a comparabilidade desse período. Por fim, a seleção dos programas é manual, e os resultados dependem dela.
