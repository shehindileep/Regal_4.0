"""This classess are used to collect the diameter message stats """
#!/bin/python

import signal
import sys
import time

from stats_utility import Utility, ClientStatsSender

IS_PY2 = sys.version_info < (3, 0)

COLLECTION_NAME = "DIAMessageStatResult"
DURATION_KEY = "DiamsgStatDuration"
PROTOCOL = "DIA"
SCRIPT_NAME = "diamsgstats"


DATE = "date +%s"
SNMP_CMD = "snmpwalk -v 2c -c rwnni -M /opt/titan/sys/mibs:/usr/share/snmp/mibs -m ALL localhost"
ACTIVE_TRANS_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkPerformanceActiveTransactions"
ANS_2XXX_REC_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsClientSuccess"
ANS_3XXX_REC_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsClientProtocolErrors"
ANS_4XXX_REC_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsClientTransientFailures"
ANS_5XXX_REC_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsClientPermanentFailures"
ANS_2XXX_SENT_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsServerSuccess"
ANS_3XXX_SENT_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsServerProtocolErrors"
ANS_4XXX_SENT_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsServerTransientFailures"
ANS_5XXX_SENT_OID = "TITAN-Diameter-NG-MIB::titanDiameterNgNetworkStatisticsServerPermanentFailures"
ACTIVE_TRANS_PARSER = "awk '{print $4}'"
ANS_PARSER = "awk -F ' ' '{s+=$4}END{print s}'"


def get_stats_info():
    """ This method returns the collection name and fields which are used in
    this stats.

    Return:
        dict: key=collections name,
              val=Fileds the

    """
    fields = ["Active_transcation", "2xxx_ans_received", "3xxx_ans_received",
             "4xxx_ans_received", "5xxx_ans_received", "2xxx_ans_sent", "3xxx_ans_sent",
             "4xxx_ans_sent", "5xxx_ans_sent", "SENT_TPS"]
    stats_info_dict = {COLLECTION_NAME: fields}
    return stats_info_dict


class DIAMessageStatistics(object):
    """Class is defined to get the Diameter message statistics information."""

    def __init__(self, client):
        """The Initilazition of this class create object of the Utility class.

        Args:
            self (instance): it refers to the variables and methods of the same
            class.

        """
        self._client_obj = client
        self._start_time = None
        self._active_trans = None
        self._2xxx_ans_rec = None
        self._3xxx_ans_rec = None
        self._4xxx_ans_rec = None
        self._5xxx_ans_rec = None
        self._2xxx_ans_sent = None
        self._3xxx_ans_sent = None
        self._4xxx_ans_sent = None
        self._5xxx_ans_sent = None
        self._sent_2xxx_ans_prev_msg = 0
        self._sent_2xxx_ans_prev_timestamp = 0
        self._end_time = None

    def execute_diamsgstats(self):
        """This method execute all diameter message stats commands.
        Taking avg of start and end time because execution of all commmands
        takig nearly one second .

        Args:
            self (instance): it refers to the variables and methods of the same
            class.

        Returns:
            None: Nothing is returned

        """
        self._start_time = Utility.command_executer("{}".format(DATE))
        self._active_trans = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ACTIVE_TRANS_OID, ACTIVE_TRANS_PARSER))
        self._2xxx_ans_rec = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_2XXX_REC_OID, ANS_PARSER))
        self._3xxx_ans_rec = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_3XXX_REC_OID, ANS_PARSER))
        self._4xxx_ans_rec = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_4XXX_REC_OID, ANS_PARSER))
        self._5xxx_ans_rec = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_5XXX_REC_OID, ANS_PARSER))
        self._2xxx_ans_sent = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_2XXX_SENT_OID, ANS_PARSER))
        self._3xxx_ans_sent = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_3XXX_SENT_OID, ANS_PARSER))
        self._4xxx_ans_sent = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_4XXX_SENT_OID, ANS_PARSER))
        self._5xxx_ans_sent = Utility.command_executer("{} {} | {}".format(
            SNMP_CMD, ANS_5XXX_SENT_OID, ANS_PARSER))
        self._end_time = Utility.command_executer("{}".format(DATE))

    def get_time_stamp(self):
        """This method returns date and time.

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int: date and time

        """
        try:
            return (int(self._start_time)+int(self._end_time))/2
        except ValueError:
            return -1

    def get_active_transcation(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._active_trans)
        except ValueError:
            return -1

    def get_2xxx_answer_recevied(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._2xxx_ans_rec)
        except ValueError:
            return -1

    def get_3xxx_answer_recevied(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._3xxx_ans_rec)
        except ValueError:
            return -1

    def get_4xxx_answer_recevied(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._4xxx_ans_rec)
        except ValueError:
            return -1

    def get_5xxx_answer_recevied(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._5xxx_ans_rec)
        except ValueError:
            return -1

    def get_2xxx_answer_sent(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._2xxx_ans_sent)
        except ValueError:
            return -1

    def get_3xxx_answer_sent(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._3xxx_ans_sent)
        except ValueError:
            return -1

    def get_4xxx_answer_sent(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._4xxx_ans_sent)
        except ValueError:
            return -1

    def get_5xxx_answer_sent(self):
        """This method returns .

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            int:

        """
        try:
            return int(self._5xxx_ans_sent)
        except ValueError:
            return -1

    def get_2xxx_answer_sent_tps(self):
        """ This method returns the tps of the 2xxx answer sent

        Returns:
            str: Tps of the 2xx answer sent.

        """
        interval_msg_count = self.get_2xxx_answer_sent() - self._sent_2xxx_ans_prev_msg
        interval_duration = self.get_time_stamp() - self._sent_2xxx_ans_prev_timestamp
        self._sent_2xxx_ans_prev_timestamp = self.get_time_stamp()
        self._sent_2xxx_ans_prev_msg = self.get_2xxx_answer_sent()
        if not interval_duration:
            return 0
        tps = interval_msg_count/interval_duration
        return round(float(tps), 2)


    def send_diamsg_stats(self):
        """This method sends the dia message stats information to pushgateway
        and stats collector.

        Args:
            self (instance): it refers to the variables and methods of the
            same class.

        Returns:
            None: Nothing is returned.
        """
        #Note: Field name should be in [a-zA-Z_:][a-zA-Z0-9_:]* regex pattern
        #Examples: 
        #1. Field which contains with bracket not supported --> "cpu(%)": self.get_cpu()
        #2. Field which starts with number not supported --> 5xxx_ans_sent":  10

        dia_stat = {"timeStamp": self.get_time_stamp(),
            "Active_transcation": self.get_active_transcation(),
            "_2xxx_ans_received": self.get_2xxx_answer_recevied(),
            "_3xxx_ans_received": self.get_3xxx_answer_recevied(),
            "_4xxx_ans_received": self.get_4xxx_answer_recevied(),
            "_5xxx_ans_received": self.get_5xxx_answer_recevied(),
            "_2xxx_ans_sent": self.get_2xxx_answer_sent(),
            "_3xxx_ans_sent": self.get_3xxx_answer_sent(),
            "_4xxx_ans_sent": self.get_4xxx_answer_sent(),
            "_5xxx_ans_sent": self.get_5xxx_answer_sent(),
            "SENT_TPS": self.get_2xxx_answer_sent_tps(),
            "collectionName": COLLECTION_NAME,
            "otherInfo": {"ScriptName": SCRIPT_NAME, "Protocol": PROTOCOL}
            }
        self._client_obj.send_stats_to_server(dia_stat)
        
if __name__ == "__main__":
    DONE = True
    DURATION = Utility.get_duration(DURATION_KEY)
    STAT_OBJ = ClientStatsSender()
    DIAMSG_OBJ = DIAMessageStatistics(STAT_OBJ)

    def sigint_handler(signum, frame):
        """ This method catch the signal and perform respective action.
        """
        global DONE
        DONE = False

    signal.signal(signal.SIGINT, sigint_handler)

    while DONE:
        START_TIME = time.time()
        DIAMSG_OBJ.execute_diamsgstats()
        END_TIME = time.time()
        DIAMSG_OBJ.send_diamsg_stats()
        time.sleep(DURATION-(END_TIME-START_TIME))
