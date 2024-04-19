import serial 
from datetime import datetime

if __name__ == "__main__":
    porta_serial = serial.Serial('COM4', 9600)
    saida = []
    try:
        while True:
            # Ler uma linha da porta serial
            hora_atual = datetime.now().time()
            linha = porta_serial.readline().decode('utf-8').strip()
            # Imprimir os dados lidos
            print(linha)
            #saida.append( (hora_atual , linha) )
    except:
        # Fechar a porta serial ao interromper o programa
        porta_serial.close()
        print("Programa interrompido. Porta serial fechada.")
    lines = [f"{i} {j}" for i,j in zip(saida)]
    with open("sainda.txt","w") as out:
        out.write("\n".join())