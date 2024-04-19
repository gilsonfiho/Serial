import serial 
import threading
import time

class MonitorSerial:
    def __init__(self, port, boudrate, timeout = 0.1):
        self.port          , self.boudrate      = port , boudrate
        self.tx_callback   , self.rx_callback   = lambda response : print(f'tx {response[0]} - {  [h.hex() for h in response[1]] }') , lambda response : print(f'rx {response[0]} - { [h.hex() for h in response[1]] }')
        self.flagStop = True
        self.timeout = timeout
    def __tx_routine__(self, msg, period):
        try:
            while True:
                self.__serial_port__.write(msg)
                self.tx_callback((time.time(),msg))
                time.sleep(period)
                pass
        except Exception as e:
            pass
        pass

    def __rx_routine__(self):
        try:
            buffer , timeref = [] , time.time()
            while True:
                byte = self.__serial_port__.read(1)
                if byte:
                    buffer.append(byte)
                else:
                    self.rx_callback((timeref,buffer))
                    buffer , timeref = [] , time.time()
        except KeyboardInterrupt:
            exit()

    def start(self, msg = [], period = 0.1):
        rx_thread = threading.Thread(target=self.__rx_routine__,daemon=True)
        tx_thread = threading.Thread(args=(msg,period),target=self.__tx_routine__,daemon=True)
        try:
            self.__serial_port__ = serial.Serial(self.port, self.boudrate, timeout=self.timeout)
            rx_thread.run()
            tx_thread.run()
            rx_thread.join()
            tx_thread.join()
        except KeyboardInterrupt:
            self.flagStop = False
            print("Finished")
        except Exception as e:
            print(f"Error Starting Serial {e}")
            self.__serial_port__ = False  

