# Chapter 5

## Network Layer: Control Plane

### 5.1 Introduction

The network-layer control plane determines how datagrams are routed through a network and how routers obtain the information used to populate their forwarding tables.

- **Data plane:** Performs local packet forwarding at a router using forwarding-table entries.
- **Control plane:** Computes and distributes the information that determines forwarding behaviour.
- **Routing:** Selects paths through a network. Routing protocols and algorithms operate in the control plane.
- **Forwarding:** Moves a packet from an input interface to an output interface within one router.

Two control-plane architectures are common:

- **Per-router control:** Each router runs routing protocols and computes its own forwarding state while exchanging routing information with other routers.
- **Logically centralized control (SDN):** A controller computes or manages forwarding state and communicates it to network devices. The control function is logically centralized, although the controller itself may be distributed.

### 5.2 Routing Algorithms

A network can be represented as a graph, where routers are vertices and links are edges. Each edge has a cost, which may represent configured administrative cost, bandwidth-related cost, delay, or another metric. A route is a sequence of links between a source and destination. A least-cost route minimizes the sum of its link costs.

Routing algorithms are commonly classified as:

- **Global (link-state):** Routers obtain a view of the network topology and link costs, then independently calculate shortest paths.
- **Decentralized (distance-vector):** Routers exchange path-cost information with directly connected neighbours and calculate routes from those neighbours' advertised distances.
- **Static:** Routes are configured manually and change only when configuration is changed.
- **Dynamic:** Routes adapt to topology or policy changes through routing protocols.

#### 5.2.1 Link-State (LS) Routing

In link-state routing, each router discovers its directly connected neighbours and the cost of each link. It distributes this information through link-state advertisements (LSAs), which are flooded through the routing domain. Routers use the collected information to construct a link-state database representing the topology.

Each router runs **Dijkstra's shortest-path algorithm** with itself as the root of the graph. The resulting shortest-path tree is used to determine the next hop for each reachable destination.

Dijkstra's algorithm maintains:

- A set of nodes whose least-cost paths from the source have been finalized.
- A tentative least cost from the source to each node not yet finalized.
- The predecessor of each node on its currently known least-cost path.

The algorithm repeatedly selects the unfinalized node with the smallest tentative cost, finalizes it, and updates the tentative costs of its neighbours. When all reachable nodes have been processed, the predecessor relationships define the shortest-path tree.

Link-state properties:

- Routers in the same link-state domain build synchronized topology databases.
- Each router computes routes independently from the shared topology information.
- A topology change is advertised and causes affected routers to recalculate paths.
- Link-state flooding and topology storage consume bandwidth and memory.
- Convergence depends on detecting changes, distributing updated information, and recalculating routes.

#### 5.2.2 Distance-Vector (DV) Routing

In distance-vector routing, a router does not need a complete network topology map. It maintains an estimate of the least cost to each destination and exchanges its distance vector with neighbouring routers.

The method is based on the Bellman-Ford equation:

\[
D_x(y)=\min_{v\in N(x)}\{c(x,v)+D_v(y)\}
\]

where:

- \(D_x(y)\) is router \(x\)'s current estimated cost to destination \(y\).
- \(N(x)\) is the set of neighbours directly connected to \(x\).
- \(c(x,v)\) is the link cost from \(x\) to neighbour \(v\).
- \(D_v(y)\) is neighbour \(v\)'s advertised cost to destination \(y\).

For each destination, router \(x\) adds the cost to reach a neighbour to that neighbour's advertised cost to the destination. It selects the neighbour that gives the lowest total cost as the next hop.

Distance-vector operation is iterative and distributed:

1. Each router initializes the cost to itself as zero, directly connected destinations to their link costs, and unknown destinations to infinity.
2. Routers exchange distance vectors with their neighbours.
3. Each router recalculates its estimates using the Bellman-Ford equation.
4. Updated vectors are sent to neighbours when route information changes, eventually reaching a stable state if the network and costs remain stable.

Distance-vector properties:

- Routers exchange information with neighbours rather than flooding a complete topology map.
- A router's route calculation depends on the information received from neighbours.
- Updates can propagate incrementally after a topology or cost change.
- Temporary routing loops and slow convergence can occur after failures.

**Count-to-infinity** is a distance-vector problem in which routers may repeatedly increase a route's metric while incorrectly believing that another router has a path to a failed destination. The process continues until the metric reaches the protocol's defined infinity.

Common loop-reduction techniques include:

- **Split horizon:** A route learned from a neighbour is not advertised back to that same neighbour.
- **Poisoned reverse:** A route learned from a neighbour is advertised back to it with an infinite metric.
- **Triggered updates:** A router sends an update when route information changes rather than waiting only for a periodic update.

Split horizon and poisoned reverse reduce some loops but do not eliminate every possible routing loop in all topologies.

#### Link-State and Distance-Vector Comparison

| Property | Link-state | Distance-vector |
|---|---|---|
| Information exchanged | Link-state information about links and topology | Estimated costs to destinations |
| Network knowledge | Topology database for the routing domain | Neighbour-provided distance information |
| Main algorithm | Dijkstra | Bellman-Ford-based calculation |
| Distribution | Flooding of link-state advertisements | Exchanges with neighbours |
| Route calculation | Each router computes a shortest-path tree | Each router calculates costs using neighbours' vectors |
| Notable concern | Flooding and topology-database overhead | Loops and count-to-infinity behaviour |

### 5.3 Intra-AS Routing in the Internet: OSPF

An **Autonomous System (AS)** is a group of IP networks and routers administered under a common routing policy. An AS is identified by an Autonomous System Number (ASN).

An **Interior Gateway Protocol (IGP)** distributes routing information within an AS. **Open Shortest Path First (OSPF)** is a link-state IGP. OSPF routers exchange link-state information, build a link-state database, and use Dijkstra's algorithm to calculate shortest paths.

OSPF characteristics:

- Operates within an autonomous system.
- Uses link-state advertisements and reliable flooding to distribute topology information.
- Calculates routes using a shortest-path-first algorithm.
- Uses a configurable link cost as its routing metric; the cost is commonly associated with interface bandwidth.
- Supports equal-cost multipath, allowing traffic to use multiple routes with the same cost.
- Supports authentication of routing protocol exchanges.
- Supports hierarchical routing through areas.

#### OSPF Areas

Large OSPF networks can be divided into areas to limit the scope of link-state information and reduce routing overhead. Routers within an area maintain that area's link-state database. Inter-area routing is coordinated through the OSPF backbone, **Area 0**.

Important OSPF router roles include:

- **Internal router:** Has interfaces belonging to a single OSPF area.
- **Area Border Router (ABR):** Connects one or more OSPF areas to the backbone or connects multiple areas.
- **Autonomous System Boundary Router (ASBR):** Introduces routes learned from outside the OSPF routing domain.

On multiaccess networks, OSPF can elect a **Designated Router (DR)** and a **Backup Designated Router (BDR)** to reduce the number of adjacencies and simplify link-state exchange.

OSPFv2 is used for IPv4 routing. OSPFv3 extends OSPF to support IPv6. OSPF is carried directly over IP rather than over TCP or UDP; its IP protocol number is 89.

### 5.4 Routing Among the ISPs: BGP

The Internet consists of many independently administered autonomous systems. Routing between autonomous systems is called **inter-AS routing**. The Internet's principal inter-domain routing protocol is **Border Gateway Protocol (BGP)**.

BGP is a **path-vector** protocol. It advertises network-layer reachability information together with path attributes, including information about the autonomous systems through which a route has passed. BGP is often described as the glue that connects the Internet's autonomous systems.

#### 5.4.1 Role of BGP

BGP distributes reachability information for IP prefixes between autonomous systems and applies routing policies to select routes. It is not simply a shortest-path algorithm: economic relationships, traffic-engineering preferences, security policies, and administrative decisions affect route selection.

Two forms of BGP peering are:

- **eBGP (External BGP):** Exchanges routes between routers in different autonomous systems.
- **iBGP (Internal BGP):** Distributes BGP-learned routes among routers within the same autonomous system.

BGP uses TCP port 179 for its peer sessions. BGP peers exchange messages such as OPEN, UPDATE, KEEPALIVE, and NOTIFICATION.

#### 5.4.2 Advertising BGP Route Information

A BGP route advertisement associates a reachable IP prefix with path attributes. An UPDATE message can advertise new or changed routes and withdraw routes that are no longer available.

Important path attributes include:

| Attribute | Meaning |
|---|---|
| AS-PATH | Sequence of autonomous systems through which the route advertisement has passed; also supports loop detection |
| NEXT-HOP | IP address of the next router to use toward the advertised destination |
| LOCAL-PREF | Preference assigned within an AS; higher values are preferred |
| MED (MULTI_EXIT_DISC) | Can suggest a preferred entry point into an AS to a neighbouring AS; lower values are generally preferred when compared under the applicable decision process |
| ORIGIN | Indicates how the route was originated into BGP |

An AS prepends its ASN to the AS-PATH when advertising a route to an external peer. When an AS receives a route containing its own ASN in the path, it can reject the route to prevent an inter-AS routing loop.

#### 5.4.3 Determining the Best Routes

A BGP router may learn multiple routes to the same destination prefix. Its BGP decision process chooses a preferred route using path attributes and locally configured policy.

Common influences include:

- Local preference within the AS.
- AS-PATH length.
- ORIGIN type.
- MED, where applicable.
- eBGP versus iBGP route source.
- Interior cost to reach the BGP NEXT-HOP, often associated with hot-potato routing.
- Vendor-specific or locally configured tie-breaking rules.

Route selection is policy-driven. A shorter AS-PATH does not necessarily win over a route with a higher local preference. Exact decision order and additional tie-breakers can vary by implementation and configuration.

**Hot-potato routing** is the practice of choosing an exit point that minimizes the cost within the local AS to reach the next-hop router, often handing traffic to another AS as soon as practical.

#### 5.4.4 IP Anycast

With IP anycast, the same IP prefix is announced from multiple geographically or topologically distributed locations. Routing directs a client to one of the available locations, commonly the one considered closest according to routing policy and path selection.

Anycast is used for distributed services such as DNS and content delivery. It can improve service availability and distribute traffic, although routing changes can alter which instance receives traffic.

#### 5.4.5 Routing Policy

ASes apply local policies to decide which routes to accept, prefer, advertise, or export. Policies reflect relationships such as customer-provider and peer-to-peer arrangements, as well as operational and security requirements.

A network may prefer customer-learned routes over peer- or provider-learned routes because customer traffic can have different economic value. An AS may also decline to advertise certain routes to particular neighbours to control transit traffic.

BGP is therefore both a reachability-distribution protocol and a policy mechanism. The selected path is not necessarily the path with the fewest routers, lowest latency, or lowest total physical-link cost.

BGP misconfiguration can cause route leaks, while malicious or accidental announcements can cause prefix hijacking or traffic redirection. Route Origin Authorizations (ROAs) and Route Origin Validation (RPKI-based origin validation) help networks check whether an AS is authorized to originate a prefix. Origin validation does not, by itself, validate every AS in the complete path.

### 5.5 The SDN Control Plane

Software-Defined Networking (SDN) separates network control logic from packet-forwarding devices. A logically centralized controller maintains a view of the network and communicates forwarding instructions to switches or routers. The controller can be implemented as a distributed system for availability and scalability.

Core SDN components:

- **Data-plane devices:** Forward packets using installed rules and expose programmable interfaces.
- **SDN controller:** Maintains network state, computes or coordinates forwarding behaviour, and communicates with data-plane devices.
- **Network-control applications:** Express higher-level policies and network functions, such as access control, traffic engineering, and load balancing.
- **Southbound interface:** Communication between the controller and data-plane devices.
- **Northbound interface:** Interface through which control applications interact with the controller.

OpenFlow is a historically important southbound protocol. It enables a controller to manage flow tables on compatible switches. Flow entries can contain match fields, counters, priorities, and actions such as forwarding, dropping, modifying headers, or directing packets to the controller.

The controller does not ordinarily process every packet. It installs rules that the data-plane devices apply locally. A packet that does not match an installed rule may be handled according to a table-miss rule, which can drop it, send it to another table, or forward it to the controller, depending on configuration.

SDN provides centralized policy management, programmability, and network-wide traffic control. Its security and reliability depend on controller protection, authenticated control channels, correct authorization, resilient controller design, and safe handling of flow-table resources.

### 5.6 ICMP: Internet Control Message Protocol

The Internet Control Message Protocol (ICMP) supports error reporting and diagnostic functions for IP. ICMP messages are carried inside IP datagrams. ICMP does not provide application data transport like TCP or UDP.

Important ICMPv4 message types include:

| Message | Purpose |
|---|---|
| Echo Request / Echo Reply | Used by tools such as `ping` to test reachability and round-trip response |
| Destination Unreachable | Indicates that a datagram cannot be delivered for a specified reason |
| Time Exceeded | Indicates that a packet's TTL expired in transit or that fragment reassembly timed out |
| Redirect | Informs a host of a potentially better first-hop router |
| Parameter Problem | Indicates an issue with an IP header field |

ICMP error messages include part of the original packet so the sender can identify the traffic associated with the error. Some ICMP messages are not generated in response to other ICMP error messages, and routers do not send certain errors for broadcast or multicast traffic.

**Traceroute** uses the IP hop limit/TTL and ICMP responses to infer the sequence of routers along a path. It sends probes with progressively increasing TTL values. A router that reduces a probe's TTL to zero normally returns an ICMP Time Exceeded message. The destination may return a response indicating that the probe reached it. Implementations differ in probe protocol and response type.

ICMPv6 performs corresponding functions for IPv6 and is also integral to IPv6 operation. ICMPv6 includes Neighbor Discovery messages used for functions such as router discovery and address resolution. Blocking all ICMPv6 indiscriminately can break essential IPv6 functionality, including Path MTU Discovery, which relies on Packet Too Big messages.

### 5.7 Network Management, SNMP, and NETCONF/YANG

Network management covers monitoring, configuration, fault detection, performance measurement, and maintenance of network devices and services.

A network-management system commonly includes:

- **Managed devices:** Routers, switches, servers, firewalls, and other network elements.
- **Management agents or servers:** Software on managed devices that exposes operational or configuration information.
- **Management station or manager:** The system used by administrators and management applications.
- **Management protocol:** The protocol used to retrieve information, change configuration, and send notifications.

#### 5.7.1 Network Management Framework

Management activities include:

- Fault management: Detecting, isolating, and resolving failures.
- Configuration management: Maintaining device and service configuration.
- Accounting and administration: Tracking resource use and administrative state.
- Performance management: Measuring availability, throughput, delay, errors, and resource utilization.
- Security management: Controlling access and monitoring security-related events.

#### 5.7.2 SNMP and MIB

The **Simple Network Management Protocol (SNMP)** is used to monitor and manage network devices. An SNMP manager communicates with SNMP agents running on managed devices.

A **Management Information Base (MIB)** defines managed objects and their structure. Each object is identified through an Object Identifier (OID), arranged in a hierarchical namespace. Objects can represent interface counters, device identity, status, error counts, and other operational information.

Common SNMP operations include:

- **GET:** Retrieve the value of a managed object.
- **GET-NEXT / GET-BULK:** Retrieve subsequent objects or groups of values.
- **SET:** Change the value of a writable managed object.
- **RESPONSE:** Return the result of a request.
- **TRAP / INFORM:** Notify a management system about an event; INFORM is acknowledged, while a TRAP is not.

SNMP commonly uses UDP port 161 for requests and responses and UDP port 162 for notifications. SNMPv1 and SNMPv2c use community strings and do not provide the security guarantees of SNMPv3. SNMPv3 supports authentication, message integrity, privacy through encryption, and access control.

#### 5.7.3 NETCONF and YANG

**NETCONF** is a network configuration protocol used by management systems to retrieve, install, modify, and delete configuration on network devices. It provides structured operations and configuration datastores rather than relying only on individual command-line instructions.

NETCONF operations include:

- `get`: Retrieve configuration and state data.
- `get-config`: Retrieve configuration from a selected datastore.
- `edit-config`: Modify configuration.
- `copy-config`: Copy configuration between datastores.
- `delete-config`: Delete a configuration datastore where permitted.
- `lock` and `unlock`: Control concurrent access to a datastore.
- `commit`: Apply candidate configuration to running configuration when the relevant capability is supported.

NETCONF commonly uses SSH as its transport. Its standard SSH port is TCP 830.

**YANG** is a data-modeling language used to define the structure, types, constraints, configuration data, operational state data, RPCs, and notifications exchanged through network-management systems. YANG provides a structured model that allows management clients and network devices to interpret configuration consistently.

NETCONF defines management operations and transport interactions; YANG defines the data model used to represent configuration and state. Together, they support structured and automatable network configuration.

#### SNMP and NETCONF/YANG Comparison

| SNMP | NETCONF with YANG |
|---|---|
| Commonly used for monitoring and operational data collection | Commonly used for structured configuration and state retrieval |
| Organizes managed objects using MIBs and OIDs | Organizes data using YANG models and hierarchical data trees |
| Uses operations such as GET, SET, and notifications | Uses operations such as `get`, `get-config`, and `edit-config` |
| Commonly uses UDP 161/162 | Commonly uses SSH over TCP 830 |
| SNMPv3 provides authentication, integrity, and privacy | Security depends on the transport, authorization, and server/client configuration |

### 5.8 Summary

The network-layer control plane computes and manages routes and forwarding state. Link-state algorithms distribute topology information and use Dijkstra's algorithm, while distance-vector algorithms exchange destination costs and use Bellman-Ford-based calculations. OSPF applies link-state routing within an autonomous system. BGP exchanges reachability and path information between autonomous systems while applying routing policies. SDN separates network control logic from data-plane forwarding devices. ICMP supports IP error reporting and diagnostics. SNMP and NETCONF/YANG provide mechanisms and data models for monitoring and configuring network infrastructure.
