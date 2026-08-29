"""
grafo.py
Estrutura de grafo ponderado e algoritmos sobre ele.
"""

import heapq

import sys

INFINITO = sys.maxsize


class Grafo:
    """Grafo ponderado, nao-direcionado, com metadados por vertice."""

    def __init__(self):
        self.adj = {}
        self.info = {}

    def adicionar_vertice(self, v, info=None):
        """Adiciona um vertice ao grafo. O(1)."""
        if v not in self.adj:
            self.adj[v] = []
            self.info[v] = {}
        if info:
            self.info[v].update(info)

    def adicionar_aresta(self, u, v, peso):
        """Adiciona uma aresta nao-direcionada entre u e v. O(1)."""
        if peso < 0:
            raise ValueError("Pesos negativos nao sao permitidos (Dijkstra exige peso >= 0).")
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        self.adj[u].append((v, peso))
        self.adj[v].append((u, peso))

    def definir_info(self, v, chave, valor):
        """Marca uma informacao no vertice (ex.: definir_info('v5','tipo','cmp'))."""
        self.adicionar_vertice(v)
        self.info[v][chave] = valor

    def vertices(self):
        """Retorna a lista de todos os vertices. O(V)."""
        return list(self.adj.keys())

    def vizinhos(self, v):
        """Retorna a lista [(vizinho, peso), ...] de um vertice. O(1)."""
        return self.adj.get(v, [])

    def num_vertices(self):
        return len(self.adj)

    def num_arestas(self):
        """Cada aresta foi guardada duas vezes, por isso a divisao por 2. O(V)."""
        return sum(len(lista) for lista in self.adj.values()) // 2

    def soma_pesos(self):
        """Soma o peso de todas as arestas do grafo. O(V + E)."""
        total = 0
        for u in self.adj:
            for (_, peso) in self.adj[u]:
                total += peso
        return total // 2 if total % 2 == 0 else total / 2

    def buscar_vertices_por_tipo(self, tipo):
        """Retorna todos os vertices marcados com um dado tipo. O(V)."""
        return [v for v in self.info if self.info[v].get("tipo") == tipo]

    def bfs(self, origem):
        """Busca em largura a partir de 'origem'."""
        if origem not in self.adj:
            return set()
        visitados = {origem}
        fila = [origem]
        i = 0
        while i < len(fila):
            atual = fila[i]
            i += 1
            for (vizinho, _) in self.adj[atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        return visitados

    def eh_conexo(self):
        """Verifica se todos os vertices sao alcancaveis entre si. O(V + E)."""
        if not self.adj:
            return True
        origem = next(iter(self.adj))
        return len(self.bfs(origem)) == self.num_vertices()

    def dijkstra(self, origem):
        """Calcula a distancia minima de 'origem' para todos os vertices."""
        if origem not in self.adj:
            raise ValueError(f"Vertice de origem '{origem}' nao existe no grafo.")
        dist = {}
        pred = {}
        fila = []
        for vertice in self.adj:
            if vertice == origem:
                dist[vertice] = 0
                heapq.heappush(fila, [0, vertice])
            else:
                dist[vertice] = INFINITO
                heapq.heappush(fila, [INFINITO, vertice])
            pred[vertice] = None
        while fila:
            menor = heapq.heappop(fila)[1]
            if dist[menor] == INFINITO:
                break
            for (vizinho, peso) in self.adj[menor]:
                alternativa = dist[menor] + peso
                if alternativa < dist[vizinho]:
                    dist[vizinho] = alternativa
                    pred[vizinho] = menor
                    for entrada in fila:
                        if entrada[1] == vizinho:
                            entrada[0] = alternativa
                            break
                    heapq.heapify(fila)
        return dist, pred

    def caminho_minimo(self, origem, destino):
        """Retorna (caminho, custo) do caminho minimo entre dois vertices."""
        dist, pred = self.dijkstra(origem)
        if destino not in dist or dist[destino] == INFINITO:
            return [], INFINITO
        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = pred[atual]
        caminho.reverse()
        return caminho, dist[destino]

    def vertice_mais_distante(self, origem):
        """Retorna o vertice alcancavel mais distante da origem. O((V+E) log V)."""
        dist, _ = self.dijkstra(origem)
        alcancaveis = {v: d for v, d in dist.items() if d != INFINITO}
        return max(alcancaveis, key=alcancaveis.get)

    def __str__(self):
        """Impressao legivel do grafo"""
        linhas = [f"Grafo: {self.num_vertices()} vertices, {self.num_arestas()} arestas"]
        for v in sorted(self.adj):
            marcas = self.info[v].get("tipo", "")
            rotulo = f"{v} [{marcas}]" if marcas else v
            vizinhos = ", ".join(f"{n}({p})" for n, p in sorted(self.adj[v]))
            linhas.append(f"  {rotulo} -> {vizinhos}")
        return "\n".join(linhas)
