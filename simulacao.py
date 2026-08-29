"""
simulacao.py
Motor de simulacao: relogio global e movimentacao no grafo.
"""

import random

from entidades import Pokemon, Treinador, Item

import batalha


class Simulacao:
    """Controla o relogio do jogo e o estado de todas as entidades."""

    def __init__(self, dados_mapa):
        self.dados = dados_mapa
        self.grafo = dados_mapa.grafo
        self.tempo = 0
        self.prazo = dados_mapa.prazo_inscricao
        self.jogador = None
        self.treinadores = []
        self.lideres = []
        self.pokemons_selvagens = []
        self.itens = []
        self.rocket = []
        self.registro = []

    def _sortear_vertice(self, exceto=None):
        """Escolhe um vertice qualquer do mapa. O(V)."""
        opcoes = [v for v in self.grafo.vertices() if v != exceto]
        return random.choice(opcoes)

    def _criar_pokemon(self, posicao=None, fase_inicial=True):
        """Cria um pokemon de uma especie sorteada do arquivo."""
        especies = self.dados.especies
        if fase_inicial:
            candidatas = [e for e in especies if e["evolucao"] is not None]
            especies = candidatas or especies
        especie = random.choice(especies)
        return Pokemon(
            nome=especie["nome"],
            tipo=especie["tipo"],
            evolucao=especie["evolucao"],
            posicao=posicao,
        )

    def _pokemons_iniciais(self, aceitar_os_tres=True):
        """Entrega os pokemons iniciais do Prof. Carvalho."""
        if not aceitar_os_tres:
            return [self._criar_pokemon(self.dados.lab)]
        escolhidos = []
        for tipo in ("agua", "fogo", "planta"):
            candidatas = [
                e for e in self.dados.especies
                if e["tipo"] == tipo and e["evolucao"] is not None
            ]
            if candidatas:
                especie = random.choice(candidatas)
                escolhidos.append(Pokemon(
                    nome=especie["nome"],
                    tipo=especie["tipo"],
                    evolucao=especie["evolucao"],
                    posicao=self.dados.lab,
                ))
        return escolhidos or [self._criar_pokemon(self.dados.lab)]

    def inicializar_entidades(self, nome_jogador="Ash", aceitar_iniciais=True):
        """Cria o jogador, os NPCs, os selvagens e os itens da regiao."""
        self.jogador = Treinador(nome_jogador, posicao=self.dados.lab)
        for pokemon in self._pokemons_iniciais(aceitar_iniciais):
            self.jogador.adicionar_pokemon(pokemon)
        for ordem, ginasio in enumerate(self.dados.ginasios):
            lider = Treinador(
                ginasio["lider"],
                posicao=ginasio["vertice"],
                eh_lider=True,
                ginasio=ginasio["vertice"],
            )
            lider.movel = (ginasio["mobilidade"] == "movel")
            lider.tipo_ginasio = ginasio["tipo"]
            xp_base = 20 + ordem * 40
            for _ in range(3):
                pokemon = self._criar_pokemon(ginasio["vertice"], fase_inicial=False)
                pokemon.xp = random.randint(xp_base, xp_base + 60)
                lider.adicionar_pokemon(pokemon)
            self.lideres.append(lider)
        for i in range(self.dados.quantidades.get("treinadores", 0)):
            posicao = self._sortear_vertice()
            treinador = Treinador(f"Treinador_{i+1}", posicao=posicao)
            treinador.xp = random.randint(0, 30)
            for _ in range(3):
                pokemon = self._criar_pokemon(posicao, fase_inicial=False)
                pokemon.xp = random.randint(0, 200)
                treinador.adicionar_pokemon(pokemon)
            self.treinadores.append(treinador)
        for _ in range(self.dados.quantidades.get("pokemons", 0)):
            posicao = self._sortear_vertice()
            pokemon = self._criar_pokemon(posicao, fase_inicial=False)
            pokemon.xp = random.randint(0, 150)
            self.pokemons_selvagens.append(pokemon)
        for _ in range(self.dados.quantidades.get("itens", 0)):
            tipo = random.choice(["erva", "ovo"])
            self.itens.append(Item(tipo, posicao=self._sortear_vertice()))
        self.registro.append(
            f"Regiao pronta: {len(self.lideres)} ginasios, "
            f"{len(self.treinadores)} treinadores, "
            f"{len(self.pokemons_selvagens)} selvagens, {len(self.itens)} itens."
        )

    def mover_entidade(self, entidade, destino):
        """Move a entidade para um vertice ADJACENTE ao atual."""
        for (vizinho, peso) in self.grafo.vizinhos(entidade.posicao):
            if vizinho == destino:
                entidade.posicao = destino
                return peso
        return None

    def mover_aleatorio(self, entidade):
        """Passeio aleatorio: sorteia um vizinho e move a entidade ate ele."""
        vizinhos = self.grafo.vizinhos(entidade.posicao)
        if not vizinhos:
            return 0
        destino, peso = random.choice(vizinhos)
        entidade.posicao = destino
        return peso

    def mover_demais_entidades(self):
        """Faz todos os NPCs darem um passo pelo mapa."""
        for lider in self.lideres:
            if not getattr(lider, "movel", False):
                continue
            if random.random() < 0.33 and lider.posicao != lider.ginasio:
                caminho, _ = self.grafo.caminho_minimo(lider.posicao, lider.ginasio)
                if len(caminho) > 1:
                    self.mover_entidade(lider, caminho[1])
                    continue
            self.mover_aleatorio(lider)
        for treinador in self.treinadores:
            self.mover_aleatorio(treinador)
        for selvagem in self.pokemons_selvagens:
            self.mover_aleatorio(selvagem)

    def avancar_tempo(self, unidades):
        """Avanca o relogio e aplica todos os efeitos dependentes do tempo."""
        if unidades <= 0:
            return
        self.tempo += unidades
        if self.jogador is not None:
            self.jogador.passar_tempo(unidades)
            self._verificar_ovo()
        for treinador in self.treinadores + self.lideres:
            treinador.passar_tempo(unidades)
        for selvagem in self.pokemons_selvagens:
            selvagem.passar_tempo(unidades)

    def _verificar_ovo(self):
        """Choca o ovo do jogador quando ele completa 100 unidades."""
        ovo = self.jogador.ovo
        if ovo is None or not ovo.pronto_para_chocar():
            return
        filhote = self._criar_pokemon(self.jogador.posicao)
        filhote.xp = 0
        self.jogador.ovo = None
        if self.jogador.adicionar_pokemon(filhote):
            self.registro.append(f"O ovo chocou: nasceu um {filhote.nome}!")
        else:
            self.registro.append(
                f"O ovo chocou ({filhote.nome}), mas a equipe esta cheia: "
                "enviado ao Prof. Carvalho."
            )

    def entidades_no_vertice(self, vertice):
        """Retorna o que esta em um dado vertice, para detectar encontros."""
        return {
            "treinadores": [t for t in self.treinadores if t.posicao == vertice],
            "lider": next(
                (l for l in self.lideres if l.posicao == vertice), None
            ),
            "selvagens": [
                p for p in self.pokemons_selvagens
                if p.posicao == vertice
                and self.jogador.nome not in p.fugiu_de
            ],
            "itens": [
                i for i in self.itens
                if i.posicao == vertice and not i.coletado
            ],
        }

    def prazo_expirado(self):
        """Verifica se o prazo de inscricao na Liga ja passou."""
        return self.tempo > self.prazo

    def tempo_restante(self):
        """Quanto ainda resta do prazo de inscricao."""
        return max(0, self.prazo - self.tempo)

    def local_permite_batalha(self, vertice):
        """Batalhas sao proibidas no CMP e no laboratorio (Requisito 7)."""
        tipo = self.grafo.info.get(vertice, {}).get("tipo")
        return tipo not in ("cmp", "laboratorio")

    def andar_para(self, destino):
        """Move o jogador um vertice e avanca o relogio pelo peso da aresta."""
        custo = self.mover_entidade(self.jogador, destino)
        if custo is None:
            return None
        self.avancar_tempo(custo)
        self.mover_demais_entidades()
        self._tratar_chegada()
        return custo

    def _tratar_chegada(self):
        """Aplica os efeitos de chegar em um vertice."""
        posicao = self.jogador.posicao
        tipo = self.grafo.info.get(posicao, {}).get("tipo")
        if tipo == "cmp":
            for pokemon in self.jogador.pokemons:
                if pokemon.hp < 100 and not pokemon.no_cmp:
                    pokemon.internar_no_cmp()
                    self.registro.append(
                        f"{pokemon.nome} (HP {pokemon.hp}) foi internado no CMP."
                    )

    def coletar_item(self, item):
        """Pega uma erva (usa na hora) ou um ovo (vai para a incubadora)."""
        if item.tipo == "erva":
            curados = item.usar_erva(self.jogador)
            self.registro.append(f"Erva usada: {curados} pokemons curados em 10 HP.")
            return True
        if not self.jogador.pode_pegar_ovo():
            self.registro.append("Nao e possivel carregar outro ovo agora.")
            return False
        item.coletado = True
        item.tempo_choco = 0
        self.jogador.ovo = item
        self.registro.append("Ovo colocado na incubadora (choca em 100 unidades).")
        return True

    def desafiar_lider(self, lider):
        """Desafia um lider de ginasio. Vencer rende a insignia."""
        if not self.local_permite_batalha(self.jogador.posicao):
            self.avancar_tempo(1)
            self.registro.append("Batalhas sao proibidas neste local.")
            return None
        vencedor, _ = batalha_treinadores_wrapper(self.jogador, lider, self.registro)
        self.avancar_tempo(1)
        if vencedor is self.jogador:
            self.jogador.receber_insignia(lider.ginasio)
            self.registro.append(
                f"Insignia de {lider.nome} conquistada! "
                f"Total: {len(self.jogador.insignias)}/8"
            )
        return vencedor

    def tentar_inscricao(self):
        """Inscricao na Liga: exige 8 insignias, estar no estadio e no prazo."""
        if self.jogador.posicao != self.dados.estadio:
            return "Voce precisa estar no estadio da Liga."
        if not self.jogador.pode_se_inscrever():
            return f"Voce tem apenas {len(self.jogador.insignias)} das 8 insignias."
        if self.prazo_expirado():
            return "O prazo de inscricao expirou. Voce esta inapto para a Liga."
        self.jogador.inscrito = True
        return "Inscricao confirmada! Voce esta na Liga Pokemon!"


def batalha_treinadores_wrapper(desafiante, desafiado, registro):
    """Encaminha para batalha.batalha_treinadores (mantido separado para"""
    return batalha.batalha_treinadores(desafiante, desafiado, registro)


class EquipeRocket(Treinador):
    """Time que rouba pokemons e insignias de outros treinadores."""

    def __init__(self, nome, posicao=None):
        super().__init__(nome, posicao=posicao)
        self.invisivel_ate = 0

    def fugir_para_longe(self, grafo, ponto_de_ataque):
        """Teleporta a equipe para um dos vertices mais distantes."""
        from grafo import INFINITO
        dist, _ = grafo.dijkstra(ponto_de_ataque)
        alcancaveis = [v for v, d in dist.items() if d != INFINITO]
        if not alcancaveis:
            return self.posicao
        alcancaveis.sort(key=lambda v: dist[v], reverse=True)
        corte = max(1, len(alcancaveis) // 3)
        self.posicao = random.choice(alcancaveis[:corte])
        return self.posicao

    def roubar(self, vitima, registro=None):
        """Rouba um pokemon ou uma insignia, mas so apos vencer o duelo."""
        vencedor, _ = batalha.batalha_treinadores(self, vitima, registro)
        if vencedor is not self:
            return None
        if vitima.pokemons:
            roubado = random.choice(vitima.pokemons)
            vitima.pokemons.remove(roubado)
            self.adicionar_pokemon(roubado)
            if registro is not None:
                registro.append(f"  A Equipe Rocket roubou {roubado.nome}!")
            return roubado
        if vitima.insignias:
            insignia = random.choice(list(vitima.insignias))
            vitima.insignias.remove(insignia)
            self.insignias.add(insignia)
            if registro is not None:
                registro.append(f"  A Equipe Rocket roubou uma insignia!")
            return insignia
        return None


if __name__ == "__main__":
    print(__doc__.strip())
    print("\nEste arquivo e um modulo: ele nao roda sozinho.")
    print("Para iniciar o simulador, execute executar.py.")
    try:
        input("\nPressione Enter para fechar...")
    except EOFError:
        pass
