# Power Supply 3 simulation
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 50503))
server.listen(1)
print("Power Supply 3 listening on port 50503...")

conn, addr = server.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    print("Power Supply 3 received:", data.decode().strip())

conn.close()
