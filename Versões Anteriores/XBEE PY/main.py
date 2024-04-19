from Monitor import MonitorSerial

if __name__ == "__main__":
    monitor = MonitorSerial("COM4",9600) 
    monitor.start()