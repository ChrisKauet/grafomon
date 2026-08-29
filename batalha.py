"""
batalha.py
Regras de combate entre pokemons e treinadores.
"""

import random

CHANCE_MAXIMA = 0.50

ESCALA_XP = 1000.0

VANTAGENS = {
    "agua":      ["fogo", "terra", "pedra"],
    "fogo":      ["planta", "gelo", "inseto"],
    "planta":    ["agua", "terra", "pedra"],
    "eletrico":  ["agua", "voador"],
    "terra":     ["fogo", "eletrico", "pedra", "venenoso"],
    "pedra":     ["fogo", "gelo", "voador", "inseto"],
    "psiquico":  ["venenoso", "lutador"],
    "venenoso":  ["planta"],
    "gelo":      ["planta", "terra", "voador"],
    "lutador":   ["pedra", "gelo"],
    "voador":    ["planta", "lutador", "inseto"],
    "inseto":    ["planta", "psiquico"],
    "fantasma":  ["psiquico", "fantasma"],
}

MULTIPLICADOR_VANTAGEM = 2.0

MULTIPLICADOR_DESVANTAGEM = 0.5


def multiplicador_de_tipo(atacante, defensor):
    """Retorna o multiplicador de dano pela vantagem de tipo."""
    if defensor.tipo in VANTAGENS.get(atacante.tipo, []):
        return MULTIPLICADOR_VANTAGEM
    if atacante.tipo in VANTAGENS.get(defensor.tipo, []):
        return MULTIPLICADOR_DESVANTAGEM
    return 1.0


def calcular_dano(atacante, defensor):
    """Dano basico = AP do atacante - DP do defensor."""
    bruto = atacante.ataque_total() - defensor.defesa_total()
    if bruto <= 0:
        return 0
    return int(bruto * multiplicador_de_tipo(atacante, defensor))


def _probabilidade_por_xp(pokemon_a, pokemon_b):
    """Converte a diferenca de XP entre dois pokemons em probabilidade."""
    diferenca = abs(pokemon_a.xp - pokemon_b.xp)
    return min(CHANCE_MAXIMA, diferenca / ESCALA_XP)


def tentar_esquiva(atacante, defensor):
    """True se o defensor esquivou do ataque (o ataque nao surte efeito)."""
    return random.random() < _probabilidade_por_xp(atacante, defensor)


def tentar_critico(atacante, defensor):
    """True se o ataque causa o dobro do dano."""
    return random.random() < _probabilidade_por_xp(atacante, defensor)


def turno_de_ataque(atacante, defensor, registro=None):
    """Executa um turno completo de ataque."""
    if tentar_esquiva(atacante, defensor):
        if registro is not None:
            registro.append(f"    {defensor.nome} esquivou do ataque de {atacante.nome}")
        return 0
    dano = calcular_dano(atacante, defensor)
    if dano > 0 and tentar_critico(atacante, defensor):
        dano *= 2
        if registro is not None:
            registro.append(f"    {atacante.nome} acertou um golpe critico!")
    defensor.receber_dano(dano)
    if registro is not None:
        registro.append(
            f"    {atacante.nome} causou {dano} de dano em {defensor.nome} "
            f"(HP {defensor.hp}/100)"
        )
    return dano


def _premiar_vencedor(vencedor, perdedor):
    """Aplica os ganhos de XP, AP e DP apos um duelo entre pokemons."""
    if perdedor.xp >= vencedor.xp:
        vencedor.ap_bonus += 1
        vencedor.dp_bonus += 1
    vencedor.ganhar_xp(10)
    perdedor.ganhar_xp(3)


def batalha_pokemon(pokemon_a, pokemon_b, quem_comeca=None, registro=None):
    """Duelo entre dois pokemons ate um deles ficar inconsciente."""
    atacante = quem_comeca if quem_comeca is not None else pokemon_a
    defensor = pokemon_b if atacante is pokemon_a else pokemon_a
    for _ in range(200):
        turno_de_ataque(atacante, defensor, registro)
        if not defensor.esta_consciente():
            _premiar_vencedor(atacante, defensor)
            return atacante, defensor
        atacante, defensor = defensor, atacante
    if pokemon_a.hp >= pokemon_b.hp:
        return pokemon_a, pokemon_b
    return pokemon_b, pokemon_a


def batalha_treinadores(desafiante, desafiado, registro=None):
    """Batalha 3x3 entre dois treinadores. O desafiado comeca atacando."""
    if not desafiante.pode_batalhar() or not desafiado.pode_batalhar():
        return None, None
    equipe_desafiante = desafiante.pokemons_conscientes()[:3]
    equipe_desafiado = desafiado.pokemons_conscientes()[:3]
    if registro is not None:
        registro.append(f"  Batalha: {desafiante.nome} desafia {desafiado.nome}")
    indice_a = 0
    indice_b = 0
    while indice_a < len(equipe_desafiante) and indice_b < len(equipe_desafiado):
        lutador_a = equipe_desafiante[indice_a]
        lutador_b = equipe_desafiado[indice_b]
        vencedor, _ = batalha_pokemon(
            lutador_a, lutador_b, quem_comeca=lutador_b, registro=registro
        )
        if vencedor is lutador_a:
            indice_b += 1
        else:
            indice_a += 1
    if indice_b >= len(equipe_desafiado):
        vencedor, perdedor = desafiante, desafiado
    else:
        vencedor, perdedor = desafiado, desafiante
    vencedor.ganhar_xp_vitoria(perdedor)
    if registro is not None:
        registro.append(f"  Vencedor: {vencedor.nome}")
    return vencedor, perdedor


def batalha_selvagem(treinador, pokemon_selvagem, desistir=False, registro=None):
    """Batalha para capturar um pokemon selvagem."""
    conscientes = treinador.pokemons_conscientes()
    if not conscientes:
        return False
    lutador = conscientes[0]
    if registro is not None:
        registro.append(
            f"  {treinador.nome} enfrenta {pokemon_selvagem.nome} selvagem"
        )
    if desistir:
        turno_de_ataque(pokemon_selvagem, lutador, registro)
        pokemon_selvagem.fugiu_de.add(treinador.nome)
        return False
    vencedor, perdedor = batalha_pokemon(lutador, pokemon_selvagem, registro=registro)
    if vencedor is not lutador:
        return False
    treinador.xp += 3
    lutador.ganhar_xp(3)
    pokemon_selvagem.ganhar_xp(3)
    capturado = treinador.adicionar_pokemon(pokemon_selvagem)
    if registro is not None:
        if capturado:
            registro.append(f"  {pokemon_selvagem.nome} foi capturado!")
        else:
            registro.append(
                f"  {pokemon_selvagem.nome} capturado, mas a equipe esta cheia: "
                f"enviado ao Prof. Carvalho"
            )
    return True
