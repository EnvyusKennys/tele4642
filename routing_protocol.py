# tele4642 lab2 fattree routing protocol
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.topology import event
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls


class ryu(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self):
        super(ryu, self).__init__(*args, **kwargs)

    def add_ip(self, datapath, ip, port, priority):
        match = datapath.ofproto_parser.OFPMatch(ipv4_dst=ip, eth_type=0x0800)
        actions = [datapath.ofproto_parser.OFPActionOutput(port)]
        self.add_flow(datapath, match, actions, priority)

    def add_flow(self, datapath, match, actions, priority):
        inst = [datapath.ofproto_parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS,
                                                              actions)]
        mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, priority=priority,
                                                 match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        k = 4

        match = datapath.ofproto_parser.OFPMatch()
        actions = datapath.ofproto_parser.OFPActionOutput(
            datapath.ofproto.OFPP_CONTROLLER, datapath.ofproto.OFPCML_NO_BUFFER)
        self.add_flow(datapath, match, actions, priority=0)

        dpid = str(datapath.id)

        if dpid[0:2] == 'cr':    # need to be fixed, for core sw
            for i in range(k):
                port = 1 + i
                ip = ('10.' + str(i) + '.0.0', '255.255.255.0')
                self.add_ip(datapath, ip, port, priority=1)

        elif dpid[0:2] == 'ag':  # for aggr sw
            n = int(dpid[4:5])           # pod
            j = int(dpid[5:6]) + k / 2   # switch
            for i in range(k / 2):
                # unfixed for suffix port
                port = 1 + (((i - 2 + j) % (k / 2)) + k / 2)
                ip = ('0.0.0.' + str(i + 2), '0.0.0.255')
                self.add_ip(datapath, ip, port, priority=1)
            for i in range(k / 2):
                port = 1 + i
                ip = ('10.' + str(n) + '.' + str(i) + '.0', '255.255.255.0')
                self.add_ip(datapath, ip, port, priority=10)
        elif dpid[0:2] == 'ed':
            n = int(dpid[4:5])
            j = int(dpid[5:6])
            for i in range(k / 2):
                port = 1 + (((i - 2 + j) % (k / 2)) + k / 2)
                ip = ('0.0.0.' + str(i + 2), '0.0.0.255')
                self.add_ip(datapath, ip, port, priority=1)
            for i in range(k / 2):
                port = 1 + i
                ip = ('10.' + str(n) + '.' + str(j) +
                      '.' + str(i + 2), '255.255.255.0')
                self.add_ip(datapath, ip, port, priority=10)
