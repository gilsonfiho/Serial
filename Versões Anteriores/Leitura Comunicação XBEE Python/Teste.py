import serial
import multiprocessing
import time

port = "COM4"
rate = 19200

data = b'\xAB\x81\x10\xDE\xE9\x36\xCD'
interval = 0.8

serial_port = serial.Serial(port, rate, timeout=1)

try:
    serial_port = serial.Serial('COM4', 9600, timeout=0.05)
except Exception as e:
    print(f"{e}")
    exit()

def send_serial(id):
    try:
        while True:
            serial_port.write(data)
            time.sleep(interval)
    except Exception as e:
        print(f"Erro na comunicação serial: {e}")
    finally:
        serial_port.close()


def read_serial(id):
    serial_port = serial.Serial('COM4', 9600, timeout=1)
    try:
        while True:
            response = serial_port.readline()
            print(response)
    except Exception as e:
        print(f"Erro na comunicação serial: {e}")
    finally:
        serial_port.close()


if __name__ == "__main__":

    processo1 = multiprocessing.Process(target=send_serial, args=(1,))
    processo2 = multiprocessing.Process(target=read_serial, args=(1,))
     # Iniciar os processos
    processo1.start()
    processo2.start()

    # Aguardar a conclusão dos processos
    processo1.join()
    processo2.join()