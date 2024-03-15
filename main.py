'''
@file main.py
Módulo principal para iniciar a aplicação XBeeDataViewer.

Este módulo importa a classe XBeeDataViewer do arquivo XBeeDataViewer.py e
inicia a aplicação XBeeDataViewer.

@author Francisco Gilson Pereira Almeida Filho
@date 06 de Fevereiro de 2024
'''
from XBeeDataViewer import XBeeDataViewer

if __name__ == "__main__":
    app = XBeeDataViewer()
    app.mainloop()