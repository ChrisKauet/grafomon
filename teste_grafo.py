"""
teste_grafo.py
Testes da estrutura de grafo.
"""

from grafo import Grafo


def teste_grafo_pequeno():
    """Grafo montado a mao, com resposta conhecida."""
    g = Grafo()
    g.adicionar_aresta("a", "b", 1)
    g.adicionar_aresta("a", "c", 4)
    g.adicionar_aresta("b", "d", 2)
    g.adicionar_aresta("c", "d", 1)
    dist, _ = g.dijkstra("a")
    assert dist["a"] == 0, "distancia da origem ate ela mesma deve ser 0"
    assert dist["b"] == 1, f"esperado 1, obtido {dist['b']}"
    assert dist["d"] == 3, f"esperado 3, obtido {dist['d']}"
    assert dist["c"] == 4, f"esperado 4, obtido {dist['c']}"
    caminho, custo = g.caminho_minimo("a", "d")
    assert caminho == ["a", "b", "d"], f"caminho inesperado: {caminho}"
    assert custo == 3
    print("OK - dijkstra e caminho_minimo")


def teste_conectividade():
    """Grafo desconexo deve ser detectado pelo BFS."""
    g = Grafo()
    g.adicionar_aresta("a", "b", 1)
    g.adicionar_vertice("z")
    assert not g.eh_conexo(), "deveria detectar que 'z' esta isolado"
    g.adicionar_aresta("b", "z", 5)
    assert g.eh_conexo(), "agora o grafo deveria ser conexo"
    print("OK - bfs e verificacao de conectividade")


def teste_soma_pesos():
    """A soma nao pode contar cada aresta duas vezes."""
    g = Grafo()
    g.adicionar_aresta("a", "b", 3)
    g.adicionar_aresta("b", "c", 7)
    assert g.soma_pesos() == 10, f"esperado 10, obtido {g.soma_pesos()}"
    assert g.num_arestas() == 2
    print("OK - soma_pesos e num_arestas")


def teste_mais_distante():
    """Verifica a busca do vertice mais distante (usado pela Equipe Rocket)."""
    g = Grafo()
    g.adicionar_aresta("a", "b", 1)
    g.adicionar_aresta("b", "c", 1)
    g.adicionar_aresta("c", "d", 10)
    assert g.vertice_mais_distante("a") == "d"
    print("OK - vertice_mais_distante")


def teste_grafo_de_referencia():
    """Valida nossa implementacao contra um caso de teste publico."""
    g = Grafo()
    g.adicionar_aresta("A", "B", 7)
    g.adicionar_aresta("A", "C", 8)
    g.adicionar_aresta("B", "F", 2)
    g.adicionar_aresta("C", "F", 6)
    g.adicionar_aresta("C", "G", 4)
    g.adicionar_aresta("D", "F", 8)
    g.adicionar_aresta("E", "H", 1)
    g.adicionar_aresta("F", "G", 9)
    g.adicionar_aresta("F", "H", 3)
    caminho, custo = g.caminho_minimo("A", "H")
    assert caminho == ["A", "B", "F", "H"], f"caminho inesperado: {caminho}"
    assert custo == 12, f"esperado custo 12, obtido {custo}"
    print("OK - confere com o caso de teste de referencia (A -> B -> F -> H)")

if __name__ == "__main__":
    teste_grafo_pequeno()
    teste_grafo_de_referencia()
    teste_conectividade()
    teste_soma_pesos()
    teste_mais_distante()
    print("\nTodos os testes passaram.")
