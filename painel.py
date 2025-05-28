import socket

def query_average():
    sensor_id = input("Digite o ID do sensor para consultar (ex: sensor_01): ").upper()
    server_host = 'localhost'
    server_port = int(input("Digite a porta do servidor (ex: 12345): "))
    
    
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_host, server_port))
        client.send(f"GET_AVG,{sensor_id}".encode())
        response = client.recv(1024).decode()
        print(f"Média do {sensor_id}: {response}°C")
    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    query_average()