# -*- coding: utf-8 -*-
"""
Executa um ou mais notebooks .ipynb via nbclient, embutindo outputs/graficos
reais. O kernel roda com cwd = pasta do proprio notebook (normalmente
notebooks/), para que os caminhos relativos "../data/..." usados dentro dos
notebooks resolvam corretamente.

Uso: python3 execute_notebooks.py ../notebooks/01_dataset_a_fato_ou_boato_eda.ipynb [...]
"""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def run(path):
    path = Path(path).resolve()
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=600, kernel_name="python3",
                             resources={"metadata": {"path": str(path.parent)}})
    client.execute()
    nbformat.write(nb, path)
    print(f"Executado com sucesso: {path}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        run(p)
