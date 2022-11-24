"""
Total 4-servers [UPF, SMF, DN and gNodeB]
Testcase is to validate the pcap file captured in SMF, DN and GNB node which is successfully generating the connection.
Steps:
    1. Start UPF node.
    2. Capture packets in all the 3 nodes(SMF, DN and gNodeB)
    3. Start the SMF simulator
    4. SMF simulator will send 2 packets towards UPF and UPF inturn will process and create some entries.
    5. UPF responds back towards SMF with the successful cause.
    6. SMF and UPF will continue to exchange heartbeat messages at a periodic interval.
    8. Start the gNodeB simulator.
    9. gNodeB simulator will send a packet towards UPF.
   10. UPF will process it and send it towards DN.
   11. DN simulator recieve the packet from and DN will send a packet towards UPF. 
   12. UPF will process the packet and send it towards gNodeB.
   13. Stop capturing packets SMF, DN and gNodeB nodes.
   14. Stop SMF, DN and gNodeB simulator.
   15. Copy pcap file from SMF, DN and gNodeB. 
   16. Validate pcap traces between UPF and SMF, DN and gNodeB nodes.
"""

import time
import traceback

import regal_lib.corelib.custom_exception as exception
from Telaverge.helper.upf_helper import UPFHelper
from Telaverge.telaverge_constans import UPFConstants
from test_executor.test_executor.utility import GetRegal

class TestCaseConstants:
    SLEEP_TIME = 5

class UPFTest():
    """
    Initialize all the required parameter to start the test case.
        1. Create the upf node object.
        2. Create smf node object.
        3. Create the dn node object.
        4. Create the gnb node object.
    """

    def __init__(self):
        # test executor service libraries
        self.regal_api = GetRegal()
        log_mgr_obj = self.regal_api.get_log_mgr_obj()
        self._log = log_mgr_obj.get_logger(self.__class__.__name__)
        self._log.debug(">")
        self.upf_helper_obj = UPFHelper(self.regal_api, UPFConstants.UPF_NODE_NAME, UPFConstants.UPF_APP)
        self.smf_helper_obj = UPFHelper(self.regal_api, UPFConstants.SMF_NODE_NAME, UPFConstants.SMF_APP)
        self.dn_helper_obj = UPFHelper(self.regal_api, UPFConstants.DN_NODE_NAME, UPFConstants.DN_APP)
        self.gnb_helper_obj = UPFHelper(self.regal_api, UPFConstants.GNB_NODE_NAME, UPFConstants.GNB_APP)
        self._current_testcase_config = self.regal_api.get_current_test_case_configuration().get_test_case_config()
        self._test_run_duration = int(self._current_testcase_config["TestRunDuration"])
        self._log.debug("<")

    def _start_stats(self):
        """Method used to start the stats

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.upf_helper_obj.start_stats()
        self._log.info("Started stats script on UPF node: '%s'", self.upf_helper_obj.get_management_ip())
        self.smf_helper_obj.start_stats()
        self._log.info("Started stats script on SMF node: '%s'", self.smf_helper_obj.get_management_ip())
        self.dn_helper_obj.start_stats()
        self._log.info("Started stats script on DN node: '%s'", self.dn_helper_obj.get_management_ip())
        self.gnb_helper_obj.start_stats()
        self._log.info("Started stats script on gNodeB node: '%s'", self.gnb_helper_obj.get_management_ip())
        self._log.debug("<")

    def setup_scripts(self):
        """Method used to setup the scripts in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self._log.info("Started configuration of scripts on all nodes")
        self.upf_helper_obj.setup_script()
        self.smf_helper_obj.setup_script()
        self.dn_helper_obj.setup_script()
        self.gnb_helper_obj.setup_script()
        self._log.info("Completed configuration of scripts on all nodes")
        self._log.debug("<")

    def _stop_stats(self):
        """Method used to stop the stats

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.upf_helper_obj.stop_stats()
        self._log.info("Stopped stats script on UPF node: '%s'", self.upf_helper_obj.get_management_ip())
        self.smf_helper_obj.stop_stats()
        self._log.info("Stopped stats script on SMF node: '%s'", self.smf_helper_obj.get_management_ip())
        self.dn_helper_obj.stop_stats()
        self._log.info("Stopped stats script on DN node: '%s'", self.dn_helper_obj.get_management_ip())
        self.gnb_helper_obj.stop_stats()
        self._log.info("Stopped stats script on gNodeB node: '%s'", self.gnb_helper_obj.get_management_ip())
        self._log.debug("<")

    def _apply_configuration(self):
        """Method used to setup the stats

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self._log.info("Apply stats configuration on all nodes is inProgress")
        self.upf_helper_obj.apply_configuration()
        self.smf_helper_obj.apply_configuration()
        self.dn_helper_obj.apply_configuration()
        self.gnb_helper_obj.apply_configuration()
        self._log.info("Successfully applied stats configurations on all nodes")
        self._log.debug("<")

    def _check_stats(self):
        """Method used to check the stats

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.upf_helper_obj.check_stats()
        self.smf_helper_obj.check_stats()
        self.dn_helper_obj.check_stats()
        self.gnb_helper_obj.check_stats()
        self._log.debug("<")

    def manage_script_services(self):
        """Method used to start the service in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.smf_helper_obj.start_services(True)
        self._log.info("Started Capturing tcpdump of PFCP Association and Session Establishment between UPF and SMF nodes.")
        self._log.info("Sending PFCP Association and Session Establishment request towards UPF.")
        self.dn_helper_obj.start_services(True)
        self._log.info("Started capturing tcpdump of uplink and downlink packets on DN node.")
        self._log.info("Started DN simulator.")
        self.gnb_helper_obj.start_services(True)
        self._log.info("Started capturing tcpdump of uplink and downlink packets on gNodeB node.")
        self._log.info("Started gNodeB simulator.")
        self._log.info("gNodeB sent uplink packet towards UPF.")
        self._log.info("Waiting {} seconds for exchange PFCP Association, Session Establishment, uplink and downlink packets to be completed.".format(TestCaseConstants.SLEEP_TIME))
        time.sleep(TestCaseConstants.SLEEP_TIME)
        self._log.info("DN received downlink packet from UPF.")
        self.smf_helper_obj.stop_services(True)
        self._log.info("Stopped capturing PFCP Association and Session Establishment packets on SMF node.")
        self._log.info("Stopped SMF simulator")
        self.dn_helper_obj.stop_services(True)
        self._log.info("Stopped capturing of uplink and downlink packets on DN node.")
        self._log.info("Stopped DN simulator.")
        self.gnb_helper_obj.stop_services(True)
        self._log.info("Stopped capturing of uplink and downlink packets on gNodeB node.")
        self._log.info("Stopped gNodeB simulator.")
        self._log.debug("<")

    def validate_pcap(self):
        """Method used to validate pcap file captured in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self._log.info("Copying pcap files from SMF, DN and gNodeB node and validationg pcap traces.")
        self.smf_helper_obj.validate_pcap()
        self.dn_helper_obj.validate_pcap()
        self.gnb_helper_obj.validate_pcap()
        self._log.info("PFCP Association, Session Establishment, uplink and downlink packets validated successfully.")
        self._log.debug(">")

    def test_run(self):
        """Method used to execute the test run

        Args:
            None

        Returns:
            None
        """
        try:
            self._log.debug(">")
            self._apply_configuration()
            self._start_stats()
            self._check_stats()
            self.setup_scripts()
            self.upf_helper_obj.restart_upf_server()
            self.manage_script_services()
            self.validate_pcap()
            self._stop_stats()
            self._log.debug("<")
        except Exception as ex:
            trace_back = traceback.format_exc()
            self._log.error("Exception caught while running test %s", str(ex))
            self._log.error("Traceback: %s", str(trace_back))
            self._stop_stats()
            tc_name = self.regal_api.get_current_test_case()
            self._log.debug("<")
            raise exception.TestCaseFailed(tc_name, str(ex))


def execute():
    """
    Create testcase instance and execute the test

    Args:
        None

    Returns:
        None
    """
    test = UPFTest()
    test.test_run()
    test = None
