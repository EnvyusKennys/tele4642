from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.node import Node
from mininet.cli import CLI

import sys

num = int(sys.argv[1])


class FatTopo(Topo):
    def __init__(self, k, **opts):
        super(FatTopo, self).__init__(**opts)
        Hs = []
        Ss = []
        # generate the core switch and assign the dpid
        info('*** Add switches\n')
        switch = self.addSwitch('Switch', dpid='0000000000000001')
        print('Switch added: dpid = 0000000000000001')

        # generate the servers
        info('*** Add servers\n')
        for i in range(1, 4):
            Ss.append(self.addHost('s%s' % i, mac='00:00:00:00:00:0%s' % i))
            print('Server s%s added' % i)

        # generate the hosts
        info('*** Add hosts\n')
        for i in range(1, k + 1):
            Hs.append(self.addHost('h%s' % i, mac='00:00:00:00:00:0%s' % (i + 3)))
            print('Host h%s added' % i)

        # connect the host with switch
        for i in range(1, k + 1):
            self.addLink(switch, Hs[i - 1])

        # connect the servers with switch
        for i in range(1, 4):
            self.addLink(switch, Ss[i - 1])


# run the mininet test
def simpleTest():
    topo = FatTopo(k=num)
    net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=False, autoStaticArp=True)
    net.addController('controller', controller=RemoteController, ip="127.0.0.1", port=6633, protocols="OpenFlow13")
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    simpleTest()
