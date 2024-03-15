'''
@file RealXBeeData.py
@brief Módulo para comunicação com dispositivo XBee em tempo real.

Este módulo fornece uma classe RealXBeeData para comunicação com um dispositivo
XBee em tempo real, incluindo métodos para iniciar e interromper a comunicação,
receber dados do dispositivo, e baixar os dados recebidos para um arquivo de texto.

@author [Francisco Gilson Pereira Almeida Filho]
@date [06 de Fevereiro de 2024]
'''

'''Importação de Bibliotecas'''
from datetime import datetime
import threading
import time
import serial
import os

class RealXBeeData:
    """Classe para comunicação com um dispositivo XBee real."""

    def __init__(self, app, port, baudrate):
        """Inicializa uma nova instância de RealXBeeData.

        Args:
            app: A aplicação que utiliza a classe RealXBeeData.
            port (str): A porta serial à qual o dispositivo XBee está conectado.
            baudrate (int): A taxa de baud do dispositivo XBee.
        """
        self.app = app
        self.data_counter = 0
        self.running = False
        self.serial_port = None
        self.stop_flag = threading.Event()
        self.port = port
        self.baudrate = baudrate
        self.buffer = bytearray()
        self.received_data = []
        self.receive_thread = None
        self.buffer_lock = threading.Lock()

    def start_real_communication(self):
        """Inicia a comunicação com o dispositivo XBee."""
        self.stop_flag.clear()
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

    def stop_real_communication(self):
        """Interrompe a comunicação com o dispositivo XBee."""
        self.stop_flag.set()

    def join_threads(self):
        """Aguarda a finalização das threads em execução."""
        if self.receive_thread:
            self.receive_thread.join()

    def receive_data(self):
        """Recebe os dados do dispositivo XBee e os processa."""
        try:
            self.running = True
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.1)
            while not self.stop_flag.is_set():
                byte = self.serial_port.read(1)
                if byte:
                    with self.buffer_lock:
                        self.buffer.append(byte[0])
                else:
                    with self.buffer_lock:
                        if len(self.buffer) > 0:
                            timestamp = time.strftime('%Y-%m-%d %H:%M:%S.') + str(int(time.time() * 1000) % 1000).zfill(3)
                            data_hex = ' '.join(f'{b:02X}' for b in self.buffer)
                            self.app.update_serial_monitor(f"{timestamp}, Data: {data_hex}\n")
                            real_data = {'source': 'XBEE3', 'data': data_hex, 'timestamp': timestamp}
                            self.app.update_data_tree(real_data)
                            self.received_data.append((timestamp, data_hex))
                            self.buffer = bytearray()
                            self.data_counter += 1  # Incrementa o contador de dados
        except Exception as e:
            print(f"Error in receive_data: {e}")
        finally:
            self.running = False
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

    def download_data(self):
        """Baixa os dados recebidos do dispositivo XBee e os salva em um arquivo de texto."""
        filename_base = 'data_log'
        extension = 'txt'

        i = 1
        while True:
            filename = f"{filename_base}{i}.{extension}"
            if not os.path.exists(filename):
                break
            i += 1

        # Inicializa contadores
        quantidade_silabas_e1 = 0
        numero_linhas = 1

        with open(filename, 'w+') as file:
            # Preenche o arquivo e conta as sílabas "E1" e o número de linhas
            for timestamp, data_hex in self.received_data:
                file.write(f"{timestamp} - XBEE3: {data_hex}\n")
                quantidade_silabas_e1 += data_hex.upper().count("E1")
                numero_linhas += 1

            # Obtém o conteúdo atual do arquivo
            file.seek(0)
            existing_content = file.read()

            # Reinicia o cursor para o início e escreve o relatório
            file.seek(0)
            file.write(f"{'-'*50}\n")
            file.write(f"{'-'*50}\n")
            file.write(f"Quantidade de Erros de Pacote: {quantidade_silabas_e1}\n")
            file.write(f"Quantidade de Linhas: {numero_linhas}\n")
            file.write(f"Porcentagem de erro: {(quantidade_silabas_e1/numero_linhas)*100}%\n")
            file.write(f"{'-'*50}\n")
            file.write(f"{'-'*50}\n")

            # Adiciona de volta o conteúdo anterior
            file.write(existing_content)

        print(f"Dados baixados e salvos em: {filename}")