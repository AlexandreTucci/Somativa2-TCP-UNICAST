import socket
import sys
import threading
import time
from datetime import datetime

# Estrutura para armazenar leituras de temperatura
SENSOR_DATA = {}  # {sensor_id: [(timestamp, temperature), ...]}
SENSORES = {}     # {sensor_id: conn}
CONSOLE = None    # Conexão com o painel de controle
LOCK = threading.Lock()  # Para acesso seguro a SENSOR_DATA

def TrataSensor(conn, addr):
    print(f'Uma thread foi criada para: {addr}')
    
    # Recebe o ID do sensor e confirma
    sensor_id = conn.recv(10).decode().strip()
    conn.send(b'OK')  # Confirmação para o cliente
    with LOCK:
        SENSORES[sensor_id] = conn
        if sensor_id not in SENSOR_DATA:
            SENSOR_DATA[sensor_id] = []
    
    print(f'Sensor {sensor_id} registrado no socket {conn.getpeername()}')

    while True:
        try:
            data = conn.recv(100).decode().strip()
            if not data:
                break
                
            # Dados esperados: temperatura (ex.: "23.5")
            try:
                temperature = float(data)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with LOCK:
                    SENSOR_DATA[sensor_id].append((timestamp, temperature))
                print(f'Sensor {sensor_id} enviou {temperature}°C às {timestamp}')
            except ValueError:
                print(f'Dados inválidos recebidos de Sensor {sensor_id}: {data}')
                
        except Exception as e:
            print(f'Erro ao receber dados de Sensor {sensor_id}: {e}')
            break

    with LOCK:
        del SENSORES[sensor_id]
    conn.close()
    print(f'Sensor {sensor_id} encerrou')

def TrataConsole(conn, addr):
    global CONSOLE
    print(f'Painel de controle conectado de: {addr}')
    CONSOLE = conn

    while True:
        try:
            comando = conn.recv(100).decode().strip()
            if not comando:
                break
                
            # Apenas o comando "media todos" é suportado
            if comando == "media todos":
                with LOCK:
                    resposta = ""
                    for sid, dados in SENSOR_DATA.items():
                        if dados:
                            media = sum(temp for _, temp in dados) / len(dados)
                            resposta += f"Sensor {sid}: Média {media:.2f}°C\n"
                        else:
                            resposta += f"Sensor {sid}: Sem dados\n"
                    if not resposta:
                        resposta = "Nenhum sensor registrado"
                conn.send(resposta.encode())
            else:
                conn.send("Comando inválido. Use 'media todos'.".encode())
                
        except Exception as e:
            print(f'Erro no painel de controle: {e}')
            break

    CONSOLE = None
    conn.close()
    print('Painel de controle encerrou')

# PROGRAMA PRINCIPAL
HOST = ''
PORTA = int(input('Entre com a porta do servidor: '))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORTA))
except:
    print('# Erro de bind')
    sys.exit()

hostname = socket.gethostname()
hostip = socket.gethostbyname(hostname)
print(f'Host: {hostname} IP: {hostip}')

s.listen(5)
print(f'Aguardando conexões em {PORTA}')

while True:
    conn, addr = s.accept()
    print(f'Recebi uma conexão de {addr}')
    
    tipo = conn.recv(10).decode().strip()
    conn.send(b'OK')  # Confirmação para o cliente
    
    if tipo == "CONSOLE":
        t = threading.Thread(target=TrataConsole, args=(conn, addr))
    else:
        t = threading.Thread(target=TrataSensor, args=(conn, addr))
    t.start()

s.close()
print('O servidor encerrou')