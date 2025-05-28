import socket
import threading
from datetime import datetime
from collections import defaultdict

sensor_data = defaultdict(list)

def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
                
            if data.startswith("GET_AVG,"):
                # Requisição do painel de controle
                sensor_id = data.split(',')[1]
                temperatures = [temp for (_, temp) in sensor_data.get(sensor_id, [])]
                avg = sum(temperatures)/len(temperatures) if temperatures else 0
                conn.send(str(round(avg, 2)).encode())
            else:
                # Dados normal do sensor
                sensor_id, temperature = data.split(',')
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sensor_data[sensor_id].append((timestamp, float(temperature)))
                print(f"Dados recebidos: Sensor {sensor_id} = {temperature}°C")
                
        except Exception as e:
            print(f"Erro: {e}")
            break
    conn.close()

def start_server():
    host = '0.0.0.0'
    port = int(input("Digite a porta do servidor (ex: 12345): "))
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f"Servidor ouvindo em {host}:{port}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()