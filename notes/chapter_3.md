# 3.1 Introduction and Transport-Layer Services

- The Transport Layer sits directly above the Network Layer. It provides **logical communication** between application processes running on different hosts.
- From the application's perspective, it looks like the two processes are directly connected by a pipe, even if they are physically on opposite sides of the planet.
- Transport protocols are implemented in the **end systems** (your laptop, a server), never in the network routers. Routers only read up to the Network Layer (IP).

### Transport Layer vs. Network Layer
- **Network Layer (IP):** Provides logical communication between **Hosts (Computers)**. Like a mail delivery truck moving mailbags between two houses.
- **Transport Layer (TCP/UDP):** Provides logical communication between **Processes (Applications)**. Like the parents in those houses sorting the mail and handing specific letters to specific kids.
- The transport layer relies on the network layer's delivery service, but it can enhance it (e.g., IP is unreliable, but TCP adds reliability on top).

### The Internet's Transport Protocols
1. **TCP (Transmission Control Protocol):** Provides reliable, in-order data delivery, congestion control, flow control, and connection setup.
2. **UDP (User Datagram Protocol):** Provides an unreliable, unordered, "best-effort" delivery service. No frills, just speed.


# 3.2 Multiplexing and Demultiplexing

- A single computer often runs multiple networked applications at once (e.g., downloading a file via FTP while loading a web page via HTTP). 
- When the Network layer (IP) hands a payload up to the Transport layer, the Transport layer must figure out exactly which application gets the data. This is called **Demultiplexing**.

### The Socket Interface
- Processes do not hand data directly to the network; they hand data to a **socket**.
- To route data to the correct socket, each transport-layer segment must have specific fields:
  1. **Source Port Number** (16 bits, 0 to 65535)
  2. **Destination Port Number** (16 bits, 0 to 65535)
- Ports 0–1023 are **Well-Known Ports** (e.g., 80 for HTTP, 443 for HTTPS, 22 for SSH) and are strictly reserved for standard server applications.

### Demultiplexing in UDP (Connectionless)
- A UDP socket is fully identified by a **two-tuple**: `(Destination IP, Destination Port)`.
- If two UDP packets arrive from entirely different Source IPs, but both have the same Destination Port (e.g., Port 53 for DNS), the OS sends them *both to the exact same socket process*.

### Demultiplexing in TCP (Connection-Oriented)
- A TCP socket is fully identified by a **four-tuple**: `(Source IP, Source Port, Destination IP, Destination Port)`.
- If two TCP packets arrive from two different Source IPs, but both are aimed at Destination Port 80, the OS will route them to **two completely separate sockets**. 
- This is how a single web server (like Nginx on Port 80) can handle thousands of concurrent client connections without mixing up the data. Each new client gets a dedicated socket spawned via the `accept()` function.

### Red Team Context: Port Scanning
- When an attacker runs `nmap -sS target_ip`, the tool works by rapidly manipulating the Demultiplexing process. Nmap fires packets at all 65,535 possible Destination Ports. If the target OS demultiplexes a packet and finds a listening socket, it replies (revealing an open port). If it demultiplexes to a port with no socket, the OS returns a specific error (an ICMP error for UDP, or a TCP RST), revealing the port is closed.


# 3.3 Connectionless Transport: UDP

- UDP (User Datagram Protocol) does the bare minimum required for a transport protocol. It takes data from the application, attaches source/destination ports for demultiplexing, adds a checksum for basic error checking, and immediately fires it into the network.
- **There is no handshake.** The sender does not ask if the receiver is ready.
- **There is no reliability.** Packets can arrive out of order, or not arrive at all. UDP does not care, and it does not retransmit.

### The UDP Header
The UDP header is incredibly lightweight—only **8 bytes** total (compared to TCP's 20 bytes).
1. **Source Port** (2 bytes)
2. **Destination Port** (2 bytes)
3. **Length** (2 bytes): The length of the entire UDP segment (header + data).
4. **Checksum** (2 bytes): A basic mathematical check to see if bits flipped during transit. (If a checksum fails, UDP simply drops the packet).

## Why do Applications Choose UDP over TCP?

Given that UDP is unreliable and unmanaged, why would an application developer ever choose it? It comes down to **control and speed**.

### 1. Finer application-level control over what data is sent, and when.
- Under TCP, if a packet is lost, TCP completely halts transmission and refuses to send any new data until that specific packet is successfully retransmitted and acknowledged.
- This is catastrophic for real-time applications. If you are on a Zoom call, you don't want the video to freeze for 2 seconds while TCP desperately tries to retransmit a single dropped frame from 3 seconds ago. 
- With UDP, the application (Zoom) gets to decide: "Just skip the dropped frame and render the next one."

### 2. No connection establishment (No Handshake Delay)
- TCP requires a 3-way handshake (`SYN`, `SYN-ACK`, `ACK`) before a single byte of data can be sent. This introduces a minimum of one full Round Trip Time (RTT) of delay.
- UDP just starts blasting data immediately. This is critical for protocols like **DNS**. If DNS used TCP, every single web page load would be significantly delayed by handshake overhead.

### 3. No connection state
- A TCP server must allocate memory buffers and state variables for *every single connected client* (which we saw exploited in SYN Floods and Slowloris).
- A UDP server maintains zero connection state. This means a UDP server can support vastly more active clients than a TCP server on the same hardware hardware.

### 4. Small packet header overhead
- UDP's 8-byte header means more of the network bandwidth is dedicated to the actual payload, rather than TCP's 20-byte overhead.

### Red Team Context: UDP Scanning and Exploitation
- **UDP Port Scanning:** Scanning UDP (e.g., `nmap -sU`) is notoriously difficult. If you send a UDP packet to an open port, the application usually just ignores it (no response). If you send it to a closed port, the OS might send back an ICMP "Port Unreachable" error. Attackers have to infer that "no response" *probably* means "open," which makes scans slow and inaccurate.
- **UDP Amplification Attacks (DDoS):** Because UDP has no handshake, it is trivial to spoof the Source IP address. An attacker can forge a DNS request (UDP port 53) so that the Source IP looks like the victim's IP. The attacker sends a tiny 60-byte request to a DNS server, and the DNS server sends a massive 3000-byte response directly to the victim. The attacker uses a botnet to do this millions of times, amplifying their attack power by 50x and crushing the victim's bandwidth.


# 3.4 Principles of Reliable Data Transfer (rdt)

- **The Problem:** The Network Layer (IP) is unreliable. It drops packets, flips bits, and delivers packets out of order.
- **The Goal:** The Transport Layer must build a reliable data transfer protocol (`rdt`) on top of this unreliable channel. 
- *Kurose & Ross teach this by building a protocol from scratch, starting with a perfect channel and adding real-world flaws one by one.*

### The Evolution of rdt
1. **rdt1.0 (The Perfect Channel):** Assumes the underlying network never loses packets or flips bits. (Theoretical only).
2. **rdt2.0 (The Noisy Channel):** Assumes bits can be corrupted in transit.
   - *Solution:* Introduces **ARQ (Automatic Repeat reQuest)**. Requires three things:
     1. Checksums (Error Detection).
     2. Receiver feedback: ACKs (Acknowledge) and NAKs (Negative Acknowledge).
     3. Retransmission by the sender if a NAK is received.
3. **rdt2.1 (The Flawed ACK Problem):** What if the ACK or NAK itself is corrupted? The sender resends the packet, but the receiver doesn't know if it's new data or a duplicate.
   - *Solution:* Introduces **Sequence Numbers** (0 and 1). The receiver can look at the sequence number and discard duplicates.
4. **rdt2.2 (NAK-Free):** Simplifies the protocol by removing NAKs. If the receiver gets a corrupted packet, it simply sends an ACK for the *last successfully received packet*. A **Duplicate ACK** triggers a retransmission.
5. **rdt3.0 (The Lossy Channel):** Assumes whole packets (or ACKs) can vanish into the void. 
   - *Solution:* Introduces a **Countdown Timer**. The sender starts a timer. If it doesn't receive an ACK before the timer expires, it assumes loss and retransmits. (This is a *Stop-and-Wait* protocol).

### Pipelining (Fixing rdt3.0's Performance)
- *Stop-and-Wait* is mathematically reliable but terribly slow. The sender spends 99% of its time waiting for an ACK.
- **Pipelining** allows the sender to have multiple unacknowledged packets in flight simultaneously, drastically increasing throughput. 
- Pipelining requires two new error-recovery protocols:

#### Go-Back-N (GBN)
- **Cumulative ACKs:** An `ACK n` means "I have received all packets up to and including $n$."
- **Receiver Behavior:** If Packet 2 is lost, the receiver discards packets 3, 4, and 5 because they are out of order. 
- **Sender Behavior:** Uses a single timer for the oldest unacknowledged packet. If it times out, the sender *Goes Back N* and retransmits the entire window (2, 3, 4, and 5).

#### Selective Repeat (SR)
- **Individual ACKs:** The receiver ACKs each packet individually.
- **Receiver Behavior:** If Packet 2 is lost, the receiver **buffers** packets 3, 4, and 5.
- **Sender Behavior:** Uses a separate logical timer for every packet. It only retransmits the specific packet that was lost (Packet 2).


# 3.5 Connection-Oriented Transport: TCP

- TCP is built directly on the principles of `rdt3.0`, Go-Back-N, and Selective Repeat.
- It is **Point-to-Point** (one sender, one receiver—no multicasting).
- It is **Full-Duplex** (data flows in both directions simultaneously).
- TCP views data as an unstructured, ordered **stream of bytes**, not as individual packets.

### The TCP Header
- **Sequence Number:** The byte-stream number of the *first byte* in the segment's data. (If a segment contains bytes 1000–1999, the Seq # is 1000).
- **Acknowledgment Number:** The sequence number of the *next byte* the host expects to receive. (Cumulative ACK).
- **Receive Window (`rwnd`):** Used for Flow Control. Tells the sender how many bytes the receiver's buffer can handle.
- **Flags:** `ACK`, `SYN`, `FIN`, `RST`, `PSH`, `URG`.

### TCP Reliability Mechanisms
- **Single Retransmission Timer:** TCP uses a single timer (like Go-Back-N). The timer duration (`TimeoutInterval`) dynamically adjusts based on the smoothed `EstimatedRTT` and network jitter (`DevRTT`).
- **Fast Retransmit:** If a sender receives **3 duplicate ACKs** for the same data, it assumes the packet was lost and retransmits it immediately, *before* the timer expires. (This prevents long delays).

### TCP Flow Control
- Flow control ensures the sender does not overwhelm the receiver's application memory buffer.
- The receiver calculates its free buffer space and advertises it in the `rwnd` header field.
- If `rwnd = 0`, the sender halts transmission (except for 1-byte probes to check if the window opens again).

### TCP Connection Management (The 3-Way Handshake)
Before any data is exchanged, the two hosts must establish connection parameters (like Initial Sequence Numbers).
1. **SYN:** Client sends a segment with the `SYN` flag set to 1, and a random Initial Sequence Number (Client_ISN).
2. **SYN-ACK:** Server allocates buffers, replies with `SYN` = 1, `ACK` = Client_ISN + 1, and its own random Server_ISN.
3. **ACK:** Client replies with `ACK` = Server_ISN + 1. (Data can be attached to this third step).

*Security Note:* Attackers exploit Step 2. By sending thousands of `SYN` packets but never sending the final `ACK` (a SYN Flood), they exhaust the server's memory. Modern OSs defend against this using **SYN Cookies**—cryptographically generating the Server_ISN so no memory is allocated until the final ACK returns.

# 3.6 Principles of Congestion Control

- **Flow Control vs. Congestion Control:**
  - *Flow Control* protects the receiving application's memory buffer.
  - *Congestion Control* protects the physical network (routers and links) between the sender and receiver.
- **The Cost of Congestion:** When routers get overwhelmed, queues fill up and packets are dropped. This forces the sender to retransmit the dropped packets, which means the network is now spending its scarce bandwidth transmitting the exact same data twice (wasted capacity).

### Approaches to Congestion Control
1. **Network-Assisted Congestion Control:** Routers actively send feedback to the sender (e.g., an "I'm congested" packet or setting a specific bit in a header). *Used in ATM and some modern datacenter protocols (ECN).*
2. **End-to-End Congestion Control:** The network provides zero direct feedback. The end systems (sender and receiver) must *infer* congestion based on observed behavior (packet loss or delay). *This is the approach taken by TCP.*

# 3.7 TCP Congestion Control

- TCP uses **end-to-end congestion control**. 
- **The Core Premise:** TCP assumes that packet loss (indicated by a timeout or 3 duplicate ACKs) is caused by a congested router dropping the packet. 

### The Congestion Window (`cwnd`)
- The TCP sender maintains a variable called `cwnd` (Congestion Window). 
- The sender's actual transmission rate is limited by the minimum of the Receive Window (`rwnd`) and the Congestion Window (`cwnd`).
  - `Rate ≤ min(cwnd, rwnd) / RTT`

### The AIMD Algorithm (Additive Increase, Multiplicative Decrease)
TCP probes the network to find the maximum possible bandwidth without causing drops. It does this via a "sawtooth" behavior.

1. **Slow Start (Exponential Growth):**
   - When a connection begins, `cwnd` is set to 1 MSS (Maximum Segment Size).
   - For every ACK received, `cwnd` increases by 1 MSS. (This effectively doubles the window size every RTT).
   - Despite the name, this is rapid, exponential growth.
   - It ends when a packet is lost, or when `cwnd` reaches a threshold variable called `ssthresh` (Slow Start Threshold).

2. **Congestion Avoidance (Additive Increase):**
   - Once `cwnd` hits `ssthresh`, TCP stops exponential growth.
   - It enters a probing phase, increasing `cwnd` by only 1 MSS *per entire RTT* (linear growth).

3. **Reacting to Loss (Multiplicative Decrease):**
   - TCP reacts differently depending on *how* the packet was lost:
   - **Loss by 3 Duplicate ACKs (Fast Recovery):** Implies the network is congested, but some packets are still getting through. TCP cuts `ssthresh` in half, sets `cwnd` to the new `ssthresh` + 3 MSS, and resumes Additive Increase.
   - **Loss by Timeout:** Implies severe congestion (deadlock). TCP cuts `ssthresh` in half, but slams `cwnd` all the way down to **1 MSS**, forcing it to restart the Slow Start phase.

### TCP Fairness
- When multiple TCP connections share a single bottleneck link, the AIMD algorithm naturally forces them to share the bandwidth equally.
- Because they all cut their speeds in half upon congestion, and climb at the same linear rate, they eventually converge to an equal share.
- *Caveat:* UDP applications (which do not use congestion control) and applications that open multiple parallel TCP connections (like browsers or botnets) can easily cheat this fairness.