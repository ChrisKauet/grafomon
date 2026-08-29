"""
executar.py
Ponto de entrada do simulador "grafomon".
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()
