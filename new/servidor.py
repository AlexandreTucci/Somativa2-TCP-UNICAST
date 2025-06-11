import socket # comunicação de rede
import sys # manipulação do sistema (ex: sys.exit)
import threading # uso de threads
import time # Importa o módulo time (não utilizado, mas pode ser útil para delays)
from datetime import datetime

SENSOR_DATA = {} # Armazenar leituras de temperatura de cada sensor {sensor_id: [(timestamp, temperature), ...]}
SENSORES = {} # Armazenar as conexões dos sensores {sensor_id: conn}
CONSOLE = None # Armazenar a conexão do painel de controle
LOCK = threading.Lock() # Garantir acesso seguro às estruturas compartilhadas entre threads

# Comunicação com um sensor
def TrataSensor(conn, addr):
    # Uma thread foi criada para o sensor
    print(f'Uma thread foi criada para: {addr}')
    
    sensor_id = conn.recv(10).decode().strip() # Recebe o ID do sensor e envia confirmação
    conn.send(b'OK')  # Confirmação para o cliente
    # Adiciona o sensor ao dicionário de sensores e inicializa lista de dados se necessário
    with LOCK:
        SENSORES[sensor_id] = conn
        if sensor_id not in SENSOR_DATA:
            SENSOR_DATA[sensor_id] = []
    
    print(f'Sensor {sensor_id} registrado no socket {conn.getpeername()}') # Informa que o sensor foi registrado

    while True: # Loop para receber dados do sensor
        try:
            # Recebe dados do sensor (temperatura)
            data = conn.recv(100).decode().strip()
            # Se não receber dados, encerra o loop
            if not data:
                break
                
            # Tenta converter os dados recebidos em float (temperatura)
            try:
                temperature = float(data)
                # Registra o timestamp da leitura
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Adiciona a leitura ao dicionário de dados do sensor
                with LOCK:
                    SENSOR_DATA[sensor_id].append((timestamp, temperature))
                # Exibe no servidor a leitura recebida
                print(f'Sensor {sensor_id} enviou {temperature}°C às {timestamp}')
            except ValueError:
                # Caso os dados não sejam válidos, exibe mensagem de erro
                print(f'Dados inválidos recebidos de Sensor {sensor_id}: {data}')
                
        except Exception as e:
            # Em caso de erro na comunicação, exibe mensagem e encerra
            print(f'Erro ao receber dados de Sensor {sensor_id}: {e}')
            break

    # Remove o sensor do dicionário de sensores ao encerrar
    with LOCK:
        del SENSORES[sensor_id]
    # Fecha a conexão com o sensor
    conn.close()
    # Informa que o sensor encerrou
    print(f'Sensor {sensor_id} encerrou')

# Função que trata a comunicação com o painel de controle
def TrataConsole(conn, addr):
    global CONSOLE
    # Informa que o painel de controle conectou
    print(f'Painel de controle conectado de: {addr}')
    # Armazena a conexão do painel de controle
    CONSOLE = conn

    # Loop para receber comandos do painel
    while True:
        try:
            # Recebe comando do painel
            comando = conn.recv(100).decode().strip()
            # Se não receber comando, encerra o loop
            if not comando:
                break
                
            # Verifica se o comando é "media todos"
            if comando == "media todos":
                with LOCK:
                    resposta = ""
                    # Para cada sensor, calcula a média das temperaturas
                    for sid, dados in SENSOR_DATA.items():
                        if dados:
                            media = sum(temp for _, temp in dados) / len(dados)
                            resposta += f"Sensor {sid}: Média {media:.2f}°C\n"
                        else:
                            resposta += f"Sensor {sid}: Sem dados\n"
                    # Se não houver sensores, informa
                    if not resposta:
                        resposta = "Nenhum sensor registrado"
                # Envia a resposta ao painel
                conn.send(resposta.encode())
            else:
                # Se comando inválido, informa ao painel
                conn.send("Comando inválido. Use 'media todos'.".encode())
                
        except Exception as e:
            # Em caso de erro na comunicação, exibe mensagem e encerra
            print(f'Erro no painel de controle: {e}')
            break

    # Limpa a variável CONSOLE ao encerrar
    CONSOLE = None
    # Fecha a conexão com o painel
    conn.close()
    # Informa que o painel encerrou
    print('Painel de controle encerrou')

# PROGRAMA PRINCIPAL
# Define o host (vazio para aceitar conexões em todas as interfaces)
HOST = ''
# Solicita ao usuário a porta do servidor
PORTA = int(input('Entre com a porta do servidor: '))

# Cria o socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Faz o bind do socket ao host e porta
    s.bind((HOST, PORTA))
except:
    # Em caso de erro no bind, exibe mensagem e encerra
    print('# Erro de bind')
    sys.exit()

# Obtém o nome do host e IP local
hostname = socket.gethostname()
hostip = socket.gethostbyname(hostname)
# Exibe informações do host
print(f'Host: {hostname} IP: {hostip}')

# Coloca o socket em modo de escuta
s.listen(5)
# Informa que está aguardando conexões
print(f'Aguardando conexões em {PORTA}')

# Loop principal para aceitar conexões
while True:
    # Aceita uma nova conexão
    conn, addr = s.accept()
    # Exibe informações da conexão recebida
    print(f'Recebi uma conexão de {addr}')
    print(f'conn: {conn}')
    # Recebe o tipo de conexão (CONSOLE ou sensor)
    tipo = conn.recv(10).decode().strip()
    # Envia confirmação para o cliente
    conn.send(b'OK')  # Confirmação para o cliente
    
    # Cria uma thread para tratar a conexão, dependendo do tipo
    if tipo == "CONSOLE":
        t = threading.Thread(target=TrataConsole, args=(conn, addr))
    else:
        t = threading.Thread(target=TrataSensor, args=(conn, addr))
    t.start()

# Fecha o socket do servidor ao encerrar
s.close()
# Informa que o servidor encerrou
print('O servidor encerrou')