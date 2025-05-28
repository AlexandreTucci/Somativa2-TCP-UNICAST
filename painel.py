import socket

def query_average():
    sensor_id = input("Digite o ID do sensor para consultar (ex: sensor_01): ")
    server_host = 'localhost'
    server_port = int(input("Digite a porta do servidor (ex: 12345): "))
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_host, server_port))
    client.send(f"GET_AVG,{sensor_id}".encode())
    response = client.recv(1024).decode()
    print(f"Média do {sensor_id}: {response}°C")

if __name__ == "__main__":
    query_average()