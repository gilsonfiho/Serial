import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import time
import serial
import os

# Classe que lida com a comunicação real com o XBee
class RealXBeeData:
    def __init__(self, app, port, baudrate):
        # Referência à aplicação principal
        self.app = app
        # Contador de dados recebidos
        self.data_counter = 0
        # Flag indicando se a comunicação está em execução
        self.running = False
        # Objeto para a comunicação serial
        self.serial_port = None
        # Flag de parada para threads
        self.stop_flag = threading.Event()
        # Configurações da porta serial
        self.port = port
        self.baudrate = baudrate
        # Buffer para armazenar os dados recebidos
        self.buffer = bytearray()
        # Thread para recebimento de dados
        self.receive_thread = None

    # Inicia a comunicação real
    def start_real_communication(self):
        self.running = True
        self.stop_flag.clear()
        # Inicializa a porta serial
        self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.1)
        # Inicia a thread de recebimento de dados
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

    # Para a comunicação real
    def stop_real_communication(self):
        self.running = False
        self.stop_flag.set()
        # Espera a thread de recebimento de dados finalizar
        if self.receive_thread:
            self.receive_thread.join()
        # Fecha a porta serial se estiver aberta
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    # Função para recebimento de dados da porta serial
    def receive_data(self):
        while self.running and not self.stop_flag.is_set():
            byte = self.serial_port.read(1)
            if byte:
                self.buffer.extend(byte)
            else:
                # Se houver dados no buffer, processa e exibe
                if len(self.buffer) > 0:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.app.update_serial_monitor(f"{timestamp}, Data: {self.buffer.hex()}\n")
                    real_data = {'source': 'XBEE3', 'data': self.buffer.hex(), 'timestamp': timestamp}
                    self.app.update_data_tree(real_data)
                    self.buffer = bytearray()
                    self.data_counter += 1  # Incrementa o contador de dados apenas se houver dados

    # Função para baixar os dados para um arquivo
    def download_data(self):
        filename_base = 'data_log'
        extension = 'txt'
        
        i = 1
        # Encontrar um nome de arquivo único
        while True:
            filename = f"{filename_base}{i}.{extension}"
            if not os.path.exists(filename):
                break
            i += 1

        # Escrever os dados no arquivo
        with open(filename, 'w') as file:
            for j in range(1, self.data_counter + 1):
                source = 'XBEE3'
                data = f'RealData_{j}'
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file.write(f"{timestamp} - {source}: {data}\n")

        print(f"Dados baixados e salvos em: {filename}")

# Classe para monitoramento da porta serial
class MonitorSerial:
    def __init__(self, app, port, baudrate, timeout=0.1):
        self.app = app
        self.port, self.baudrate = port, baudrate
        # Callbacks para transmitir e receber dados
        self.tx_callback, self.rx_callback = lambda response: print(f'tx {response[0]} - { response[1] }'), lambda response: self.handle_rx_data(response)
        self.flagStop = True
        self.timeout = timeout

    # Manipula os dados recebidos
    def handle_rx_data(self, response):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        hex_data = [h.hex() for h in response[1]]
        self.app.update_serial_monitor(f"{timestamp}, Data: {''.join(hex_data)}\n")
        real_data = {'source': 'SerialMonitor', 'data': ''.join(hex_data), 'timestamp': timestamp}
        self.app.update_data_tree(real_data)

    # Rotina de transmissão
    def __tx_routine__(self, msg, period):
        try:
            while self.flagStop:
                if msg:
                    self.__serial_port__.write(bytes.fromhex(msg))
                    self.tx_callback((time.time(), msg))
                time.sleep(period)
        except Exception as e:
            print(f"{e}")

    # Rotina de recebimento
    def __rx_routine__(self):
        try:
            buffer, timeref = [], time.time()
            while self.flagStop:
                byte = self.__serial_port__.read(1)
                if byte:
                    buffer.append(byte)
                else:
                    self.rx_callback((timeref, buffer))
                    buffer, timeref = [], time.time()
        except KeyboardInterrupt:
            exit()

    # Inicia a monitoração da porta serial
    def start(self, msg=None, period=0.8):
        rx_thread = threading.Thread(target=self.__rx_routine__, daemon=False)
        tx_thread = threading.Thread(args=(msg, period), target=self.__tx_routine__, daemon=True)
        try:
            # Inicializa a porta serial
            self.__serial_port__ = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            rx_thread.start()
            tx_thread.start()
            # Espera as threads finalizarem
            rx_thread.join()
            tx_thread.join()
            # Fecha a porta serial
            self.__serial_port__.close()
        except KeyboardInterrupt:
            print("Finished")
        except Exception as e:
            print(f"Error Starting Serial {e}")

    # Para a monitoração da porta serial
    def stop(self):
        self.flagStop = False

# Classe principal da aplicação tkinter
class XBeeDataViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("XBee Data Viewer")
        self.geometry("900x700")

        # Utilizar RealXBeeData para comunicação real com o XBee
        self.real_xbee = RealXBeeData(self, port="COM3", baudrate=9600)

        # Utilizar MonitorSerial para monitorar a porta serial
        self.serial_monitor = MonitorSerial(self, port="COM3", baudrate=9600)

        # Configurar a chamada de download_data ao fechar a aplicação
        self.protocol("WM_DELETE_WINDOW", self.exit_application)

        # Criar e configurar widgets
        self.create_widgets()

    def create_widgets(self):

        self.paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned_window.pack(expand=True, fill='both')

        self.serial_monitor_label = tk.Label(self.paned_window, text="Monitor Serial:")
        self.serial_monitor_label.pack()

        self.serial_monitor = tk.Text(self.paned_window, height=10, width=70)
        self.serial_monitor.pack(expand=True, fill='both')

        self.paned_window.add(self.serial_monitor_label)
        self.paned_window.add(self.serial_monitor)

        self.data_analysis_label = tk.Label(self, text="Análise de Dados:")
        self.data_analysis_label.pack()

        self.data_tree = ttk.Treeview(self, columns=('Source', 'Data', 'Timestamp'), show='headings', height=10)
        self.data_tree.heading('Source', text='Source')
        self.data_tree.heading('Data', text='Data')
        self.data_tree.heading('Timestamp', text='Timestamp')
        self.data_tree.pack(expand=True, fill='both')

        self.button_frame = tk.Frame(self)
        self.button_frame.pack()

        self.start_button = tk.Button(self.button_frame, text="Iniciar Leitura", command=self.start_real_communication)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(self.button_frame, text="Parar Leitura", command=self.stop_real_communication)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.download_button = tk.Button(self.button_frame, text="Baixar Dados", command=self.download_data)
        self.download_button.grid(row=0, column=2, padx=10, pady=10)

        self.clear_monitor_button = tk.Button(self.button_frame, text="Limpar Monitor", command=self.clear_monitor)
        self.clear_monitor_button.grid(row=0, column=3, padx=10, pady=10)

        self.clear_data_button = tk.Button(self.button_frame, text="Limpar Dados", command=self.clear_data)
        self.clear_data_button.grid(row=0, column=4, padx=10, pady=10)

        self.exit_button = tk.Button(self.button_frame, text="Sair", command=self.exit_application)
        self.exit_button.grid(row=0, column=5, padx=10, pady=10)

    def start_real_communication(self):
        self.real_xbee.start_real_communication()

    def stop_real_communication(self):
        self.real_xbee.stop_real_communication()

    def download_data(self):
        self.real_xbee.download_data()

    def update_serial_monitor(self, text):
        self.serial_monitor.insert(tk.END, text)
        self.serial_monitor.see(tk.END)

    def update_data_tree(self, data):
        values = (data['source'], data['data'], data['timestamp'])
        self.data_tree.insert('', 0, values=values)

    def exit_application(self):
        # Chama a função download_data ao fechar a aplicação
        self.real_xbee.download_data()
        self.stop_real_communication()
        # Para a monitoração da porta serial
        self.serial_monitor.stop()
        self.destroy()

# Ponto de entrada para a aplicação
if __name__ == "__main__":
    app = XBeeDataViewer()
    app.mainloop()
