from socket import *

# Server Address
serverIP = '127.0.0.1' # Layer 3 (localhost currently)
serverPort = 12000 # Layer 4

clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input("Input lowercase characters: ")

# Fire packet
clientSocket.sendto(message.encode(), (serverIP, serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

print(f"Message From Server: {serverAddress}")

print(modifiedMessage.decode())

clientSocket.close()