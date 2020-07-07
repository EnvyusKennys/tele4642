# tele4642 lab2 fat-tree topology for mininet

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

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
        self.Host = self.EdgeSwitch * 2  # each edge switch connects two hosts
        Topo.__init__(self)

    def createTopo(self):
        self.generateCoreSwitch(self.CoreSwitch)
        self.generateAggrSwitch(self.AggrSwitch)
        self.generateEdgeSwitch(self.EdgeSwitch)
        self.generateHost(self.Host)

    # Switch and Host
    # func to create the switch
    # i = num of switches, level = which level the switch belongs
    def createSwitch(self, i, level, list):
        list.append(self.addSwitch())  # mininet.topo.Topo.addSwitch
        # Unsolved

    def generateCoreSwitch(self, i):
        self.createSwitch(i, 1, Core)

    def generateAggrSwitch(self, i):
        self.createSwitch(i, 2, Aggr)

    def generateEdgeSwitch(self, i):
        self.createSwitch(i, 3, Edge)

    def generateHost(self, i):
        self.Hostlist.append(self.addHost())
        # Unsolved
    # Link

    def createLink(self):
        self.addLink()
        # Unsolved


def main(pod, ip='127.0.0.1', port=6633):
    topo = fattree(pod)
    topo.createTopo
    topo.createlink()
    net = Mininet(topo, link=TCLink, controller=None,
                  autoSetMacs=True, autoStaticArp=True)
    net.addController('controller', controller=RemoteController,
                      ip="127.0.0.1", port=6633, protocols="OpenFlow13")
    net.start()
