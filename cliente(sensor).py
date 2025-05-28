import socket
import time
import random

def send_temperature():
    sensor_id = input("Digite o ID do sensor (ex: sensor_01): ").upper()
    server_host = 'localhost'
    server_port = int(input("Digite a porta do servidor (ex: 12345): "))
    client_port = input("Digite a porta do cliente (opcional, pressione Enter para aleatório): ")
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if client_port:
        client.bind(('0.0.0.0', int(client_port)))
    
    client.connect((server_host, server_port))
    print(f"Sensor {sensor_id} conectado ao servidor {server_host}:{server_port}")
    
    try:
        while True:
            temperature = round(random.uniform(20.0, 30.0), 2)
            data = f"{sensor_id},{temperature}"
            client.send(data.encode())
            print(f"Enviado: {data}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nSensor encerrado.")
    finally:
        client.close()

if __name__ == "__main__":
    send_temperature()