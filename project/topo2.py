from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.node import Node
from mininet.cli import CLI
import os
import sys

num = int(sys.argv[1])


class Topo(Topo):
    Hs = []
    Ss = []
    Cs = []

    def __init__(self, k, **opts):
        super(Topo, self).__init__(**opts)
        # generate the core switch and assign the dpid
        # info('*** Add switches\n')
        # switch = self.addSwitch('Switch', dpid='0000000000000001')
        # print('Switch added: dpid = 0000000000000001')

        # generate the servers
        info('*** Add servers\n')
        for i in range(1, 4):
            self.Ss.append(self.addHost('s%s' %
                                        (i - 1), mac='00:00:00:00:00:0%s' % i))
            print('Server s%s added' % i)

        info('*** Add a ctrl switch\n')
        self.Cs.append(self.addSwitch(
            'ctrlSw0', dpid='0000000000000001'))
        print('Switch added: dpid = 0000000000000001')

        # generate the hosts
        info('*** Add hosts\n')
        for i in range(1, k + 1):
            self.Hs.append(self.addHost('h%s' %
                                        i, mac='00:00:00:00:00:0%s' % (i + 3)))
            print('Host h%s added' % i)

        # connect the host with switch
        for i in range(1, k + 1):
            self.addLink(self.Cs[0], self.Hs[i - 1])

        # connect the servers with switch
        for i in range(1, 4):
            self.addLink(self.Cs[0], self.Ss[i - 1])

    def setOvs(self):
        self.setproto(self.Cs)

    def setproto(self, list):
        for sw in list:
            cmd = "sudo ovs-vsctl set bridge %s protocols=OpenFlow13" % sw
            os.system(cmd)


# run the mininet test
def simpleTest():
    topo = Topo(k=num)
    net = Mininet(topo=topo, link=TCLink, controller=None,
                  autoSetMacs=False, autoStaticArp=True)
    net.addController('controller', controller=RemoteController,
                      ip="127.0.0.1", port=6633, protocols="OpenFlow13")
    net.start()
    topo.setOvs()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    simpleTest()
