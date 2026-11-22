# SDN Telemetry and Anomaly Detection System

An OpenFlow 1.3 Software-Defined Networking (SDN) monitoring, real-time telemetry, and automated DDoS mitigation testbed built with **OS-Ken**, **Mininet**, **Prometheus**, and **Grafana** on Ubuntu 22.04 LTS.

The project implements a 7-switch, 8-host binary tree topology with periodic flow and port statistics polling, packet-level protocol verification, control-plane polling overhead benchmarking, live Prometheus/Grafana telemetry visualization, and real-time **Exponentially Weighted Moving Average (EWMA)** anomaly detection with automated OpenFlow mitigation.

---

## Architecture Overview

* **Controller:** OS-Ken (`SDNMonitoringController`) listening on `127.0.0.1:6653` (OpenFlow 1.3)
* **Topology:** 3-tier binary tree (`s1` root, `s2-s3` aggregation, `s4-s7` edge) connecting 8 hosts (`h1-h8`) in subnet `10.0.0.0/24`
* **Host Addressing:**
  * `h1` (`10.0.0.1`, `00:00:00:00:00:01`) & `h2` (`10.0.0.2`, `00:00:00:00:00:02`) --> `s4`
  * `h3` (`10.0.0.3`, `00:00:00:00:00:03`) & `h4` (`10.0.0.4`, `00:00:00:00:00:04`) --> `s5`
  * `h5` (`10.0.0.5`, `00:00:00:00:00:05`) & `h6` (`10.0.0.6`, `00:00:00:00:00:06`) --> `s6`
  * `h7` (`10.0.0.7`, `00:00:00:00:00:07`) & `h8` (`10.0.0.8`, `00:00:00:00:00:08`) --> `s7`
* **Telemetry & Detection Pipeline:**
  * `telemetry.py` exposes live Prometheus metrics (`port_rx_pps`, `port_rx_bps`, `anomaly_alarms_total`) scraped via `prometheus.yml`.
  * `detector.py` computes per-host EWMA packet-rate Z-scores and triggers `controller.py` to install high-priority drop rules within `< 1 ms`, logging all events to `detections.csv`.

---

## Repository Structure

    SDN-Telemetry-and-Anomoly-Detection/
    ├── controller.py             # OS-Ken OpenFlow 1.3 L2 switch, stats polling & automated mitigation
    ├── detector.py               # EWMA Z-score anomaly detection engine
    ├── telemetry.py              # Prometheus HTTP metrics exporter
    ├── prometheus.yml            # Prometheus scrape configuration
    ├── topology.py               # Mininet 7-switch, 8-host binary tree topology
    ├── grafana-dashboard.json    # Exported 3-panel Grafana dashboard (RX packets, RX bits, Alarms)
    ├── detections.csv            # Logged anomaly detection and block timestamps/metrics
    ├── scripts/
    │   └── baseline.sh           # Baseline traffic generator helper script
    ├── captures/                 # Architecture diagram & Wireshark/OpenFlow verification captures
    │   ├── ArchitectureDiagram.jpg
    │   └── screenshots/          # Protocol captures (ARP/ICMP, TCP/HTTP, UDP, SYN/UDP flood, OpenFlow)
    ├── results/
    │   └── polling_overhead.csv  # Raw CPU % and stats message rate benchmarking data
    └── README.md

---

## Prerequisites

* **OS:** Ubuntu 22.04 LTS
* **Python:** Python 3.10+ with `venv`
* **System Packages:**

      sudo apt update
      sudo apt install -y mininet openvswitch-switch iperf3 curl python3-venv prometheus

* **Grafana:** Installed and running on `http://localhost:3000`:

      sudo systemctl enable --now grafana-server

---

## Step-by-Step Setup & Execution Guide

### 1. Clone the Repository & Create the Python Virtual Environment

    git clone [https://github.com/ayraomar/SDN-Telemetry-and-Anomoly-Detection.git](https://github.com/ayraomar/SDN-Telemetry-and-Anomoly-Detection.git)
    cd SDN-Telemetry-and-Anomoly-Detection

    python3 -m venv ryu-env
    source ryu-env/bin/activate
    pip install os-ken prometheus-client

### 2. Start Prometheus (Terminal 1)

    cd ~/SDN-Telemetry-and-Anomoly-Detection
    prometheus --config.file=prometheus.yml

* **Verify:** Open `http://localhost:9090/targets` in your browser and confirm the SDN telemetry endpoint state is **UP**.

### 3. Start the OS-Ken SDN Controller (Terminal 2)

    cd ~/SDN-Telemetry-and-Anomoly-Detection
    source ryu-env/bin/activate
    osken-manager controller.py

* **Verify:** The controller starts listening on `127.0.0.1:6653` and registers datapaths `0000000000000001` through `0000000000000007` once Mininet launches.

### 4. Start the Mininet Topology (Terminal 3)

    cd ~/SDN-Telemetry-and-Anomoly-Detection
    sudo mn -c
    sudo python3 topology.py

* **Verify:** All 7 switches connect in Terminal 2 (`Register datapath: 0000000000000001` ... `0000000000000007`) and `pingall` succeeds at the `mininet>` prompt.

### 5. Set Up the Grafana Dashboard
1. Open `http://localhost:3000` in Firefox (default credentials: `admin` / `admin`).
2. Go to **Connections -> Data sources -> Add data source**, choose **Prometheus**, set URL to `http://localhost:9090`, and click **Save & test**.
3. Either import `grafana-dashboard.json` (**Dashboards -> New -> Import**) or create a dashboard with three Time Series panels:
   * **Port RX packets:** `port_rx_pps{dpid=~"4|5|6|7"}`
   * **Port RX bits:** `port_rx_bps`
   * **Alarms:** `anomaly_alarms_total`
4. Set the dashboard time range to **Last 5 minutes** and auto-refresh to **5s**.

---

## Running the Baseline & Attack Mitigation Demo

### Step A: Generate Normal Baseline Traffic (`h1`-`h5`)
At the `mininet>` prompt, start background HTTP servers/clients and an `iperf3` TCP stream:

    h1 python3 -m http.server 80 >/dev/null 2>&1 &
    h2 iperf3 -s >/dev/null 2>&1 &
    h3 python3 -c "import time, urllib.request; exec('while True:
 try: urllib.request.urlopen("[http://10.0.0.1](http://10.0.0.1)", timeout=2).read()
 except: pass
 time.sleep(0.5)')" >/dev/null 2>&1 &
    h4 iperf3 -c 10.0.0.2 -t 600 -b 5M >/dev/null 2>&1 &
    h5 python3 -c "import time, urllib.request; exec('while True:
 try: urllib.request.urlopen("[http://10.0.0.1](http://10.0.0.1)", timeout=2).read()
 except: pass
 time.sleep(1)')" >/dev/null 2>&1 &

* **Verify:** Grafana shows steady baseline packet and bit rates across the edge switch ports.

### Step B: Launch a Volumetric UDP Flood Attack (`h6` -> `h2`)
With baseline traffic active, launch a 100 Mbps UDP flood from `h6` (`10.0.0.6`) toward `h2` (`10.0.0.2`) at the `mininet>` prompt:

    h6 iperf3 -c 10.0.0.2 -u -b 100M -t 45 >/dev/null 2>&1 &

* **Verify:**
  1. **Traffic Spike:** `Port RX packets` surges to `~8,500+ pps` and `Port RX bits` exceeds `100 Mbps` in Grafana.
  2. **EWMA Detection:** Terminal 2 prints `ALARM h6 pps=... z=... -> blocked` and `{host="h6"}` increments in Grafana's **Alarms** panel.
  3. **Automated Mitigation:** An OpenFlow drop flow rule is installed within `< 1 ms`, immediately returning switch traffic back to baseline levels.

### Step C: Inspect Logs & Clean Up
Exit Mininet (`exit`), stop `osken-manager` and `prometheus` (`Ctrl + C`), and inspect `detections.csv`:

    cat detections.csv
    sudo mn -c

---

## Sample Detection Results (`detections.csv`)

| Host | Event | Epoch Timestamp | Packet Rate (`pps`) | EWMA Z-Score | Mitigation Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `h6` (Attacker) | `detected` -> `blocked` | `1795334143.141` | `8,543` | `1344.4` | `< 1 ms` |
