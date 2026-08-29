"""
executar.py
Ponto de entrada do simulador "grafomon".
"""

import os
import sys
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from main import main


def _pausar():
    """Mantem a janela aberta quando o arquivo e executado por duplo clique."""
    try:
        input("\nPressione Enter para fechar...")
    except EOFError:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
    _pausar()
