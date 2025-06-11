# Integrantes: Alexandre Andrioli Tucci, João Victor Saboya Ribeiro de Carvalho, Arthur de Oliveira Carvalho
import socket
import time
import random

SENSOR_ID = input("Digite o ID do sensor: ")
HOST = '127.0.0.1'
PORTA = int(input("Digite a porta do servidor: "))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORTA))
except:
    print("Erro ao conectar ao servidor")
    exit()

s.send(b"SENSOR")
response = s.recv(10).decode().strip()
if response != "OK":
    print("Erro na negociação de tipo de conexão")
    s.close()
    exit()

s.send(SENSOR_ID.encode())
response = s.recv(10).decode().strip()
if response == "OK":
    print(f"Sensor {SENSOR_ID} conectado ao servidor")
else:
    print("Erro na conexão")
    s.close()
    exit()

while True:
    temperatura = round(random.uniform(10, 40), 1)
    s.send(str(temperatura).encode())
    print(f"Enviado: {temperatura}°C")
    time.sleep(5)
    
s.close()