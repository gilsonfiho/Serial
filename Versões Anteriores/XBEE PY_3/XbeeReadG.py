import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
from serial.tools import list_ports

class SerialCommunicator:
    def __init__(self, port, baudrate, timeout=0.1, rx_callback=None):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.rx_callback = rx_callback
        self.serial_port = None
        self.flag_stop = threading.Event()

    def open_serial_port(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        except Exception as e:
            print(f"Error opening serial port: {e}")

    def auto_detect_serial_port(self):
        ports = list_ports.comports()
        for port, _, _ in ports:
            if "COM" in port:
                self.port = port
                return True
        return False

    def close_serial_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def read_serial_data(self):
        try:
            while not self.flag_stop.is_set():
                byte = self.serial_port.read(1)
                if byte:
                    timestamp = time.time()
                    self.rx_callback((timestamp, [byte]))
        except KeyboardInterrupt:
            pass

    def start_communication(self):
        if not self.port:
            if not self.auto_detect_serial_port():
                print("No serial port found.")
                return

        self.open_serial_port()
        if self.serial_port and self.serial_port.is_open:
            rx_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            rx_thread.start()
        else:
            print("Failed to start communication. Serial port not opened.")

    def stop_communication(self):
        self.flag_stop.set()
        self.close_serial_port()

class XBeeDataViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("XBee Data Viewer")
        self.geometry("900x700")

        self.serial_communicator = SerialCommunicator(None, 9600, rx_callback=self.update_serial_monitor)

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

        self.start_button = tk.Button(self.button_frame, text="Iniciar Leitura", command=self.start_serial_communication)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(self.button_frame, text="Parar Leitura", command=self.stop_serial_communication)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.download_button = tk.Button(self.button_frame, text="Baixar Dados", command=self.download_data)
        self.download_button.grid(row=0, column=2, padx=10, pady=10)

        self.clear_monitor_button = tk.Button(self.button_frame, text="Limpar Monitor", command=self.clear_monitor)
        self.clear_monitor_button.grid(row=0, column=3, padx=10, pady=10)

        self.clear_data_button = tk.Button(self.button_frame, text="Limpar Dados", command=self.clear_data)
        self.clear_data_button.grid(row=0, column=4, padx=10, pady=10)

        self.exit_button = tk.Button(self.button_frame, text="Sair", command=self.exit_application)
        self.exit_button.grid(row=0, column=5, padx=10, pady=10)

    def start_serial_communication(self):
        self.serial_communicator.start_communication()

    def stop_serial_communication(self):
        self.serial_communicator.stop_communication()

    def download_data(self):
        filename = 'data_log.txt'
        with open(filename, 'w') as file:
            for child_id in self.data_tree.get_children():
                values = self.data_tree.item(child_id, 'values')
                timestamp, source, data = values
                file.write(f"{timestamp} - {source}: {data}\n")

    def update_serial_monitor(self, data):
        timestamp, byte_data = data
        hex_data = [byte.hex() for byte in byte_data]
        self.serial_monitor.insert(tk.END, f"Timestamp: {timestamp}, Data: {hex_data}\n")
        self.serial_monitor.see(tk.END)

    def update_data_tree(self, data):
        values = (data['source'], data['data'], data['timestamp'])
        self.data_tree.insert('', 0, values=values)

    def clear_monitor(self):
        self.serial_monitor.delete(1.0, tk.END)

    def clear_data(self):
        self.data_tree.delete(*self.data_tree.get_children())

    def exit_application(self):
        self.stop_serial_communication()
        self.destroy()

if __name__ == "__main__":
    app = XBeeDataViewer()
    app.mainloop()
