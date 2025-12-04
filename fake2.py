# Power Supply 2 simulation
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 50502))
server.listen(1)
print("Power Supply 2 listening on port 50502...")

conn, addr = server.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    print("Power Supply 2 received:", data.decode().strip())

conn.close()
