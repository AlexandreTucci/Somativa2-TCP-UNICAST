import socket

HOST = '127.0.0.1'
PORTA = int(input("Digite a porta do servidor: "))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORTA))
except:
    print("Erro ao conectar ao servidor")
    exit()

# Identifica como console
s.send("CONSOLE".encode())
s.recv(10)  # Aguarda confirmação

while True:
    comando = input("Digite o comando ('media todos' ou 'sair'): ")
    if comando.lower() == "sair":
        break
    s.send(comando.encode())
    resposta = s.recv(1024).decode()
    print(resposta)

s.close()