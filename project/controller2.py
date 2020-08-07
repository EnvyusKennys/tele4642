# tele4642 mini project


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import time


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.src_mac = []
        self.dst_mac = []
        self.flag = [0, 0, 0, 0, 0, 0, 0]
        self.curr_time = 0

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_tableflow(datapath, 0, match, actions)

    def add_tableflow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)
        # curr_time.append(time.time())

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, idle_timeout=10)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, idle_timeout=10)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)

        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        self.firewall(src, dst, datapath, msg.buffer_id, out_port)
        actions = [parser.OFPActionOutput(out_port)]
        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
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

    def firewall(self, src, dst, dp, buffer_id, port):
        parser = dp.ofproto_parser
        x = 0
        i = int(dst[-1:]) - 1
        print(i)
        if len(self.src_mac) == 0 and len(self.dst_mac) == 0:
            self.src_mac.append(src)
            self.dst_mac.append(dst)
        else:
            if src == self.dst_mac[0] and dst == self.src_mac[0]:
                # handshake
                self.flag[i] = 1
                x = 1
                self.curr_time = time.time()
                self.dst_mac[0] = dst
                self.src_mac[0] = src

            else:
                self.src_mac.remove(self.src_mac[0])
                self.dst_mac.remove(self.dst_mac[0])
                if (time.time() < self.curr_time + 30) and self.flag[i] == 1:
                    match = parser.OFPMatch(eth_dst=dst, eth_src=src)
                    self.add_flow(dp, priority=1, match=match,
                                  actions=[], buffer_id=buffer_id)
                    time.sleep(15)
                else:
                    self.flag[i] = 0
                    self.curr_time = 0

        if self.flag[i] == 1 and x == 1:
            actions = [parser.OFPActionOutput(port)]
            match = parser.OFPMatch(eth_dst=dst, eth_src=src)
            self.add_flow(dp, priority=1, match=match,
                          actions=actions, buffer_id=buffer_id)

       #     else:
            #         for i in range(0, len(self.src_mac)):
            #             for j in range(0, len(self.src_mac)):
            #                 if src == dst_mac[j] and dst == src_mac[i] and i == j:
            #                     self.flag = 0
            #                     # flag goes to zero, ping between host and server is complete
            #                     self.src_mac.remove(src[i])
            #                     self.dst_mac.remove(dst[j])
            #                 elif dst == dst[j] and src != src_mac[i] and i == j:
            #                     actions = self.parser.OFPMatch()
            #                     # actions = drop
            #                 else:
            #                     self.src_mac.append(src)
            #                     self.dst_mac.append(dst)
            #                     # append, add flow
