from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class SDNTopology(Topo):
    def build(self):
        # Create 7 OpenFlow Switches (s1 to s7)
        switches = [self.addSwitch(f's{i}', cls=OVSKernelSwitch, protocols='OpenFlow13') for i in range(1, 8)]

        # Create Hosts (h1 to h4)
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')

        # Link Hosts to Switches
        self.addLink(h1, switches[0]) # h1 -> s1
        self.addLink(h2, switches[0]) # h2 -> s1
        self.addLink(h3, switches[6]) # h3 -> s7
        self.addLink(h4, switches[6]) # h4 -> s7

        # Connect Switches together (s1 through s7)
        for i in range(6):
            self.addLink(switches[i], switches[i+1])

def run():
    topo = SDNTopology()
    # Connect to local controller listening on default OpenFlow port 6653/6633
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6653), switch=OVSKernelSwitch)
    net.start()
    info("*** Network is running. Entering Mininet CLI ***\n")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
