from socket import *
import time

serverIP = '127.0.0.1'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

# 1 second timeout limit
clientSocket.settimeout(1.0)

for i in range(1 ,11): 
    try:
        # craft message and keep time
        currentTime = time.time()
        message = "Ping" + " " + str(i) + " " + str(currentTime) 
        
        #send packet
        clientSocket.sendto(message.encode(), (serverIP, serverPort))
        
        #receive time
        response, serverAddress = clientSocket.recvfrom(2048)
        server_time = time.time()
        print(response.decode())
        print(f"RTT: {float(server_time) - currentTime}")
        
    except TimeoutError:
        print("Request Timed out")
