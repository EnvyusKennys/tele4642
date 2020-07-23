# tele4642 lab2 fattree routing protocol
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.lib.packet import ethernet, arp, ipv4
from ryu.topology import event
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet


class ryu(app_manager.Ryuapp):
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

        dpid = datapath.id
