# Referências

Materiais consultados durante o desenvolvimento do projeto.
As referências abaixo foram usadas para estudo dos algoritmos, como base
de implementação e para validação dos resultados obtidos. Trechos
adaptados de material de terceiros estão indicados no próprio código.

## Algoritmo de Dijkstra

**DIJKSTRA, E. W.** A note on two problems in connexion with graphs.
*Numerische Mathematik*, v. 1, n. 1, p. 269–271, 1959.
Artigo original em que o algoritmo foi publicado.

**CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C.**
*Algoritmos: teoria e prática*. 3. ed. Rio de Janeiro: Elsevier, 2012.
Capítulo 24 (Caminhos mínimos de origem única). Base para a
implementação com fila de prioridade e para a análise de complexidade
O((V + E) log V).

**BURSTEIN, M.** *Implementations of Dijkstra's shortest path algorithm
in different languages*. Disponível em:
<https://github.com/mburst/dijkstras-algorithm>. Acesso em: 28 ago. 2026.
Repositório com implementações do algoritmo em dez linguagens. Serviu de
base para a nossa implementação do método `dijkstra()` em `grafo.py`,
adaptada para a estrutura de lista de adjacência adotada no projeto. O
grafo de teste do repositório é reproduzido em `teste_grafo.py` para
verificação do resultado.

## Busca em largura e conectividade

**CORMEN, T. H. et al.** *Algoritmos: teoria e prática*. 3. ed.
Capítulo 22 (Busca em grafos elementares). Referência para a BFS usada
na verificação de conectividade do mapa, em O(V + E).

## Estruturas de dados

**PYTHON SOFTWARE FOUNDATION.** *heapq — Heap queue algorithm*.
Documentação oficial do Python. Disponível em:
<https://docs.python.org/3/library/heapq.html>.
Módulo da biblioteca padrão usado como fila de prioridade no Dijkstra.
O enunciado permite explicitamente o uso de bibliotecas para estruturas
de dados clássicas (listas, pilhas, filas, heaps), exigindo apenas que
os algoritmos vistos em sala sejam implementados manualmente.

## Enunciado

**LIMA, C. V. G. C.** *Projeto: grafomon*. Disciplina de
Algoritmos em Grafos, CCT/UFCA, 1º semestre de 2026.
