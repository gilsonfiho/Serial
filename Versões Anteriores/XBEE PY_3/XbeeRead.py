import serial
import re
from datetime import datetime

def read_xbee_data(ser_xbee):
    # Funcao para ler dados do XBEE
    data = ser_xbee.readline().decode('utf-8').strip()
    return data

def organize_data(data, source):
    # Funcao para organizar os dados em um dicionario com horario
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    organized_data = {'source': source, 'data': data, 'timestamp': timestamp}
    return organized_data

def main():
    # Configuracao da porta serial do XBEE3 conectado via USB
    xbee_usb_port = 'COM4'  # Substitua pela porta correta do XBEE3 no seu computador

    # Inicializacao da porta serial do XBEE3
    ser_xbee_usb = serial.Serial(xbee_usb_port, 9600, timeout=1)

    try:
        while True:
            xbee3_data = read_xbee_data(ser_xbee_usb)

            # Exibir dados brutos do XBEE3
            print("Dados brutos do XBEE3:", xbee3_data)

    except KeyboardInterrupt:
        print("Interrupt")
    finally:
        ser_xbee_usb.close()

if __name__ == "__main__":
    main()