import socket
import sys
import threading
import time
from datetime import datetime

# Estruturas globais para armazenar dados e conexões
SENSOR_DATA = {}
SENSORES = {}
CONSOLE = None
LOCK = threading.Lock()

# Função para tratar cada sensor conectado
def TrataSensor(conn, addr):
    print(f'Uma thread foi criada para: {addr}')
    
    sensor_id = conn.recv(10).decode().strip()  # Recebe o ID do sensor
    conn.send(b'OK')
    with LOCK:
        SENSORES[sensor_id] = conn
        if sensor_id not in SENSOR_DATA:
            SENSOR_DATA[sensor_id] = []
    
    print(f'Sensor {sensor_id} registrado no socket {conn.getpeername()}')

    while True:
        try:
            data = conn.recv(100).decode().strip()  # Recebe temperatura
            if not data:
                break
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

HOST = ''
PORTA = int(input('Entre com a porta do servidor: '))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORTA))
except:
    print('# Erro de bind')
    sys.exit()

# Obtém o nome do host e IP local para exibir informações do servidor
hostname = socket.gethostname()
hostip = socket.gethostbyname(hostname)
print(f'Host: {hostname} IP: {hostip}')

# Coloca o socket em modo de escuta para aceitar conexões
s.listen(5)
print(f'Aguardando conexões em {PORTA}')

# Loop principal do servidor para aceitar múltiplas conexões
while True:
    conn, addr = s.accept()  # Aceita uma nova conexão
    print(f'Recebi uma conexão de {addr}')
    print(f'conn: {conn}')
    tipo = conn.recv(10).decode().strip()  # Recebe o tipo de conexão (CONSOLE ou sensor)
    conn.send(b'OK')
    # Cria uma thread para tratar a conexão de acordo com o tipo
    if tipo == "CONSOLE":
        t = threading.Thread(target=TrataConsole, args=(conn, addr))
    else:
        t = threading.Thread(target=TrataSensor, args=(conn, addr))
    t.start()

# Fecha o socket do servidor ao encerrar
s.close()
print('O servidor encerrou')