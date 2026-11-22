import time
from prometheus_client import Gauge, Counter, start_http_server
from detector import EWMADetector

EDGE = (4, 5, 6, 7)  # edge switch dpids; host ports are 2 and 3

def host_of(dpid, port):  # s4p2->h1, s4p3->h2, s5p2->h3 ...
    return f"h{(dpid - 4) * 2 + (port - 1)}"

class Telemetry:
    def __init__(self, app, port=8000):
        self.app = app
        self.rx_pps = Gauge("port_rx_pps", "RX packets/s", ["dpid", "port"])
        self.rx_bps = Gauge("port_rx_bps", "RX bits/s", ["dpid", "port"])
        self.alarms = Counter("anomaly_alarms_total", "Alarms", ["host"])
        self.prev, self.det, self.blocked = {}, {}, set()
        self.log = open("detections.csv", "a")
        start_http_server(port)  # Prometheus scrapes :8000

    def on_port_stats(self, dpid, body):
        now = time.time()
        for s in body:
            if s.port_no > 0xffffff00:  # skip the OVS local port
                continue
            key = (dpid, s.port_no)
            if key in self.prev:
                t0, p0, b0 = self.prev[key]
                dt = now - t0  # real elapsed time, not nominal interval
                if dt > 0:
                    pps = (s.rx_packets - p0) / dt
                    bps = (s.rx_bytes - b0) * 8 / dt
                    self.rx_pps.labels(str(dpid), str(s.port_no)).set(pps)
                    self.rx_bps.labels(str(dpid), str(s.port_no)).set(bps)
                    if dpid in EDGE and s.port_no in (2, 3):
                        self._check(dpid, s.port_no, pps, now)
            self.prev[key] = (now, s.rx_packets, s.rx_bytes)

    def _check(self, dpid, port, pps, now):
        host = host_of(dpid, port)
        if host in self.blocked:
            return
        det = self.det.setdefault(host, EWMADetector())
        z, alarm = det.update(pps)
        if alarm:
            self.alarms.labels(host).inc()
            self.log.write(f"{host},detected,{now:.3f},{pps:.0f},{z:.1f}\n")
            self.app.block_port(dpid, port)
            self.log.write(f"{host},blocked,{time.time():.3f},,\n")
            self.log.flush()
            self.blocked.add(host)
            self.app.logger.warning("ALARM %s pps=%.0f z=%.1f -> blocked", host, pps, z)
