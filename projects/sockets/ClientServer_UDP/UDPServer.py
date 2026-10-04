from socket import *

# Non-privilaged port
serverPort = 12000

# AF_INET = IPv4 & SOCK_DGRAM = UDP DGRAM = Datagram (Network Layer)
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Binding to '' listens to all network interfaces
serverSocket.bind(('', serverPort))

print("Server ready to Recieve..")

while True:
    # buffer size 2048 bytes
    message, clientAddress = serverSocket.recvfrom(2048)
    
    print(f"Received message from {clientAddress}")
    modifiedMessage = message.decode().upper()
    
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)