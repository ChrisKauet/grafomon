"""
teste_simulacao.py
Teste de integracao: jornada automatica completa.
"""

import random

from leitura_arquivo import ler_mapa

from simulacao import Simulacao, EquipeRocket


def ginasio_mais_proximo(sim, dados, tentativas):
    """Escolhe o ginasio pendente mais proximo, usando Dijkstra."""
    dist, _ = sim.grafo.dijkstra(sim.jogador.posicao)
    pendentes = [
        g["vertice"] for g in dados.ginasios
        if g["vertice"] not in sim.jogador.insignias
        and tentativas[g["vertice"]] < 3
    ]
    if not pendentes:
        return None
    return min(pendentes, key=lambda v: dist[v])


def batalha_selvagem_segura(sim, selvagem):
    """Tenta capturar um selvagem sem arriscar a equipe inteira."""
    import batalha
    return batalha.batalha_selvagem(sim.jogador, selvagem, registro=sim.registro)


def dar_um_passo_ate(sim, destino):
    """Anda uma aresta na direcao do destino, seguindo o caminho minimo."""
    caminho, _ = sim.grafo.caminho_minimo(sim.jogador.posicao, destino)
    if len(caminho) > 1:
        sim.andar_para(caminho[1])
        return False
    return True


def main():
    random.seed(7)
    dados = ler_mapa("mapa.txt")
    sim = Simulacao(dados)
    sim.inicializar_entidades(nome_jogador="Kauet")
    print(f"Prazo de inscricao: {sim.prazo} unidades de tempo")
    print(f"Inicio em {sim.jogador.posicao} com {len(sim.jogador.pokemons)} pokemons:")
    for p in sim.jogador.pokemons:
        print(f"  - {p}")
    tentativas = {g["vertice"]: 0 for g in dados.ginasios}
    print("\n--- Jornada automatica ---")
    for _ in range(3000):
        if sim.prazo_expirado():
            print(f"\nO prazo expirou no tempo {sim.tempo}.")
            break
        if sim.jogador.inscrito:
            break
        if sim.jogador.pode_se_inscrever():
            if dar_um_passo_ate(sim, dados.estadio):
                print("\n" + sim.tentar_inscricao())
                break
            continue
        em_forma = [p for p in sim.jogador.pokemons
                    if p.esta_consciente() and p.hp >= 60]
        internados = [p for p in sim.jogador.pokemons if p.no_cmp]
        if len(em_forma) < 3 and not internados:
            if sim.jogador.posicao != dados.cmp:
                dar_um_passo_ate(sim, dados.cmp)
                continue
        if internados:
            sim.avancar_tempo(5)
            sim.mover_demais_entidades()
            continue
        if not sim.jogador.pode_batalhar():
            sim.avancar_tempo(10)
            sim.mover_demais_entidades()
            continue
        encontros = sim.entidades_no_vertice(sim.jogador.posicao)
        for item in encontros["itens"]:
            sim.coletar_item(item)
        if encontros["selvagens"] and sim.local_permite_batalha(sim.jogador.posicao):
            selvagem = encontros["selvagens"][0]
            if batalha_selvagem_segura(sim, selvagem):
                sim.pokemons_selvagens.remove(selvagem)
            else:
                selvagem.fugiu_de.add(sim.jogador.nome)
            sim.avancar_tempo(1)
            sim.mover_demais_entidades()
            continue
        lider = encontros["lider"]
        if (lider is not None
                and lider.ginasio not in sim.jogador.insignias
                and tentativas[lider.ginasio] < 3
                and sim.local_permite_batalha(sim.jogador.posicao)):
            vencedor = sim.desafiar_lider(lider)
            if vencedor is not sim.jogador:
                tentativas[lider.ginasio] += 1
            else:
                tentativas[lider.ginasio] = 0
            continue
        alvo = ginasio_mais_proximo(sim, dados, tentativas)
        if alvo is None:
            for vertice in tentativas:
                tentativas[vertice] = 0
            sim.avancar_tempo(1)
            sim.mover_demais_entidades()
            continue
        if dar_um_passo_ate(sim, alvo):
            sim.avancar_tempo(1)
    print(f"\nTempo decorrido: {sim.tempo} de {sim.prazo}")
    print(f"Insignias: {len(sim.jogador.insignias)}/8")
    print(f"XP do treinador: {sim.jogador.xp}")
    print(f"Inscrito na Liga: {'sim' if sim.jogador.inscrito else 'nao'}")
    print("\nEquipe final:")
    for p in sim.jogador.pokemons:
        print(f"  - {p}")
    print("\n--- Ultimos acontecimentos ---")
    for linha in sim.registro[-10:]:
        print(linha)
    print("\n--- Equipe Rocket ---")
    rocket = EquipeRocket("Equipe Rocket", posicao=dados.lab)
    ponto_ataque = sim.jogador.posicao
    destino = rocket.fugir_para_longe(sim.grafo, ponto_ataque)
    dist, _ = sim.grafo.dijkstra(ponto_ataque)
    print(f"Derrotada em {ponto_ataque}, teleportada para {destino} "
          f"(a {dist[destino]} unidades de distancia)")
    print("\nSimulacao concluida sem erros.")

if __name__ == "__main__":
    main()
