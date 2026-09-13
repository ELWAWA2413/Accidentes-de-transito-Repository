"""Ejecuta las celdas con IPython, sin abrir un servidor."""

import os
from pathlib import Path
import sys

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

from src.etl import ROOT


def ejecutar():
    ruta = ROOT / 'notebooks/01_eda.ipynb'
    nb = nbformat.read(ruta, as_version=4)
    shell = InteractiveShell.instance()
    anterior = Path.cwd()
    contador = 0
    try:
        os.chdir(ROOT)
        for celda in nb.cells:
            if celda.cell_type != 'code':
                continue
            contador += 1
            with capture_output(stdout=True, stderr=True, display=True) as captura:
                resultado = shell.run_cell(celda.source, store_history=False)
            if resultado.error_before_exec or resultado.error_in_exec:
                raise RuntimeError(f'Falló la celda de código {contador}: {captura.stdout}')
            salidas = []
            if captura.stdout:
                salidas.append(nbformat.v4.new_output('stream', name='stdout', text=captura.stdout))
            if captura.stderr:
                salidas.append(nbformat.v4.new_output('stream', name='stderr', text=captura.stderr))
            for salida in captura.outputs:
                salidas.append(nbformat.v4.new_output('display_data', data=salida.data, metadata=salida.metadata))
            celda.outputs = salidas
            celda.execution_count = contador
        nb.metadata['verificacion'] = 'Celdas ejecutadas secuencialmente con IPython en proceso, sin servidor Jupyter.'
        nb.metadata['language_info']['version'] = sys.version.split()[0]
        nbformat.validate(nb)
        nbformat.write(nb, ruta)
    finally:
        os.chdir(anterior)
    print(f'Verificadas {contador} celdas de código sin errores.')


if __name__ == '__main__':
    ejecutar()
