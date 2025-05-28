import socket
import threading
from datetime import datetime

sensor_data = {}

def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            sensor_id, temperature = data.split(',')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if sensor_id not in sensor_data:
                sensor_data[sensor_id] = []
            sensor_data[sensor_id].append((timestamp, float(temperature)))
            
            print(f"Dados recebidos: Sensor {sensor_id} = {temperature}°C")
        except:
            break
    conn.close()

def start_server():
    host = '0.0.0.0'
    port = int(input("Digite a porta do servidor (ex: 12345): "))  # Input da porta
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Servidor ouvindo em {host}:{port}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()