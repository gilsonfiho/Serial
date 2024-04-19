import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import time
import serial
import os 

class RealXBeeData:
    def __init__(self, app, port, baudrate):
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
        self.stop_flag.clear()
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

    def stop_real_communication(self):
        self.stop_flag.set()

    def join_threads(self):
        if self.receive_thread:
            self.receive_thread.join()

    def receive_data(self):
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
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        filename_base = 'data_log'
        extension = 'txt'

        i = 1
        while True:
            filename = f"{filename_base}{i}.{extension}"
            if not os.path.exists(filename):
                break
            i += 1

        with open(filename, 'w') as file:
            for timestamp, data_hex in self.received_data:
                file.write(f"{timestamp} - XBEE3: {data_hex}\n")

        print(f"Dados baixados e salvos em: {filename}")

class XBeeDataViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("XBee Data Viewer")
        self.geometry("900x700")

        # Utilizar RealXBeeData para comunicação real
        self.real_xbee = RealXBeeData(self, port="COM4", baudrate=9600)

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

    def clear_monitor(self):
        self.serial_monitor.delete(1.0, tk.END)

    def clear_data(self):
        self.data_tree.delete(*self.data_tree.get_children())

    def exit_application(self):
        self.real_xbee.download_data()  # Chama a função download_data ao fechar a aplicação
        self.stop_real_communication()
        self.destroy()

if __name__ == "__main__":
    app = XBeeDataViewer()
    app.mainloop()
