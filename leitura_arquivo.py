"""
leitura_arquivo.py
Leitura do arquivo texto que descreve o mapa.
"""

from grafo import Grafo


class DadosMapa:
    """Guarda tudo que foi lido do arquivo, ja organizado."""

    def __init__(self):
        self.grafo = Grafo()
        self.lab = None
        self.cmp = None
        self.estadio = None
        self.ginasios = []
        self.especies = []
        self.quantidades = {}
        self.fator_prazo = 10
        self.prazo_inscricao = 0

    def __str__(self):
        return (
            f"Mapa carregado:\n"
            f"  Vertices......: {self.grafo.num_vertices()}\n"
            f"  Arestas.......: {self.grafo.num_arestas()}\n"
            f"  Soma dos pesos: {self.grafo.soma_pesos()}\n"
            f"  Laboratorio...: {self.lab}\n"
            f"  CMP...........: {self.cmp}\n"
            f"  Estadio.......: {self.estadio}\n"
            f"  Ginasios......: {len(self.ginasios)}\n"
            f"  Especies......: {len(self.especies)}\n"
            f"  Quantidades...: {self.quantidades}\n"
            f"  Prazo (fator {self.fator_prazo}): {self.prazo_inscricao} unidades de tempo"
        )


def _linhas_uteis(caminho):
    """Le o arquivo e devolve so as linhas que interessam."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                yield linha


def ler_mapa(caminho):
    """Le o arquivo de mapa e retorna um objeto DadosMapa."""
    dados = DadosMapa()
    linhas = list(_linhas_uteis(caminho))
    i = 0
    while i < len(linhas):
        partes = linhas[i].split()
        chave = partes[0].upper()
        if chave == "VERTICES":
            quantidade = int(partes[1])
            for j in range(1, quantidade + 1):
                dados.grafo.adicionar_vertice(linhas[i + j])
            i += quantidade + 1
        elif chave == "ARESTAS":
            quantidade = int(partes[1])
            for j in range(1, quantidade + 1):
                u, v, peso = linhas[i + j].split()
                dados.grafo.adicionar_aresta(u, v, int(peso))
            i += quantidade + 1
        elif chave == "LAB":
            dados.lab = partes[1]
            dados.grafo.definir_info(partes[1], "tipo", "laboratorio")
            i += 1
        elif chave == "CMP":
            dados.cmp = partes[1]
            dados.grafo.definir_info(partes[1], "tipo", "cmp")
            i += 1
        elif chave == "ESTADIO":
            dados.estadio = partes[1]
            dados.grafo.definir_info(partes[1], "tipo", "estadio")
            i += 1
        elif chave == "GINASIOS":
            quantidade = int(partes[1])
            for j in range(1, quantidade + 1):
                vertice, lider, tipo, mobilidade = linhas[i + j].split()
                dados.ginasios.append({
                    "vertice": vertice,
                    "lider": lider,
                    "tipo": tipo,
                    "mobilidade": mobilidade,
                })
                dados.grafo.definir_info(vertice, "tipo", "ginasio")
                dados.grafo.definir_info(vertice, "lider", lider)
            i += quantidade + 1
        elif chave == "ESPECIES":
            quantidade = int(partes[1])
            for j in range(1, quantidade + 1):
                nome, tipo, evolucao, xp = linhas[i + j].split()
                dados.especies.append({
                    "nome": nome,
                    "tipo": tipo,
                    "evolucao": None if evolucao.upper() == "NENHUMA" else evolucao,
                    "xp_necessario": int(xp),
                })
            i += quantidade + 1
        elif chave == "QUANTIDADES":
            quantidade = int(partes[1])
            for j in range(1, quantidade + 1):
                nome, valor = linhas[i + j].split()
                dados.quantidades[nome] = int(valor)
            i += quantidade + 1
        elif chave == "FATOR_PRAZO":
            dados.fator_prazo = int(partes[1])
            i += 1
        else:
            raise ValueError(f"Linha nao reconhecida no arquivo: '{linhas[i]}'")
    _validar(dados)
    dados.prazo_inscricao = dados.fator_prazo * dados.grafo.soma_pesos()
    return dados


def _validar(dados):
    """Confere se o mapa lido faz sentido antes de comecar a simulacao."""
    especiais = {"laboratorio": dados.lab, "CMP": dados.cmp, "estadio": dados.estadio}
    vertices_ginasio = {g["vertice"] for g in dados.ginasios}
    for papel, vertice in especiais.items():
        if vertice is not None and vertice in vertices_ginasio:
            raise ValueError(
                f"O vertice '{vertice}' foi declarado como {papel} e tambem "
                "como ginasio. Cada local especial precisa de um vertice proprio."
            )
    ocupados = [v for v in especiais.values() if v is not None]
    if len(set(ocupados)) != len(ocupados):
        raise ValueError(
            "Laboratorio, CMP e estadio precisam estar em vertices diferentes."
        )
    if dados.lab is None:
        raise ValueError("O arquivo nao define o laboratorio (LAB).")
    if dados.cmp is None:
        raise ValueError("O arquivo nao define o Centro Medico Pokemon (CMP).")
    if dados.estadio is None:
        raise ValueError("O arquivo nao define o estadio da Liga (ESTADIO).")
    if len(dados.ginasios) < 8:
        raise ValueError(
            f"A regiao tem apenas {len(dados.ginasios)} ginasios; "
            "sao necessarios pelo menos 8 para a inscricao na Liga."
        )
    if not (10 <= dados.fator_prazo <= 15):
        raise ValueError(
            f"FATOR_PRAZO = {dados.fator_prazo}; o enunciado exige um valor entre 10 e 15."
        )
    if not dados.grafo.eh_conexo():
        raise ValueError(
            "O mapa nao e conexo: existem pontos inalcancaveis a partir do restante da regiao."
        )
