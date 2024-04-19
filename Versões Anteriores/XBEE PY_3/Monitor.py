import serial 
import threading
import time

class MonitorSerial:
    def __init__(self, port, boudrate, timeout = 0.1):
        self.port          , self.boudrate      = port , boudrate
        self.tx_callback   , self.rx_callback   = lambda response : print(f'tx {response[0]} - { response[1] }') , lambda response : print(f'rx {response[0]} - { [h.hex() for h in response[1]] }')
        self.flagStop = True
        self.timeout = timeout

    def __tx_routine__(self, msg, period):
        try:
            while self.flagStop:
                if msg:
                    self.__serial_port__.write(  bytes.fromhex(msg) )
                    self.tx_callback((time.time(),msg))
                time.sleep(period)
                pass
        except Exception as e:
            print(f"{e}")
        pass

    def __rx_routine__(self):
        try:
            buffer , timeref = [] , time.time()
            while self.flagStop:
                byte = self.__serial_port__.read(1)
                if byte:
                    buffer.append(byte)
                else:
                    self.rx_callback((timeref,buffer))
                    buffer , timeref = [] , time.time()
        except KeyboardInterrupt:
            exit()

    def start(self, msg = None, period = 0.8):
        rx_thread = threading.Thread(target=self.__rx_routine__,daemon=False)
        tx_thread = threading.Thread(args=(msg,period),target=self.__tx_routine__,daemon=True)
        try:
            self.__serial_port__ = serial.Serial(self.port, self.boudrate, timeout=self.timeout)
            rx_thread.start()
            tx_thread.start()
            rx_thread.join()
            tx_thread.join()
            self.__serial_port__.close()
        except KeyboardInterrupt:
            print("Finished")
        except Exception as e:
            print(f"Error Starting Serial {e}")

    def stop(self):
        self.flagStop = False