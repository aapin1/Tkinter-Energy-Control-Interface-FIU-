# Power Supply 1 simulation
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 50501))
server.listen(1)
print("Power Supply 1 listening on port 50501...")

conn, addr = server.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    print("Power Supply 1 received:", data.decode().strip())

conn.close()
