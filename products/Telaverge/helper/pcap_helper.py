"""Pcap helper"""

from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP
from scapy.contrib.pfcp import PFCP
from scapy.contrib.gtp import GTP_U_Header

class PcapHelper:
    def __init__(self, service_store_obj):
        """ """
        self.service_store_obj = service_store_obj
        self.log_mgr_obj = self.service_store_obj.get_log_mgr_obj()
        self._log = self.log_mgr_obj.get_logger(self.__class__.__name__)
        self._log.debug("> ")
        self._log.debug("< ")

    def get_udp_packet_src_dest_ip_list(self, pcap_file_name):
        """ Method read the pcap file and filter for the UDP packets
        and list the source and destination ip of the packets

        Args:
            pcap_file_name(str): File path of the pcap

        Returns:
            List: list of tuples with src and dest ip

        """
        self._log.debug(">")
        self._log.debug("Reading pcap file %s", pcap_file_name)
        message_type = ""
        tcp_packet_src_dest_ip_list = []
        for pkt_data in rdpcap(pcap_file_name):
            if (pkt_data.haslayer(UDP)):
                if (pkt_data.haslayer(IP)):
                    src =  pkt_data[IP].src
                    dest = pkt_data[IP].dst
                    if (pkt_data.haslayer(GTP_U_Header)):
                        message_type = pkt_data[GTP_U_Header].gtp_type
                    tcp_packet_src_dest_ip_list.append([src, dest, message_type])
        self._log.debug("The src dest ip list of udp packets %s",
                str(tcp_packet_src_dest_ip_list))
        self._log.debug("<")
        return tcp_packet_src_dest_ip_list

    def get_src_and_dest_details_of_pfcp_pcap_file(self, file_name):
        """ Method read the pcap file and filter for the UDP packets
        and list the source and destination ip of the packets

        Args:
            file_name(str): File path of the pcap

        Returns:
            List: list of list with cause, src and dest ip

        """
        self._log.debug(">")
        packet_details = []
        pkts = rdpcap(file_name)
        self._log.debug("%s Pcap file packets%s", file_name, pkts)
        for pkt in pkts:
            if (pkt.haslayer(UDP)):
                if (pkt.haslayer(IP)):
                    if pkt.haslayer("PFCP Association Setup Request"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst])

                    if pkt.haslayer("PFCP Association Setup Response"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst, pkt["IE Cause"].cause])

                    if pkt.haslayer("PFCP Session Establishment Request"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst])    

                    if pkt.haslayer("PFCP Session Establishment Response"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst, pkt["IE Cause"].cause])

                    if pkt.haslayer("PFCP Session Modification Request"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst])

                    if pkt.haslayer("PFCP Session Modification Response"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst, pkt["IE Cause"].cause])
                    
                    if pkt.haslayer("PFCP Session Deletion Request"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst])    

                    if pkt.haslayer("PFCP Session Deletion Response"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst, pkt["IE Cause"].cause])

        self._log.debug("< ")
        return packet_details

    def get_src_and_dest_details_of_pfd_pcap_file(self, file_name):
        """ Method read the pcap file and filter for the UDP packets
        and list the source and destination ip of the packets

        Args:
            file_name(str): File path of the pcap

        Returns:
            List: list of list with cause, src and dest ip

        """
        self._log.debug(">")
        packet_details = []
        pkts = rdpcap(file_name)
        for pkt in pkts:
            if (pkt.haslayer(UDP)):
                if (pkt.haslayer(IP)):
                    if pkt.haslayer("PFCP PFD Management Request"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst])    

                    if pkt.haslayer("PFCP PFD Management Response"):
                        packet_details.append([pkt[IP].src, pkt[IP].dst, pkt["IE Cause"].cause])

        self._log.debug("< ")
        return packet_details