import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 5050))

s.listen(5)

while True:
    clientsocket, address = s.accept()
    print(f"Connection {address} has been established!")
    clientsocket.send(bytes("welcome to the server", "utf-8"))
    

