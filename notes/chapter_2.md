# 2.1 general overview

- TCP is relaible and gurantees intact data tranfer.
- UDP is not reliable, and has no gurantee of intact data transfer, but is faster
- TLS is an additional layer of security on TCP, it encrypts the message. (SSL is the older version of TLS)


# 2.2 the Web and HTTP


- HTTP is said to be stateless protocol
- stateless means it has no memory of it's previous interactions 
- If all requests and responses from a client server is exchanged over the same TCP connection, it is called persistent connection. HTTP is persistent by default, but can be engineered to be ono-persistent(different TCP connection for each request/responce pair)

#### Example HTTP GET request

``telnet gaia.cs.umass.edu 80``
``GET /kurose_ross/interactive/index.php HTTP/1.1
Host: gaia.cs.umass.edu``

``Response is 301 moved permanently``

- cookies allow 'state' of client in the stateless HTTP protocol. cookies host user data that can help servers/sites to provide a plethora of services. attackers can steal cookies and use it for their own goals.

- A web Cache/Proxy server is a middleman server that can communicate with clients and original server through HTTP protocol. it is both a server and a client from a HTTP requset/response perspective.

- Web Cache is primarily used for speed, it allows clients to receive data early if the data is cached.

- Conditional GET request comes into play when cache server has an outdated copy of the webpage. it operates thorugh an if-modified-since header line. if not modified, the response code is 304 Not Modified

# 2.3 Electronic mail

- Mails use SMTP (Simple Mail Transfer Protocol). It uses TCP transfer protocol.