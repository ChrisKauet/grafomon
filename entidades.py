"""
entidades.py
Classes de dominio: Pokemon, Treinador e Item.
"""

import random

HP_MAXIMO = 100

HP_CONSCIENTE = 20

HP_CRITICO = 5

XP_PARA_EVOLUIR = 1000

MAX_POKEMONS = 6

MAX_TOTAL = 7

TEMPO_CHOCAR_OVO = 100


class Pokemon:
    """Um pokemon, selvagem ou pertencente a um treinador."""

    def __init__(self, nome, tipo, evolucao=None, posicao=None):
        self.nome = nome
        self.tipo = tipo
        self.evolucao = evolucao
        self.posicao = posicao
        self.fase = 1
        self.xp = 0
        self.hp = HP_MAXIMO
        self.ap_inicial = random.randint(10, 30)
        self.dp_inicial = random.randint(10, 30)
        self.ap_bonus = 0
        self.dp_bonus = 0
        self.tempo_inconsciente = 0
        self.tempo_no_cmp = 0
        self.no_cmp = False
        self.dono = None
        self.fugiu_de = set()
        self._distancia_para_xp = 0
        self._distancia_para_hp = 0

    def ataque_total(self):
        """AP atual = AP inicial + 10% do XP + bonus de batalhas."""
        total = self.ap_inicial + int(self.xp * 0.10) + self.ap_bonus
        if self.dono is not None:
            total += self.dono.xp
        return total

    def defesa_total(self):
        """DP atual = DP inicial + 10% do XP + bonus de batalhas."""
        total = self.dp_inicial + int(self.xp * 0.10) + self.dp_bonus
        if self.dono is not None:
            total += self.dono.xp
        return total

    def esta_consciente(self):
        """Pronto para batalhar: HP >= 20, sem desmaio e fora do CMP."""
        return (
            self.hp >= HP_CONSCIENTE
            and self.tempo_inconsciente <= 0
            and not self.no_cmp
        )

    def precisa_cmp(self):
        """Muito machucado (HP < 5): so se recupera no Centro Medico."""
        return self.hp < HP_CRITICO

    def receber_dano(self, dano):
        """Aplica dano ao HP e atualiza o estado do pokemon."""
        if dano <= 0:
            return
        self.hp = max(1, self.hp - dano)
        if self.hp < HP_CONSCIENTE and self.tempo_inconsciente <= 0:
            self.tempo_inconsciente = random.randint(10, 50)

    def curar(self, quantidade):
        """Cura por erva medicinal: +HP ate o maximo de 100."""
        if not self.esta_consciente():
            return False
        self.hp = min(HP_MAXIMO, self.hp + quantidade)
        return True

    def internar_no_cmp(self):
        """Entra no Centro Medico por um tempo aleatorio de 10 a 50 unidades."""
        self.no_cmp = True
        self.tempo_no_cmp = random.randint(10, 50)

    def sair_do_cmp(self):
        """Ao sair do CMP, o HP volta para 100."""
        self.no_cmp = False
        self.tempo_no_cmp = 0
        self.hp = HP_MAXIMO
        self.tempo_inconsciente = 0

    def ganhar_xp(self, quantidade):
        """Soma XP e verifica se o pokemon atingiu o limite para evoluir."""
        self.xp += quantidade
        if self.xp >= XP_PARA_EVOLUIR:
            return self.evoluir()
        return False

    def evoluir(self):
        """Passa para a proxima forma; AP e DP sobem 30%."""
        if self.evolucao is None or self.fase >= 3:
            return False
        self.nome = self.evolucao
        self.fase += 1
        self.ap_inicial = int(self.ap_inicial * 1.30)
        self.dp_inicial = int(self.dp_inicial * 1.30)
        self.evolucao = None
        return True

    def passar_tempo(self, unidades):
        """Aplica os efeitos da passagem do tempo sobre este pokemon."""
        if self.tempo_inconsciente > 0:
            self.tempo_inconsciente = max(0, self.tempo_inconsciente - unidades)
        if self.no_cmp:
            self.tempo_no_cmp -= unidades
            if self.tempo_no_cmp <= 0:
                self.sair_do_cmp()
            return
        if self.precisa_cmp():
            return
        self._distancia_para_hp += unidades
        while self._distancia_para_hp >= 10:
            self._distancia_para_hp -= 10
            self.hp = min(HP_MAXIMO, self.hp + 1)
        self._distancia_para_xp += unidades
        while self._distancia_para_xp >= 100:
            self._distancia_para_xp -= 100
            self.ganhar_xp(1)

    def __str__(self):
        if self.no_cmp:
            estado = "no CMP"
        elif self.precisa_cmp():
            estado = "muito machucado - precisa do CMP"
        elif self.tempo_inconsciente > 0:
            estado = f"inconsciente ({self.tempo_inconsciente}u)"
        elif not self.esta_consciente():
            estado = "inconsciente"
        else:
            estado = "pronto"
        return (
            f"{self.nome} ({self.tipo}) HP {self.hp}/100 "
            f"XP {self.xp} AP {self.ataque_total()} DP {self.defesa_total()} - {estado}"
        )


class Treinador:
    """Um treinador pokemon: o jogador, um rival ou um lider de ginasio."""

    def __init__(self, nome, posicao=None, eh_lider=False, ginasio=None):
        self.nome = nome
        self.posicao = posicao
        self.xp = 0
        self.pokemons = []
        self.ovo = None
        self.insignias = set()
        self.pokebolas = 7
        self.incubadora = True
        self.eh_lider = eh_lider
        self.ginasio = ginasio
        self.inscrito = False

    def pokemons_conscientes(self):
        """Lista dos pokemons prontos para batalhar."""
        return [p for p in self.pokemons if p.esta_consciente()]

    def pode_batalhar(self):
        """So e possivel desafiar outro treinador com 3 pokemons conscientes."""
        return len(self.pokemons_conscientes()) >= 3

    def adicionar_pokemon(self, pokemon):
        """Adiciona um pokemon a equipe."""
        pokemon.dono = self
        if len(self.pokemons) < MAX_POKEMONS:
            self.pokemons.append(pokemon)
            return True
        return False

    def total_pokemons(self):
        """Conta ativos + ovo nao chocado (o enunciado limita a 7)."""
        return len(self.pokemons) + (1 if self.ovo else 0)

    def pode_pegar_ovo(self):
        """So um ovo por vez, e o total (ativos + ovo) nao pode passar de 7."""
        return self.ovo is None and self.total_pokemons() < MAX_TOTAL

    def receber_insignia(self, nome_ginasio):
        """Guarda a insignia. E permanente, mesmo apos derrotas futuras."""
        self.insignias.add(nome_ginasio)

    def pode_se_inscrever(self):
        """Sao necessarias 8 insignias distintas para entrar na Liga."""
        return len(self.insignias) >= 8

    def ganhar_xp_vitoria(self, oponente):
        """+3 XP ao vencer alguem com XP maior ou igual; +1 caso contrario."""
        if oponente is not None and oponente.xp >= self.xp:
            self.xp += 3
        else:
            self.xp += 1

    def passar_tempo(self, unidades):
        """Repassa a passagem do tempo para todos os pokemons e para o ovo."""
        for pokemon in self.pokemons:
            pokemon.passar_tempo(unidades)
        if self.ovo is not None:
            self.ovo.tempo_choco += unidades

    def __str__(self):
        return (
            f"{self.nome} @ {self.posicao} | XP {self.xp} | "
            f"insignias {len(self.insignias)}/8 | pokemons {len(self.pokemons)}"
        )


class Item:
    """Item encontrado pelo caminho: erva medicinal ou ovo de pokemon."""

    def __init__(self, tipo, posicao=None):
        self.tipo = tipo
        self.posicao = posicao
        self.tempo_choco = 0
        self.coletado = False

    def pronto_para_chocar(self):
        """O ovo choca apos o equivalente a 100 unidades de distancia."""
        return self.tipo == "ovo" and self.tempo_choco >= TEMPO_CHOCAR_OVO

    def usar_erva(self, treinador):
        """Erva medicinal: +10 HP em todos os pokemons conscientes."""
        if self.tipo != "erva":
            return 0
        curados = 0
        for pokemon in treinador.pokemons:
            if pokemon.curar(10):
                curados += 1
        self.coletado = True
        return curados


if __name__ == "__main__":
    print(__doc__.strip())
    print("\nEste arquivo e um modulo: ele nao roda sozinho.")
    print("Para iniciar o simulador, execute executar.py.")
    try:
        input("\nPressione Enter para fechar...")
    except EOFError:
        pass
