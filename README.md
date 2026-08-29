# grafomon

Projeto da disciplina **Algoritmos em Grafos** — CCT/UFCA, 1º semestre de 2026
Prof. Carlos Vinicius G. C. Lima

Simulador de uma jornada Pokémon modelada como um **grafo ponderado não-direcionado**,
onde os vértices são pontos da região, as arestas são caminhos e os pesos representam
o tempo necessário para percorrê-los.

## Como executar

Requisitos: **Python 3.8 ou superior**. Não há dependências externas.

```bash
python executar.py
```

Para usar outro arquivo de mapa:

```bash
python executar.py meu_mapa.txt
```

Para rodar os testes:

```bash
python teste_grafo.py   # testes da estrutura de grafo
python teste_simulacao.py        # teste de integracao (jornada automatica)
```

## Estrutura dos arquivos

```
.
├── executar.py            Ponto de entrada do programa
├── grafo.py               Classe Grafo, Dijkstra e BFS
├── leitura_arquivo.py     Leitura e validação do arquivo de mapa
├── main.py                Menu de linha de comando
├── teste_grafo.py         Testes da estrutura de grafo
├── simulacao.py           Relógio global, movimentação e Equipe Rocket
├── entidades.py           Classes Pokemon, Treinador e Item
├── batalha.py             Regras de combate e vantagens de tipo
├── teste_simulacao.py     Teste de integração
├── mapa.txt               Mapa de exemplo da região
├── README.md
└── REFERENCIAS.md
```


## Operações sobre o grafo

- **Dijkstra** com fila de prioridade — caminho mínimo entre pontos da região.
  Usado no menu, na navegação do jogador e na fuga da Equipe Rocket.
- **BFS**, `O(V+E)` — validação da conectividade do mapa na leitura do arquivo.
- **Soma dos pesos das arestas**, `O(V+E)` — cálculo do prazo de inscrição na Liga.
- **Percurso sobre a lista de adjacência**, `O(1)` por passo — movimentação das
  entidades, um vértice por vez, conforme o requisito 7 do enunciado.

## Escolhas de implementação

**Lista de adjacência em vez de matriz.** O mapa de uma região é um grafo esparso,
então a lista gasta bem menos memória que uma matriz e permite percorrer apenas os
vizinhos que existem de fato.

**Dijkstra em vez de BFS para rotas.** BFS minimiza o *número de arestas*, mas aqui
o que importa é a *soma dos pesos* (o tempo de viagem). Bellman-Ford foi descartado
por não haver pesos negativos, e Floyd-Warshall (`O(V³)`) por não precisarmos de
distâncias de todos para todos.

**Grafo desacoplado do domínio.** O módulo `grafo.py` não conhece nada de Pokémon —
só vértices, arestas e pesos. As regras do jogo ficam nos módulos superiores.

## Formato do arquivo de mapa

O arquivo é texto puro. Linhas iniciadas por `#` e linhas em branco são ignoradas.
Cada seção começa com uma palavra-chave seguida da quantidade de linhas.

```
VERTICES 10        # depois, um nome de vértice por linha
ARESTAS 14         # depois, "<origem> <destino> <peso>" por linha
LAB v0             # laboratório do Prof. Carvalho (ponto de partida)
CMP v5             # Centro Médico Pokémon
ESTADIO v9         # estádio da Liga
GINASIOS 8         # "<vértice> <líder> <tipo> <fixo|movel>"
ESPECIES 9         # "<nome> <tipo> <evolução|NENHUMA> <xp_necessário>"
QUANTIDADES 3      # "<pokemons|treinadores|itens> <quantidade>"
FATOR_PRAZO 12     # entre 10 e 15 (requisito 6)
```

O prazo de inscrição na Liga é calculado como
`FATOR_PRAZO × soma de todos os pesos das arestas`.

## Referências

- **DIJKSTRA, E. W.** A note on two problems in connexion with graphs.
  *Numerische Mathematik*, v. 1, p. 269–271, 1959. Artigo original do algoritmo.
- **CORMEN, T. H. et al.** *Algoritmos: teoria e prática*. 3. ed. Elsevier, 2012.
  Capítulos 22 (busca em grafos) e 24 (caminhos mínimos de origem única).
- **BURSTEIN, M.** *Implementations of Dijkstra's shortest path algorithm in
  different languages*. Disponível em <https://github.com/mburst/dijkstras-algorithm>.
  Acesso em 28 ago. 2026. Repositório consultado durante o estudo do algoritmo.
  O grafo de teste utilizado naquele projeto foi reaproveitado em
  `teste_grafo.py` para validar nossa implementação: ambos encontram o
  caminho mínimo `A -> B -> F -> H`.
  Nossa implementação de `dijkstra()` segue a estratégia desse repositório
  (atualização da chave na fila seguida de `heapify`), adaptada para a nossa
  lista de adjacência e para retornar distâncias e predecessores. O grafo de
  teste de lá é reproduzido em `teste_grafo.py` e ambos encontram o mesmo
  caminho mínimo.
- **PYTHON SOFTWARE FOUNDATION.** *heapq — Heap queue algorithm*.
  <https://docs.python.org/3/library/heapq.html>. Fila de prioridade usada no
  Dijkstra. O enunciado permite bibliotecas de estruturas de dados clássicas
  (listas, pilhas, filas, heaps), exigindo apenas que os algoritmos vistos em
  sala sejam implementados manualmente — como é o caso aqui.

## Vídeo de explicação

[- _(link)_](https://youtu.be/DJV9XlgOGd8)
