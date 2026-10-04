from socket import *

# Server Address
serverIP = '192.168.0.188' # Localhost
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)

# TCP Handshake (SYN, SYN-ACK, ACK) with server
clientSocket.connect((serverIP, serverPort))

sentence = input("Enter Lowercase sentence: ")

# Use send() instead of sendto() because connection is there
clientSocket.send(sentence.encode())

# recv() instead of recvfrom() for same reason
modifiedSentence = clientSocket.recv(2048)

print(f"From The Server: {modifiedSentence.decode()}")

clientSocket.close()

