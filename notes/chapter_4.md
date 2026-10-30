# Chapter 4 — Network Layer: Data Plane
>
> **Big picture:** The network layer moves packets across networks. Hosts create IP packets; routers inspect packet headers and forward them toward their destinations; middleboxes may additionally filter, translate, or inspect traffic.

## 1. Core concepts

- **Forwarding:** A router's local action of moving a packet from an input interface to the appropriate output interface.
- **Routing:** The network-wide process of determining paths and building the information routers use to forward packets.
- **Data plane:** Handles packets at forwarding time.
- **Control plane:** Computes or distributes the information that determines forwarding behaviour.
- **IP is best-effort:** It provides addressing and packet delivery across networks, but does not itself guarantee delivery, ordering, or reliability. Those guarantees, when needed, are handled elsewhere in the stack.

## 2. Inside a router — 4.2

A simplified router contains:

- **Input ports:** Receive frames, inspect packet headers, and perform forwarding lookups.
- **Switching fabric:** Transfers packets from input ports to output ports.
- **Output ports:** Queue and transmit packets.
- **Routing processor:** Runs control-plane functions and maintains routing/forwarding information.

### Queuing and scheduling

Queues form when packets arrive faster than they can be processed or transmitted.

| Method | Behaviour | Remember |
|---|---|---|
| FIFO | Transmit in arrival order | Simple; no prioritization |
| Priority queuing | Serve higher-priority queues first | Low-priority traffic can starve |
| Fair queuing / WFQ | Share service among flows | Reduces the chance that one flow dominates |

**Queueing** is where packets wait; **scheduling** decides which queued packet is sent next. These are useful QoS concepts for CCNA and useful context for congestion and resource-exhaustion problems. The switching-fabric hardware details are lower priority for my goals.

## 3. Internet Protocol — 4.3 

### IPv4 datagram: fields worth recognizing

| Field | Why it matters |
|---|---|
| Source / destination address | Identifies the packet's sender and intended destination at the IP layer |
| TTL | Decreased by each router; packet is discarded at zero to prevent endless circulation |
| Protocol | Identifies the payload protocol, e.g. TCP or UDP |
| Total Length | Length of the entire IPv4 datagram, header included |
| IHL / Header Length | Size of the IPv4 header |
| Header Checksum | Checks the IPv4 header (not the payload); updated when relevant header fields change |
| Identification, Flags, Fragment Offset | Allow IPv4 fragments belonging to the same original datagram to be identified and reassembled |

The usual IPv4 header is 20 bytes without options. Routers use the destination address to choose the next hop; the packet's link-layer frame is rebuilt for each link along the path.

### Fragmentation and MTU

- **MTU (Maximum Transmission Unit):** Maximum size of a network-layer packet that a link can carry in one frame, subject to the link technology.
- If an IPv4 datagram is too large for an outgoing link, it may be fragmented when fragmentation is permitted. The **DF (Don't Fragment)** flag prevents this; a router unable to forward the packet may discard it and send an ICMP error.
- **MF (More Fragments)** indicates that more fragments follow. **Fragment Offset** locates a fragment's data in the original datagram (in 8-byte units).
- IPv4 fragments are reassembled by the destination host, not by each router along the path.
- **IPv6 routers do not fragment packets.** The source can fragment using the IPv6 Fragment extension header.

**Security connection:** Fragmentation and inconsistent handling of fragments can complicate packet inspection. Firewalls and other inspection devices need to interpret/reassemble traffic consistently with the destination. Recognize the concept; detailed evasion techniques are outside this note.

### Addressing, subnetting, and CIDR

- An IP address has a **network prefix** and a **host/interface portion**. The prefix length says how many leading bits identify the network.
- **CIDR notation:** `192.0.2.0/24` means the first 24 bits are the prefix. The corresponding subnet mask is `255.255.255.0`.
- A router uses **longest-prefix matching**: among matching routes, it chooses the one with the most specific (longest) prefix.
- Be comfortable converting between prefix lengths, subnet masks, network addresses, address ranges, and broadcast addresses for IPv4.
- Practice subnetting and CIDR calculations by hand separately. Reading the section is not enough.

**Importance:** Subnetting is central to CCNA, routing, ACL design, network mapping, and understanding which hosts can communicate directly at the IP layer.

### DHCP

DHCP automatically supplies hosts with configuration such as an IP address, subnet mask/prefix, default gateway, and DNS server information.

Remember **DORA**:

1. **Discover** — client looks for a DHCP server.
2. **Offer** — server offers configuration.
3. **Request** — client requests the offered configuration.
4. **Acknowledge** — server confirms the lease.

DHCP commonly uses UDP and initially relies on broadcast communication because the client may not yet have an address.

### NAT and PAT

- **NAT (Network Address Translation):** A device changes IP address information as packets pass through it, commonly translating private internal addresses to a public address.
- **PAT / NAPT:** Also translates transport-layer port numbers, allowing many internal connections/devices to share one public IPv4 address.
- The NAT device keeps a **translation table** so returning traffic can be mapped to the appropriate internal endpoint.
- NAT changes the traditional end-to-end model and can complicate inbound connections and troubleshooting.

**Security connection:** NAT is not the same thing as a firewall and should not be treated as a complete security control. Translation may hide internal addressing from the outside, but filtering policy is a separate function.

### IPv6 essentials

- IPv6 uses **128-bit addresses** (IPv4 uses 32 bits).
- Addresses are written in hexadecimal groups separated by colons; consecutive zero groups can be compressed with `::` once in an address.
- IPv6 has a simplified fixed base header and uses **Hop Limit** in place of IPv4 TTL.
- IPv6 does not use an IPv4-style header checksum, and routers do not fragment packets.
- Learn the notation, address size, basic header differences, and the reason for IPv6 (vastly larger address space). Do not get stuck memorizing every extension header on the first pass.

## 4. Generalized forwarding and SDN — 4.4

Traditional IP forwarding commonly selects an output based on the destination IP prefix. **Generalized forwarding** can match on multiple packet-header fields.

**Match–action model:**

1. Inspect selected header fields.
2. Match them against a flow-table entry.
3. Apply the associated action, such as forward, drop, modify, or send to a controller.

**Software-Defined Networking (SDN):** Separates the control logic from packet-forwarding devices, allowing a logically centralized controller to program forwarding behaviour across the network.

Know the distinction between controller/control plane and switches' data plane, plus the purpose of flow tables. Focus on the concept rather than implementation details.

**Security connection:** Programmable rules make flexible filtering and traffic steering possible, but incorrect rules or a compromised/unavailable controller can affect many devices.

## 5. Middleboxes — 4.5

A **middlebox** is a device on the path that performs functions beyond basic IP forwarding.

- **NAT:** Translates addresses and possibly ports.
- **Firewall:** Enforces a traffic policy. A stateless filter checks packets against rules; a stateful firewall also tracks connection/flow state.
- **Deep Packet Inspection (DPI):** Examines more than basic network-layer headers, potentially inspecting transport/application protocol details.

**Security limits to remember:**

- Encryption restricts what a middlebox can see inside protected application traffic (unless it has a legitimate way to decrypt or inspect it at an endpoint/proxy).
- Fragmentation, tunnelling, and protocol ambiguity can make inspection harder if devices interpret traffic differently.
- A firewall's effectiveness depends on its rules, state tracking, placement, and visibility—not merely its presence.

## 6. Important parts

### Cybersecurity / vulnerability research

- Recognize IPv4 and IPv6 packet headers and understand TTL/Hop Limit, protocol numbers, lengths, and fragmentation fields.
- Understand how routers choose next hops and why longest-prefix matching matters.
- Know what DHCP, NAT/PAT, firewalls, and DPI change or inspect.
- Understand that network observations can be affected by NAT, filtering, fragmentation, and middlebox behaviour.

### CCNA

Prioritize IPv4 addressing and subnetting, routing-versus-forwarding, router packet handling, DHCP, NAT/PAT, IPv6 basics, ACL/firewall concepts, and QoS scheduling terminology.

