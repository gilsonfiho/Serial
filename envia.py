'''
@file XBeeInterface.py
@brief Módulo para interface de envio de dados XBee.

Este módulo fornece uma classe XBeeInterface para interface de envio de dados XBee,
incluindo a criação dinâmica de botões para envio de pacotes hexadecimais com intervalos configuráveis.

@author Francisco Gilson Pereira Almeida Filho
@date 06 de Fevereiro de 2024
'''

'''Importação de Bibliotecas'''
import tkinter as tk
from serial import Serial
import threading
import time

class XBeeInterface:

    def __init__(self, root):
        """
        Inicializa a aplicação XBeeInterface.

        Configura a interface gráfica e as variáveis de controle.

        :param root: O widget raiz da aplicação.
        """
        self.root = root
        self.root.title("XBee Interface")

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack()

        self.buttons = []  # Lista para armazenar os botões dinamicamente criados
        self.is_transmitting = False  # Variável para rastrear se a transmissão está acontecendo

        # Botão fixo para parar
        self.stop_button = tk.Button(self.buttons_frame, text="Parar", command=self.stop_transmission, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        # Botão para adicionar novo botão
        tk.Button(self.buttons_frame, text="Adicionar Botão", command=self.add_button).pack(side=tk.LEFT)

        # Área para exibir feedback
        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack()

    def add_button(self):
        """
        Adiciona um novo botão para iniciar/parar a transmissão de dados.
        """
        # Frame para agrupar elementos relacionados a um botão
        button_frame = tk.Frame(self.buttons_frame)
        button_frame.pack(pady=10)

        # Variáveis para armazenar as configurações do botão
        title_var = tk.StringVar()
        packet_var = tk.StringVar()
        interval_var = tk.DoubleVar(value=1.0)

        # Campos de entrada para configurar o botão
        tk.Label(button_frame, text="Título:").pack()
        tk.Entry(button_frame, textvariable=title_var).pack()

        tk.Label(button_frame, text="Pacote Hexadecimal:").pack()
        tk.Entry(button_frame, textvariable=packet_var).pack()

        tk.Label(button_frame, text="Intervalo de Envio (segundos):").pack()
        tk.Entry(button_frame, textvariable=interval_var).pack()

        # Botão para iniciar/parar a transmissão deste botão específico
        new_button = tk.Button(button_frame, text="Iniciar/Parar", command=lambda: self.toggle_transmission(new_button, title_var.get(), packet_var.get(), interval_var.get()))
        new_button.pack()

        # Adicionar o novo botão à lista
        self.buttons.append(new_button)

    def toggle_transmission(self, button, title, packet, interval):
        """
        Inicia ou interrompe a transmissão de dados.

        :param button: O botão que disparou a ação.
        :param title: O título do botão.
        :param packet: O pacote hexadecimal a ser transmitido.
        :param interval: O intervalo de envio em segundos.
        """
        if not self.is_transmitting:
            # Iniciar a transmissão
            self.is_transmitting = True
            for b in self.buttons:
                b['state'] = 'disabled'  # Desativar outros botões durante a transmissão
            self.stop_button['state'] = 'normal'  # Ativar o botão de parar durante a transmissão
            threading.Thread(target=self.transmit_data_loop, args=(title, packet, interval)).start()
        else:
            # Parar a transmissão
            self.is_transmitting = False
            for b in self.buttons:
                b['state'] = 'normal'  # Reativar outros botões
            self.stop_button['state'] = 'disabled'  # Desativar o botão de parar
            self.result_label.config(text="Transmissão interrompida.")

    def stop_transmission(self):
        """
        Interrompe a transmissão de dados.
        """
        # Função para parar a transmissão quando o botão de parar é pressionado
        self.is_transmitting = False
        for button in self.buttons:
            button['state'] = 'normal'  # Reativar todos os botões de adicionar
        self.result_label.config(text="Transmissão interrompida.")

    def transmit_data_loop(self, title, packet, interval):
        """
        Loop de transmissão de dados.

        Este método é executado em uma thread separada para transmitir os dados
        com o intervalo especificado até que a transmissão seja interrompida.

        :param title: O título do botão.
        :param packet: O pacote hexadecimal a ser transmitido.
        :param interval: O intervalo de envio em segundos.
        """
        try:
            with Serial('COM4', 9600, timeout=1) as ser:  # Substitua 'COM1' pela porta correta
                while self.is_transmitting:
                    ser.write(bytes.fromhex(packet))
                    time.sleep(interval)
        except Exception as e:
            self.result_label.config(text=f"Erro na transmissão ({title}): {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = XBeeInterface(root)
    root.mainloop()
