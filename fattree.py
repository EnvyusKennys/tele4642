# tele4642 lab2 fat-tree topology for mininet

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel

# net = Mininet(topo, link = TCLink, controller=None, autoSetMacs=True, autoStaticArp = True)
# net.addController('controller', controller=RemoteController, ip = "127.0.0.1", port = 6633, protocols="OpenFlow13")


class fattree(Topo):
    Core = []
    Aggr = []
    Edge = []
    Host = []

    def __init__(self, k):
        self.pod = k
        self.CoreSwitch = (k/2)**2
        self.AggrSwitch = k*k/2
        self.EdgeSwitch = k*k/2
        Topo.__init__(self)

    def createTopo(self):
        self.generateCoreSwitch()
        self.generateAggrSwitch()
        self.generateEdgeSwitch()
        self.generateHost()

    # Switch and Host
    # func to create the switch
    def createSwitch(self, i, list):
        list.append(self.addSwitch())  # mininet.topo.Topo.addSwitch

    def generateCoreSwitch(self, i):
        self.createSwitch(i)

    def generateAggrSwitch(self, i):
        self.createSwitch(i)

    def generateHost(self, i):
        self.Hostlist.append(self.addHost())

    # Link
    def createLink(self):
        self.addLink()
