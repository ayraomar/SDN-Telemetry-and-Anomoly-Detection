from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class SDNTreeTopology(Topo):
    def build(self):
        s1 = self.addSwitch("s1", cls=OVSKernelSwitch, protocols="OpenFlow13")
        s2 = self.addSwitch("s2", cls=OVSKernelSwitch, protocols="OpenFlow13")
        s3 = self.addSwitch("s3", cls=OVSKernelSwitch, protocols="OpenFlow13")
        s4 = self.addSwitch("s4", cls=OVSKernelSwitch, protocols="OpenFlow13")
        s5 = self.addSwitch("s5", cls=OVSKernelSwitch, protocols="OpenFlow13")
        s6 = self.addSwitch("s6", cls=OVSKernelSwitch, protocols="OpenFlow13")
        s7 = self.addSwitch("s7", cls=OVSKernelSwitch, protocols="OpenFlow13")

        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s2, s5)
        self.addLink(s3, s6)
        self.addLink(s3, s7)

        edge_switches = [s4, s5, s6, s7]
        for i in range(1, 9):
            host = self.addHost(
                f"h{i}",
                ip=f"10.0.0.{i}/24",
                mac=f"00:00:00:00:00:0{i}"
            )
            edge_sw = edge_switches[(i - 1) // 2]
            self.addLink(host, edge_sw)

def run():
    topo = SDNTreeTopology()
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip="127.0.0.1", port=6653),
        switch=OVSKernelSwitch
    )
    net.start()
    info("*** 7-Switch, 8-Host Tree Topology Running ***\n")
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()
