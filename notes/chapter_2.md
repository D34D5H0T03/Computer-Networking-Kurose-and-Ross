# 2.1 Principles of Network Applications

- Applications run on **end systems** (clients and servers), not on the core network routers.
- **Client-Server Architecture:** There is an always-on host (server) servicing requests from many other hosts (clients).
- **P2P Architecture:** (Peer-to-Peer) Minimal reliance on dedicated servers; direct communication between intermittent hosts (e.g., BitTorrent).
- **Processes Communicating:** It is not computers that communicate, but *processes* (running programs). A process sends and receives messages to/from the network through a software interface called a **socket**. 
- To identify a receiving process, you need two things:
  1. **IP Address:** Identifies the destination host (computer).
  2. **Port Number:** Identifies the specific process running on that host (e.g., Port 80 for HTTP, Port 443 for HTTPS).

### Transport Services available to Applications
- **TCP (Transmission Control Protocol):** 
  - Reliable, guarantees intact data transfer. 
  - Connection-oriented (requires a 3-way handshake).
  - Includes congestion control (throttles back when network is busy).
- **UDP (User Datagram Protocol):** 
  - Unreliable, "fire and forget". No guarantee of intact data transfer.
  - Faster, no handshake required. Good for video streaming/gaming.
- **TLS (Transport Layer Security):** 
  - An enhancement to TCP (lives at the Application Layer) that encrypts the payload to prevent packet sniffing. SSL is the deprecated predecessor to TLS.


# 2.2 The Web and HTTP

- The Web consists of **objects** (HTML files, JPEG images, Java applets, video clips) hosted on web servers. 
- A web page consists of a base HTML file that references several other objects via URLs.
- **HTTP (HyperText Transfer Protocol):** The Web's application-layer protocol.
  - HTTP uses TCP as its underlying transport protocol.
  - HTTP is a **stateless protocol**; the server maintains no memory of past client requests.

### Non-Persistent vs. Persistent Connections
- **Non-Persistent:** A brand new TCP connection is opened and closed for *every single object* requested. Causes high latency due to multiple handshakes.
- **Persistent:** The server leaves the TCP connection open after sending a response. Multiple objects can be sent over the same connection. HTTP/1.1 uses persistent connections by default.

### HTTP Request Message Structure
An HTTP request is plain text and consists of:
1. **Request Line:** Method (GET, POST, etc.), URL path, HTTP version.
2. **Header Lines:** Host, User-Agent, Connection type, Cookies.
3. **Entity Body:** (Optional) Used in POST requests to send data (e.g., form submissions, JSON payloads).

*Example HTTP GET Request:*
GET /kurose_ross/interactive/index.php HTTP/1.1
Host: gaia.cs.umass.edu
User-Agent: Mozilla/5.0
Accept-Language: en-us

### HTTP Response Message Structure
An HTTP response consists of:
1. **Status Line:** HTTP version, Status Code, Status Message.
2. **Header Lines:** Date, Server type, Content-Length, Content-Type.
3. **Entity Body:** The requested object (the actual HTML/JSON/Image).

*Common Status Codes:*
- `200 OK`: Request succeeded.
- `301 Moved Permanently`: Object moved, new location provided in header.
- `400 Bad Request`: Server could not understand the request.
- `404 Not Found`: Object does not exist.
- `500 Internal Server Error`: The server crashed or encountered a bug while processing the request (common target for hackers).

### Cookies (Maintaining State)
- Because HTTP is stateless, **cookies** are used to track users (login sessions, shopping carts).
- **The Flow:**
  1. Client sends request.
  2. Server creates a unique ID, stores it in backend database, and replies with header: `Set-Cookie: session_id=123`
  3. Client's browser saves the cookie.
  4. On next request, browser automatically includes: `Cookie: session_id=123`
- *Security Note:* Session Hijacking (stealing a cookie) allows attackers to impersonate a user without needing a password.

### Web Caching (Proxy Servers)
- A Web Cache is a middleman server that sits between the client and origin server. It acts as both a server (to the client) and a client (to the origin server).
- **Purpose:** Speed. It allows clients to receive data faster if the cache already has a copy of the requested object, reducing load on the origin server and the network bottleneck.
- **Conditional GET:** Used to ensure the cache doesn't serve stale data. The cache sends an `If-Modified-Since` header to the origin. If the data hasn't changed, the origin replies with `304 Not Modified` and an empty body, saving bandwidth.


# 2.3 Electronic Mail in the Internet

- **Three Major Components:** 
  1. **User Agents:** The email client (e.g., Outlook, Apple Mail).
  2. **Mail Servers:** The infrastructure that holds mailboxes and message queues.
  3. **SMTP (Simple Mail Transfer Protocol):** The protocol used to send mail between servers.

### SMTP vs. HTTP
- Both are text-based application-layer protocols that use TCP.
- **Push vs. Pull:** 
  - HTTP is a **pull** protocol (the client pulls data from the server).
  - SMTP is a **push** protocol (the sending server pushes data to the receiving server).
- **Message Format:** SMTP requires the message body to be strictly 7-bit ASCII. Multimedia must be encoded (e.g., via Base64) before sending.

### Mail Access Protocols
- SMTP is *only* used to push mail to the receiver's mail server. 
- To retrieve mail from your own mail server to your laptop/phone, you must use a **Pull** protocol:
  - **POP3 (Post Office Protocol v3):** Older, downloads the email and usually deletes it from the server. Very stateless.
  - **IMAP (Internet Mail Access Protocol):** Maintains folder structures and state across multiple devices (syncs read/unread status).
  - **HTTP:** Modern webmail (Gmail, Outlook.com) uses HTTP to pull the inbox data into the browser.
  
  # 2.4 DNS: The Internet's Directory Service

- **DNS (Domain Name System)** is a distributed database implemented in a hierarchy of DNS servers, and an application-layer protocol that allows hosts to query this database.
- It primarily runs over **UDP** on **port 53**.
- DNS is complex at the edge: it is a core piece of internet infrastructure, but it is implemented entirely as Application Layer software running on end systems, not inside the network core routers.

## 2.4.1 Services Provided by DNS

- **Hostname to IP Address Translation:** The main purpose. Translating human-readable names (`google.com`) to machine-routable IPs (`142.250.190.46`).
- **Host Aliasing:** A host with a complicated canonical (real) name can have one or more alias names. DNS translates the alias to the canonical name.
- **Mail Server Aliasing:** Allows a company's email address (like `bob@yahoo.com`) to be simple, while the actual mail server hostname is much more complex. 
- **Load Distribution:** Busy sites (like Amazon) are replicated across multiple servers with different IPs. DNS can return a *set* of IP addresses for one domain and rotate the order of those IPs for each request, distributing the user traffic across all servers.

## 2.4.2 Overview of How DNS Works

- DNS is **NOT centralized**. A centralized DNS would suffer from:
  1. A single point of failure (if it crashes, the internet dies).
  2. Unmanageable traffic volume.
  3. Massive geographic distance delays (if the server is in NY, users in Australia suffer).
  4. Maintenance nightmares.

### The Distributed, Hierarchical Database
1. **Root DNS Servers:** The highest level. They do not know specific IPs. They return the IP addresses of the TLD servers. There are 13 logical root IPs globally.
2. **Top-Level Domain (TLD) Servers:** Responsible for domains like `.com`, `.org`, `.net`, and country codes (`.uk`, `.bd`). They return the IP addresses of Authoritative DNS servers.
3. **Authoritative DNS Servers:** Every organization with publicly accessible hosts must provide public DNS records. These servers hold the actual, final IP addresses for the target hostnames.

### The Local DNS Server (Resolver)
- It does not strictly belong to the hierarchy. 
- Provided by your ISP (or set to Google/Cloudflare).
- Acts as a proxy. When your browser needs an IP, it asks the Local DNS Server, which acts as the client and does all the fetching from the Root, TLD, and Authoritative servers on your behalf.

### Caching
- DNS extensively uses caching to reduce latency and network traffic.
- When a Local DNS server receives a reply, it caches the mapping in its local memory.
- Cached entries expire after a Time-To-Live (TTL), typically around 2 days.

## 2.4.3 DNS Records and Messages

- DNS servers store **Resource Records (RRs)**. 
- A Resource Record is a four-tuple: `(Name, Value, Type, TTL)`

### Common Record Types:
- **Type A:** `Name` is the hostname, `Value` is the IPv4 address (e.g., `relay1.bar.foo.com`, `145.37.93.126`).
- **Type NS:** `Name` is a domain, `Value` is the hostname of the authoritative DNS server that knows how to route that domain (e.g., `foo.com`, `dns.foo.com`).
- **Type CNAME:** `Value` is the canonical (real) hostname for the alias `Name` (e.g., `www.ibm.com`, `servereast.backup2.ibm.com`).
- **Type MX:** `Value` is the canonical name of a mail server associated with `Name`.

### DNS Message Format
- DNS uses the **exact same message format** for both Queries (Requests) and Replies (Responses).
- **Header Section (12 bytes):** Contains a 16-bit Identification number (to match replies to queries) and Flags (like `QR` to indicate if it's a query or response, and `Recursion Desired`).
- **Question Section:** Contains the Name being queried and the Type (A, MX, etc.).
- **Answer Section:** Contains the RRs for the name that was originally queried. (Empty in a query).
- **Authority Section:** Contains RRs of other authoritative servers.
- **Additional Section:** Contains helpful extra records (like the A record for the NS server listed in the Authority section).


---
## 2.4.x Security & Red Teaming Implications

Because DNS operates on connectionless UDP and is highly trusted by corporate firewalls, it is a primary vector for attackers.

- **DNS Exfiltration (Data Theft):**
  - **The Hack:** Firewalls rarely block outbound DNS UDP port 53 traffic. If an attacker compromises an internal machine, they can encode stolen data into a subdomain and request it (e.g., `GET-password123.attacker.com`). 
  - **The Result:** The local DNS resolver happily forwards the stolen data past the firewall to the attacker's Authoritative DNS server, which logs the request and steals the data.
- **DNS Spoofing (Man-in-the-Middle):**
  - **The Hack:** Since UDP has no handshake or verification, an attacker on a local network (like public Wi-Fi) can sniff a victim's DNS request for `bank.com`. 
  - **The Result:** The attacker races the router to send a forged DNS Reply back to the victim, mapping `bank.com` to the attacker's malicious IP. The victim's browser silently connects to the phishing site.
- **DNS Zone Transfers (Reconnaissance):**
  - **The Hack:** Red teamers will query a target's Authoritative server requesting a full copy of all its records (an `AXFR` request).
  - **The Result:** If misconfigured, the server dumps its entire database, revealing all hidden internal subdomains, dev servers, and infrastructure maps to the attacker.
- **DNS Amplification (DDoS):**
  - **The Hack:** Attackers send thousands of DNS Queries to public resolvers using IP Spoofing (forging the Source IP to be the victim's IP). 
  - **The Result:** The DNS resolvers send massive DNS Replies (often 50x larger than the query) to the victim, overwhelming their bandwidth and taking them offline.


# 2.5 Peer-to-Peer (P2P) File Distribution

- **The Scalability Problem:** In Client-Server architecture, if a server wants to send a massive file to **N** users, the server must transmit the file **N** times. The network burden scales linearly and creates a massive bottleneck.
- **The P2P Solution:** In P2P, each peer that downloads a chunk of the file also *uploads* that chunk to other peers. 
- **Self-Scalability:** As the number of peers increases, the demand increases, but the overall upload capacity of the network increases proportionally.

### BitTorrent Mechanics
- **Torrents & Chunks:** A file is broken into chunks (typically 256 KB). Peers in a **swarm** exchange these chunks.
- **The Tracker:** A central server that tracks the IP addresses of peers participating in the swarm. (Modern systems also use decentralized tracking like DHT).
- **Tit-for-Tat (Incentive):** BitTorrent prevents "leeching" (downloading without uploading). Your client will "choke" (stop sending data to) peers that refuse to upload to you, and "unchoke" the peers that provide you data at the highest rates.


# 2.6 Video Streaming and Content Distribution Networks (CDNs)

- Video accounts for the vast majority of all internet traffic.
- **DASH (Dynamic Adaptive Streaming over HTTP):**
  - Videos are not downloaded as one giant file. They are encoded at multiple quality levels (bitrates) and chopped into small, few-second segments.
  - The client (e.g., the YouTube player) continuously measures the current network bandwidth and dynamically requests the highest quality segment the network can currently handle without buffering.

### CDNs (Content Distribution Networks)
- **The Problem:** Serving a video from one mega-server in New York to users in Tokyo results in high propagation delay, high packet loss, and congested links.
- **The Solution:** A CDN is a network of geographically distributed edge servers holding cached copies of videos, images, and web assets.
- **Server Placement Philosophies:**
  1. **Enter Deep:** Placing CDN servers deep into the access networks of local ISPs (closer to the user, higher maintenance).
  2. **Bring Home:** Building larger server clusters at major Internet Exchange Points (IXPs) (fewer locations, lower maintenance, slightly higher delay).
- **DNS Interception:** CDNs rely heavily on DNS. When a user requests a video URL, the CDN intercepts the DNS query and returns the IP address of the edge server physically closest to the user, rather than the origin server.