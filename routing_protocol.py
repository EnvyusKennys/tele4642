# tele4642 lab2 fattree routing protocol
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.lib.packet import ethernet, arp, ipv4
from ryu.topology import event
from ryu.topology.api import get_switch, get_link


class ryu(app_manager.Ryuapp):
    def __init__(self):
        super().__init__()
    def add_ip(self):
        pass
    
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        

