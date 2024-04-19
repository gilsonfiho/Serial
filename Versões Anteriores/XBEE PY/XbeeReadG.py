import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import time

class SimulatedXBeeData:
    def __init__(self, app):
        self.app = app
        self.data_counter = 0
        self.running = False
        self.simulation_thread = None
        self.stop_flag = threading.Event()

    def start_simulation(self):
        self.running = True
        self.stop_flag.clear()
        self.simulation_thread = threading.Thread(target=self.generate_fake_data)
        self.simulation_thread.start()

    def stop_simulation(self):
        self.running = False
        self.stop_flag.set()
        if self.simulation_thread:
            self.simulation_thread.join()

    def generate_fake_data(self):
        while self.running and not self.stop_flag.is_set():
            self.data_counter += 1
            source = 'XBEE1' if self.data_counter % 2 == 0 else 'XBEE2'
            data = f'FakeData_{self.data_counter}'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            simulated_data = {'source': source, 'data': data, 'timestamp': timestamp}

            # Atualizar a interface gráfica
            self.app.update_serial_monitor(f"Dados do {simulated_data['source']}: {simulated_data}")
            self.app.update_data_tree(simulated_data)

            # Aguardar 1 segundo entre as leituras
            time.sleep(1)

    def download_data(self):
        filename = 'data_log.txt'
        with open(filename, 'w') as file:
            for i in range(1, self.data_counter + 1):
                source = 'XBEE1' if i % 2 == 0 else 'XBEE2'
                data = f'FakeData_{i}'
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file.write(f"{timestamp} - {source}: {data}\n")

class XBeeDataViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("XBee Data Viewer")

        # Ajustes nas dimensões
        self.geometry("900x700")  # Largura x Altura

        # Criar instância simulada
        self.simulated_xbee = SimulatedXBeeData(self)

        # Criar e configurar widgets
        self.create_widgets()

    def create_widgets(self):
        # PanedWindow para dividir a interface
        self.paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned_window.pack(expand=True, fill='both')

        # Monitor Serial
        self.serial_monitor_label = tk.Label(self.paned_window, text="Monitor Serial:")
        self.serial_monitor_label.pack()

        self.serial_monitor = tk.Text(self.paned_window, height=10, width=70)
        self.serial_monitor.pack(expand=True, fill='both')

        # Adiciona uma "barra divisora" para redimensionar
        self.paned_window.add(self.serial_monitor_label)
        self.paned_window.add(self.serial_monitor)

        # Seção de Análise de Dados
        self.data_analysis_label = tk.Label(self, text="Análise de Dados:")
        self.data_analysis_label.pack()

        self.data_tree = ttk.Treeview(self, columns=('Source', 'Data', 'Timestamp'), show='headings',height=10)
        self.data_tree.heading('Source', text='Source')
        self.data_tree.heading('Data', text='Data')
        self.data_tree.heading('Timestamp', text='Timestamp')
        self.data_tree.pack(expand=True, fill='both')

        # Botões
        self.button_frame = tk.Frame(self)
        self.button_frame.pack()

        self.start_button = tk.Button(self.button_frame, text="Iniciar Leitura", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(self.button_frame, text="Parar Leitura", command=self.stop_simulation)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.download_button = tk.Button(self.button_frame, text="Baixar Dados", command=self.download_data)
        self.download_button.grid(row=0, column=2, padx=10, pady=10)

        self.clear_monitor_button = tk.Button(self.button_frame, text="Limpar Monitor", command=self.clear_monitor)
        self.clear_monitor_button.grid(row=0, column=3, padx=10, pady=10)

        self.clear_data_button = tk.Button(self.button_frame, text="Limpar Dados", command=self.clear_data)
        self.clear_data_button.grid(row=0, column=4, padx=10, pady=10)

        self.exit_button = tk.Button(self.button_frame, text="Sair", command=self.exit_application)
        self.exit_button.grid(row=0, column=5, padx=10, pady=10)

    def start_simulation(self):
        self.simulated_xbee.start_simulation()

    def stop_simulation(self):
        self.simulated_xbee.stop_simulation()

    def download_data(self):
        self.simulated_xbee.download_data()

    def update_serial_monitor(self, text):
        self.serial_monitor.insert(tk.END, text + '\n')
        self.serial_monitor.see(tk.END)

    def update_data_tree(self, data):
        values = (data['source'], data['data'], data['timestamp'])
        # Adiciona os valores no início (index 0) em vez de no final
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