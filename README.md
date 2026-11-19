An OpenFlow 1.3 Software-Defined Networking (SDN) monitoring testbed built with **OS-Ken** and **Mininet** on Ubuntu 22.04 LTS. The project implements a 7-switch, 8-host binary tree topology with periodic flow and port statistics polling, packet-level protocol verification, and control-plane polling overhead benchmarking.

---

## Architecture Overview

* **Controller:** OS-Ken (`SDNMonitoringController`) listening on `127.0.0.1:6653` (OpenFlow 1.3)
* **Topology:** 3-tier binary tree (`s1` root, `s2–s3` aggregation, `s4–s7` edge) connecting 8 hosts (`h1–h8`) in subnet `10.0.0.0/24`
* **Host Addressing:**
  * `h1` (`10.0.0.1`, `00:00:00:00:00:01`) & `h2` (`10.0.0.2`, `00:00:00:00:00:02`) $\rightarrow$ `s4`
  * `h3` (`10.0.0.3`, `00:00:00:00:00:03`) & `h4` (`10.0.0.4`, `00:00:00:00:00:04`) $\rightarrow$ `s5`
  * `h5` (`10.0.0.5`, `00:00:00:00:00:05`) & `h6` (`10.0.0.6`, `00:00:00:00:00:06`) $\rightarrow$ `s6`
  * `h7` (`10.0.0.7`, `00:00:00:00:00:07`) & `h8` (`10.0.0.8`, `00:00:00:00:00:08`) $\rightarrow$ `s7`

---

## Repository Structure

```text
sdn-project/
├── controller.py                 # OS-Ken OpenFlow 1.3 L2 switch + periodic stats polling
├── topology.py                   # Mininet 7-switch, 8-host binary tree topology
├── captures/                     # Wireshark .pcapng protocol & attack captures
│   ├── openflow.pcapng           # OpenFlow handshake, FlowMod, StatsRequest/Reply
│   ├── arp_icmp.pcapng           # ARP resolution & ICMP echo traffic
│   ├── tcp_http.pcapng           # TCP 3-way handshake & HTTP GET exchange
│   ├── udp_iperf.pcapng          # Normal UDP stream via iperf3
│   ├── syn_flood.pcapng          # TCP SYN flood via hping3
│   └── udp_flood.pcapng          # UDP flood via hping3
├── results/
│   └── polling_overhead.csv      # Raw CPU % and stats message rate across 9 runs
└── README.md
