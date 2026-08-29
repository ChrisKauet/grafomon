"""
main.py
Menu de linha de comando do simulador "grafomon".
"""

import sys

from leitura_arquivo import ler_mapa


def mostrar_menu():
    print("\n" + "=" * 52)
    print("  GRAFOMON - simulador em grafo")
    print("=" * 52)
    print("  1. Mostrar o mapa (grafo completo)")
    print("  2. Caminho minimo entre dois pontos (Dijkstra)")
    print("  3. Distancias a partir do laboratorio")
    print("  4. Listar locais especiais")
    print("  5. Iniciar a jornada (simulacao)")
    print("  0. Sair")
    print("=" * 52)


def opcao_caminho_minimo(grafo):
    origem = input("Vertice de origem: ").strip()
    destino = input("Vertice de destino: ").strip()
    if origem not in grafo.adj or destino not in grafo.adj:
        print("Vertice inexistente no mapa.")
        return
    caminho, custo = grafo.caminho_minimo(origem, destino)
    if not caminho:
        print("Nao existe caminho entre esses pontos.")
    else:
        print(f"\nCaminho: {' -> '.join(caminho)}")
        print(f"Tempo total de viagem: {custo} unidades")


def opcao_distancias(grafo, origem):
    dist, _ = grafo.dijkstra(origem)
    print(f"\nDistancias a partir de {origem}:")
    for vertice in sorted(dist, key=dist.get):
        marca = grafo.info[vertice].get("tipo", "")
        rotulo = f" ({marca})" if marca else ""
        print(f"  {vertice}{rotulo}: {dist[vertice]}")


def opcao_locais(dados):
    grafo = dados.grafo
    print(f"\nLaboratorio do Prof. Carvalho: {dados.lab}")
    print(f"Centro Medico Pokemon (CMP)..: {dados.cmp}")
    print(f"Estadio da Liga..............: {dados.estadio}")
    print("\nGinasios da regiao:")
    for g in dados.ginasios:
        _, custo = grafo.caminho_minimo(dados.lab, g["vertice"])
        print(
            f"  {g['vertice']}: {g['lider']} (tipo {g['tipo']}, {g['mobilidade']})"
            f" - a {custo} unidades do laboratorio"
        )


def mostrar_status(sim):
    """Painel com o estado atual do treinador e da equipe."""
    jogador = sim.jogador
    print(f"\n--- {jogador.nome} em {jogador.posicao} ---")
    print(f"Tempo: {sim.tempo} / {sim.prazo} "
          f"(restam {sim.tempo_restante()} unidades)")
    print(f"Insignias: {len(jogador.insignias)}/8 | XP: {jogador.xp}")
    if jogador.ovo:
        falta = max(0, 100 - jogador.ovo.tempo_choco)
        print(f"Ovo na incubadora: choca em {falta} unidades")
    print("Equipe:")
    for i, pokemon in enumerate(jogador.pokemons, start=1):
        print(f"  {i}. {pokemon}")


def jogar(dados):
    """Loop principal da jornada, em linha de comando."""
    from simulacao import Simulacao
    sim = Simulacao(dados)
    nome = input("\nQual o seu nome, treinador? ").strip() or "Ash"
    resposta = input(
        "O Prof. Carvalho oferece tres pokemons iniciais "
        "(agua, fogo e planta). Aceita? [s/n] "
    ).strip().lower()
    sim.inicializar_entidades(nome_jogador=nome, aceitar_iniciais=(resposta != "n"))
    print("\n" + sim.registro[-1])
    mostrar_status(sim)
    while True:
        if sim.prazo_expirado():
            print("\nO prazo de inscricao expirou. Voce esta inapto para a Liga.")
            return
        if sim.jogador.inscrito:
            print("\nVoce esta inscrito na Liga Pokemon. Fim da jornada!")
            return
        encontros = sim.entidades_no_vertice(sim.jogador.posicao)
        vizinhos = sim.grafo.vizinhos(sim.jogador.posicao)
        print("\nCaminhos a partir daqui:")
        for vizinho, peso in sorted(vizinhos):
            marca = sim.grafo.info.get(vizinho, {}).get("tipo", "")
            rotulo = f" ({marca})" if marca else ""
            print(f"  {vizinho}{rotulo} - {peso} unidades")
        if encontros["lider"]:
            print(f"O lider {encontros['lider'].nome} esta aqui!")
        if encontros["selvagens"]:
            nomes = ", ".join(p.nome for p in encontros["selvagens"])
            print(f"Pokemons selvagens por perto: {nomes}")
        if encontros["itens"]:
            tipos = ", ".join(i.tipo for i in encontros["itens"])
            print(f"Itens no chao: {tipos}")
        print("\n  a <vertice>  andar ate um vizinho")
        print("  g            desafiar o lider daqui")
        print("  c            capturar um selvagem")
        print("  i            pegar os itens do local")
        print("  s            ver status")
        print("  r            rota mais curta ate um ponto")
        print("  x            encerrar a jornada")
        comando = input("> ").strip().split()
        if not comando:
            continue
        acao = comando[0].lower()
        if acao == "x":
            print("Jornada encerrada.")
            return
        elif acao == "s":
            mostrar_status(sim)
        elif acao == "a" and len(comando) > 1:
            custo = sim.andar_para(comando[1])
            if custo is None:
                print("Nao existe caminho direto para esse ponto.")
            else:
                print(f"Voce viajou {custo} unidades ate {sim.jogador.posicao}.")
                for linha in sim.registro[-3:]:
                    print(f"  {linha}")
        elif acao == "g":
            lider = encontros["lider"]
            if lider is None:
                print("Nao ha nenhum lider de ginasio aqui.")
            elif lider.ginasio in sim.jogador.insignias:
                print("Voce ja tem a insignia deste ginasio.")
            elif not sim.jogador.pode_batalhar():
                print("Sao necessarios 3 pokemons conscientes para batalhar.")
            else:
                marca = len(sim.registro)
                sim.desafiar_lider(lider)
                for linha in sim.registro[marca:]:
                    print(linha)
        elif acao == "c":
            import batalha
            if not encontros["selvagens"]:
                print("Nao ha pokemons selvagens aqui.")
            elif not sim.local_permite_batalha(sim.jogador.posicao):
                print("Batalhas sao proibidas neste local.")
            else:
                selvagem = encontros["selvagens"][0]
                marca = len(sim.registro)
                capturou = batalha.batalha_selvagem(
                    sim.jogador, selvagem, registro=sim.registro
                )
                if capturou:
                    sim.pokemons_selvagens.remove(selvagem)
                else:
                    selvagem.fugiu_de.add(sim.jogador.nome)
                for linha in sim.registro[marca:]:
                    print(linha)
                sim.avancar_tempo(1)
        elif acao == "i":
            if not encontros["itens"]:
                print("Nao ha itens neste local.")
            for item in encontros["itens"]:
                marca = len(sim.registro)
                sim.coletar_item(item)
                for linha in sim.registro[marca:]:
                    print(linha)
        elif acao == "r":
            destino = input("Ate qual ponto? ").strip()
            caminho, custo = sim.grafo.caminho_minimo(sim.jogador.posicao, destino)
            if not caminho:
                print("Nao existe caminho ate la.")
            else:
                print(f"Rota: {' -> '.join(caminho)} ({custo} unidades)")
        else:
            print("Comando nao reconhecido.")
        if (sim.jogador.posicao == dados.estadio
                and sim.jogador.pode_se_inscrever()):
            print("\n" + sim.tentar_inscricao())


def main():
    caminho_arquivo = sys.argv[1] if len(sys.argv) > 1 else "mapa.txt"
    try:
        dados = ler_mapa(caminho_arquivo)
    except FileNotFoundError:
        print(f"Arquivo '{caminho_arquivo}' nao encontrado.")
        return
    except ValueError as erro:
        print(f"Erro na leitura do mapa: {erro}")
        return
    print(dados)
    grafo = dados.grafo
    while True:
        mostrar_menu()
        escolha = input("Opcao: ").strip()
        if escolha == "1":
            print("\n" + str(grafo))
        elif escolha == "2":
            opcao_caminho_minimo(grafo)
        elif escolha == "3":
            opcao_distancias(grafo, dados.lab)
        elif escolha == "4":
            opcao_locais(dados)
        elif escolha == "5":
            try:
                jogar(dados)
            except ImportError:
                print("\nOs modulos de simulacao e batalha ainda nao estao "
                      "disponiveis. As opcoes de 1 a 4 continuam funcionando.")
        elif escolha == "0":
            print("Ate a proxima, treinador!")
            break
        else:
            print("Opcao invalida.")

if __name__ == "__main__":
    main()
