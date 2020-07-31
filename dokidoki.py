from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel
from mininet.link import TCLink
from mininet.node import RemoteController, Switch
from mininet.cli import CLI

import sys

num = int(sys.argv[1])


# return the dpid in hex form based on the inout argument
def int2dpid(dpid):
    dpid = hex(dpid)[2:]
    dpid = '0' * (16 - len(dpid)) + dpid
    return dpid


class FatTopo(Topo):
    def __init__(self, k=2, **opts):
        super(FatTopo, self).__init__(**opts)
        Corek = k
        hk = int(k / 2)
        Cs = []
        As = []
        Es = []
        Hs = []

        # generate the core switches and assign the dpid
        for i in irange(1, int(Corek * Corek / 4)):
            row = int((i - 1) / hk)
            col = (i - 1) % hk
            dpid = hk * 10000 + row * 100 + col
            Cs.append(self.addSwitch('crSw%s' % (i - 1), dpid=int2dpid(dpid)))
            print('crSw%s - %s' % ((i - 1), dpid))

        # generate the aggregation switches and assign the dpid
        for i in irange(1, Corek):
            for j in irange(1, int(Corek / 2)):
                pod = (i - 1)
                switch = j + hk - 1
                dpid = pod * 10000 + switch * 100 + 1
                As.append(self.addSwitch('agSw%s%s' % ((i - 1), (j - 1)), dpid=int2dpid(dpid)))
                print('agSw%s%s - %s' % ((i - 1), (j - 1), dpid))

        # generate the edge switches and assign the dpid
        for i in irange(1, Corek):
            for j in irange(1, int(Corek / 2)):
                pod = i - 1
                switch = j - 1
                dpid = pod * 10000 + switch * 100 + 1
                Es.append(self.addSwitch('edSw%s%s' % ((i - 1), (j - 1)), dpid=int2dpid(dpid)))
                print('EgSw%s%s - %s' % ((i - 1), (j - 1), dpid))

        # generate the hosts and assign the ip address
        for i in irange(1, int(Corek * Corek * Corek / 4)):
            Hs.append(self.addHost('h%s' % (i - 1), ip='10.%s.%s.%s/8' % (
            (int((i - 1) / int(Corek * Corek / 4))), int((i - 1) / int(Corek / 2) % int(Corek / 2)),
            2 + (i - 1) % int(Corek / 2))))

        # connect the host with corresponding edge switch
        counter = 0
        for i in irange(1, int(Corek * Corek / 2)):
            connect = 0
            while connect < int(Corek / 2):
                self.addLink(Es[i - 1], Hs[counter], connect, 0)
                counter += 1
                connect += 1

        # connect the aggregation switch with corresponding edge switch
        for i in irange(1, int(Corek * Corek / 2)):
            offset = int((i - 1) / int(Corek / 2)) * int(Corek / 2) - 1
            for j in irange(1, int(Corek / 2)):
                self.addLink(As[i - 1], Es[j + offset], j - 1, (i - 1) % int(Corek / 2) + int(Corek / 2))

        # connect the core switch with corresponding aggregation switch
        for i in irange(1, int(Corek * Corek / 4)):
            offset = int((i - 1) / int(Corek / 2))
            j = 0
            counter = 0
            while j < (Corek * int(Corek / 2)):
                self.addLink(Cs[i - 1], As[j + offset], counter, (i - 1) % int(Corek / 2) + int(Corek / 2))
                j += int(Corek / 2)
                counter += 1


# run the mininet test
def simpleTest():
    topo = FatTopo(k=num)
    net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=True, autoStaticArp=True)
    net.addController('controller', controller=RemoteController, ip="127.0.0.1", port=6633, protocols="OpenFlow13")
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    simpleTest()
