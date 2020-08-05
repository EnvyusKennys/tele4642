from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4

k = 4


class FatBoy(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FatBoy, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        ip = pkt.get_protocols(ipv4.ipv4)

        eth = pkt.get_protocol(ethernet.ethernet)

        mac_dst = eth.dst
        mac_src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, mac_src, mac_dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][mac_src] = in_port
        pod = int(ip.dst[4])
        switch_no = int(ip.dst[6])
        host_no = int(ip.dst[8])
        switch_pod = int(dpid[11])
        switch_no_dpid = int(dpid[13])

        if mac_dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][mac_dst]
        else:
            if switch_pod == k:  # determine if it is core switch
                out_port = pod
            else:
                if switch_no_dpid == 2 or switch_no_dpid == 3:  # determine if it is aggregation switch
                    if switch_pod == pod:  # host in same pod
                        out_port = switch_no
                    else:  # host in different pod
                        out_port = ((host_no - 2 + switch_no_dpid) % (k / 2)) + (k / 2)
                else:  # it is edge switch
                    if switch_pod == pod:  # host in same pod
                        if switch_no == switch_no_dpid:  # host under same switch
                            out_port = switch_no
                        else:  # host under different switch
                            out_port = ((host_no - 2 + switch_no_dpid + (k / 2)) % (k / 2)) + (k / 2)
                    else:  # host in different pod
                        out_port = ((host_no - 2 + switch_no_dpid + (k / 2)) % (k / 2)) + (k / 2)

        actions = [parser.OFPActionOutput(out_port)]
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=mac_dst, eth_src=mac_src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)


        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

