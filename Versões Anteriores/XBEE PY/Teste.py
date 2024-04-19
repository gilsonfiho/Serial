import tkinter as tk
from tkinter import ttk
import serial
from datetime import datetime
import threading
import re

class XBeeDataReceiver:
    def __init__(self, app, serial_port):
        self.app = app
        self.serial_port = serial_port
        self.running = False
        self.serial_connection = None
        self.receive_thread = None

    def start_receiving(self):
        self.running = True
        try:
            self.serial_connection = serial.Serial(self.serial_port, 9600, timeout=1)
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.start()
        except serial.SerialException as e:
            self.app.update_serial_monitor(f"Erro ao abrir a porta serial: {str(e)}")

    def stop_receiving(self):
        self.running = False
        if self.receive_thread:
            self.receive_thread.join()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def receive_data(self):
        while self.running:
            try:
                xbee3_data = self.read_xbee_data()

                # Verificar a origem dos dados (XBEE1 ou XBEE2) e organizar
                if re.match(r'^[0-9A-Fa-f]{6}$', xbee3_data):
                    organized_data = self.organize_data(xbee3_data, 'XBEE1')
                    self.app.update_serial_monitor(f"Dados do XBEE1: {organized_data}")
                    self.app.update_data_tree(organized_data)
                elif re.match(r'^[0-9A-Fa-f]{7,}$', xbee3_data):
                    organized_data = self.organize_data(xbee3_data, 'XBEE2')
                    self.app.update_serial_monitor(f"Dados do XBEE2: {organized_data}")
                    self.app.update_data_tree(organized_data)
                else:
                    # Tratar outros casos se necessário
                    pass

            except Exception as e:
                self.app.update_serial_monitor(f"Erro ao receber dados: {str(e)}")
                # Tratar erros de leitura, se necessário

    def read_xbee_data(self):
        return self.serial_connection.readline().decode('utf-8').strip()

    def organize_data(self, data, source):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        organized_data = {'source': source, 'data': data, 'timestamp': timestamp}
        return organized_data

class XBeeDataViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("XBee Data Viewer")
        self.geometry("800x600")

        self.xbee_usb_port = 'COM4'  # Substitua pela porta correta do XBEE3 no seu computador

        self.xbee_receiver = XBeeDataReceiver(self, self.xbee_usb_port)

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

        self.data_tree = ttk.Treeview(self, columns=('Source', 'Data', 'Timestamp'), show='headings')
        self.data_tree.heading('Source', text='Source')
        self.data_tree.heading('Data', text='Data')
        self.data_tree.heading('Timestamp', text='Timestamp')
        self.data_tree.pack()

        self.button_frame = tk.Frame(self)
        self.button_frame.pack()

        self.start_button = tk.Button(self.button_frame, text="Iniciar Leitura", command=self.start_receiving)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(self.button_frame, text="Parar Leitura", command=self.stop_receiving)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.clear_monitor_button = tk.Button(self.button_frame, text="Limpar Monitor", command=self.clear_monitor)
        self.clear_monitor_button.grid(row=0, column=2, padx=10, pady=10)

        self.clear_data_button = tk.Button(self.button_frame, text="Limpar Dados", command=self.clear_data)
        self.clear_data_button.grid(row=0, column=3, padx=10, pady=10)

        self.exit_button = tk.Button(self.button_frame, text="Sair", command=self.exit_application)
        self.exit_button.grid(row=0, column=4, padx=10, pady=10)

    def start_receiving(self):
        self.xbee_receiver.start_receiving()

    def stop_receiving(self):
        self.xbee_receiver.stop_receiving()

    def update_serial_monitor(self, text):
        self.serial_monitor.insert(tk.END, text + '\n')
        self.serial_monitor.see(tk.END)

    def update_data_tree(self, data):
        values = (data['source'], data['data'], data['timestamp'])
        self.data_tree.insert('', 0, values=values)

    def clear_monitor(self):
        self.serial_monitor.delete(1.0, tk.END)

    def clear_data(self):
        self.data_tree.delete(*self.data_tree.get_children())

    def exit_application(self):
        self.destroy()

if __name__ == "__main__":
    app = XBeeDataViewer()
    app.mainloop()
