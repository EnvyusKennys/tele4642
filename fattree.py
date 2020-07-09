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
        self.Host = self.EdgeSwitch * k/2  # each edge switch connects two hosts
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
        for num in range(0, i):
            # mininet.topo.Topo.addSwitch
            list.append(self.addSwitch(level + 'Sw' + str(i)))
            # Unsolved with the label

    def generateCoreSwitch(self, i):
        self.createSwitch(i, 'cr', Core)

    def generateAggrSwitch(self, i):
        self.createSwitch(i, 'ag', Aggr)

    def generateEdgeSwitch(self, i):
        self.createSwitch(i, 'ed', Edge)

    def generateHost(self, i):
        for num in range(0, self.pod):
            for x in range(0, self.pod/2):
                for y in range(2, self.pod/2+1):
                    self.Hostlist.append(self.addHost(
                        '10.' + str(num) + '.' + str(x) + '.' + str(y)))
            # incr between[2,k/2+1]
    # Link

    def createLink(self):
        # Unsolved

        # core to agg
        for i in range(0, self.AggrSwitch, self.pod/2):  # loop through each pod
            for j in range(0, self.pod/2):  # loop through aggr sw in pod
                for k in range(0, self.pod/2):  # loop through core sw correspond to one pod
                    self.addLink(
                        self.Core[k + j * (self.pod/2)], self.Aggr[i + j])

        # agg to edge
        for i in range(0, self.EdgeSwitch, self.pod/2):  # loop through each pod
            for j in range(0, self.pod/2):  # loop through Aggr sw in each pod
                for k in range(0, self.pod/2):  # loop through Edge sw in each pod
                    self.addLink(
                        self.Aggr[i + j], self.Edge[i + k])
        # edge to host


def main(pod, ip='127.0.0.1', port=6633):
    topo = fattree(pod)
    topo.createTopo
    topo.createlink()
    net = Mininet(topo, link=TCLink, controller=None,
                  autoSetMacs=True, autoStaticArp=True)
    net.addController('controller', controller=RemoteController,
                      ip="127.0.0.1", port=6633, protocols="OpenFlow13")
    net.start()

    # openflow13 ???

# DPID for labelling?
