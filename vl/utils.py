from socket import socket, AF_INET, SOCK_STREAM

IP_ADDR = 'tofu'
port = 5222

def send(data):
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((IP_ADDR, port))
    conn.send(data)
    conn.close()
