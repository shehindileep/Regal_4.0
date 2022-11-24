"""
Total 8-servers [ULCL, PSA1, PSA2, SMF, I_SMF, DN, LOCAL-DN and gNodeB]
Testcase is to validate the pcap file captured in SMF, I_SMF, DN, LOCAL-DN and gNodeB node which is successfully generating the connection.
Steps:
    1. Start ULCL and PSA2 nodes.
    2. Capture packets in I-SMF, LOCAL-DN and gNodeB nodes.
    4. Start the I-SMF simulator
    5. I-SMF simulator will send 2 packets towards ULCL and ULCL inturn will process and create some entries.
    6. ULCL responds back towards I-SMF with the successful cause.
    7. I-SMF and ULCL will continue to exchange heartbeat messages at a periodic interval.
    8. I-SMF simulator will send 3 packets towards PSA2 and PSA2 inturn will process and create some entries.
    9. PSA2 responds back towards SMF with the successful cause.
   10. I-SMF and PSA2 will continue to exchange heartbeat messages at a periodic interval.
   11. Start the LOCAL-DN simulator.
   12. Start the gNodeB simulator.
   13. gNodeB simulator will send a packet towards ULCL.
   14. ULCL will process it and send it towards PSA2.
   15. PSA1 will process it and send it towards LOCAL-DN.
   16. LOCAL-DN simulator receive the packet and inturn LOCAL-DN will send a packet towards PSA2.
   17. PSA2 will process it and send it towards ULCL.
   18. ULCL simulator will send a packet towards gNodeB.
   19. Stop capturing packets in I-SMF, LOCAL-DN and gNodeB nodes.
   20. Stop I-SMF, LOCAL-DN and gNodeB simulators.
   21. Copy pcap file from I-SMF, LOCAL-DN and gNodeB nodes.
   22. Validate pcap traces between ULCL, PSA2, I-SMF, LOCAL-DN and gNodeB nodes.
"""

import time
import traceback

import regal_lib.corelib.custom_exception as exception
from Telaverge.helper.upf_helper import UPFHelper
from Telaverge.telaverge_constans import UPFConstants
from test_executor.test_executor.utility import GetRegal

class TestCaseConstants:
    SLEEP_TIME = 10
    SLEEP_TIME_FOR_LOCAL_DN = 5

class UPFTest():
    """
    Initialize all the required parameter to start the test case.
        1. Create the ul_cl node object.
        2. Create smf psa1 object.
        3. Create the psa2 node object.
        4. Create the i_smf node object.
        5. Create the smf node object.
        6. Create the local_dn node object.
        7. Create the gnb node object.
    """

    def __init__(self):
        # test executor service libraries
        self.regal_api = GetRegal()
        log_mgr_obj = self.regal_api.get_log_mgr_obj()
        self._log = log_mgr_obj.get_logger(self.__class__.__name__)
        self._log.debug(">")
        self.ul_cl_helper_obj = UPFHelper(self.regal_api, UPFConstants.ULCL_NODE_NAME, UPFConstants.UPF_APP)
        self.smf_helper_obj = UPFHelper(self.regal_api, UPFConstants.SMF_NODE_NAME, UPFConstants.SMF_APP)
        self.i_smf_helper_obj = UPFHelper(self.regal_api, UPFConstants.I_SMF_NODE_NAME, UPFConstants.SMF_APP)
        self.psa1_helper_obj = UPFHelper(self.regal_api, UPFConstants.PSA1_NODE_NAME, UPFConstants.UPF_APP)
        self.psa2_helper_obj = UPFHelper(self.regal_api, UPFConstants.PSA2_NODE_NAME, UPFConstants.UPF_APP)
        self.dn_helper_obj = UPFHelper(self.regal_api, UPFConstants.DN_NODE_NAME, UPFConstants.DN_APP)
        self.gnb_helper_obj = UPFHelper(self.regal_api, UPFConstants.GNB_NODE_NAME, UPFConstants.GNB_APP)
        self.local_dn_helper_obj = UPFHelper(self.regal_api, UPFConstants.LOCAL_DN_NODE_NAME, UPFConstants.DN_APP)
        self._current_testcase_config = self.regal_api.get_current_test_case_configuration().get_test_case_config()
        self._test_run_duration = int(self._current_testcase_config["TestRunDuration"])
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
        self.ul_cl_helper_obj.apply_configuration()
        self.psa1_helper_obj.apply_configuration()
        self.psa2_helper_obj.apply_configuration()
        self.smf_helper_obj.apply_configuration()
        self.i_smf_helper_obj.apply_configuration()
        self.dn_helper_obj.apply_configuration()
        self.local_dn_helper_obj.apply_configuration()
        self.gnb_helper_obj.apply_configuration()
        self._log.info("Successfully applied stats configurations on all nodes")
        self._log.debug("<")

    def _start_stats(self):
        """Method used to start the stats

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.ul_cl_helper_obj.start_stats()
        self._log.info("Started stats script on ULCL node: '%s'", self.ul_cl_helper_obj.get_management_ip())
        self.psa1_helper_obj.start_stats()
        self._log.info("Started stats script on PSA1 node: '%s'", self.psa1_helper_obj.get_management_ip())
        self.psa2_helper_obj.start_stats()
        self._log.info("Started stats script on PSA2 node: '%s'", self.psa2_helper_obj.get_management_ip())
        self.smf_helper_obj.start_stats()
        self._log.info("Started stats script on SMF node: '%s'", self.smf_helper_obj.get_management_ip())
        self.i_smf_helper_obj.start_stats()
        self._log.info("Started stats script on I-SMF node: '%s'", self.i_smf_helper_obj.get_management_ip())
        self.dn_helper_obj.start_stats()
        self._log.info("Started stats script on DN node: '%s'", self.dn_helper_obj.get_management_ip())
        self.local_dn_helper_obj.start_stats()
        self._log.info("Started stats script on Local-DN node: '%s'", self.local_dn_helper_obj.get_management_ip())
        self.gnb_helper_obj.start_stats()
        self._log.info("Started stats script on gNodeB node: '%s'", self.gnb_helper_obj.get_management_ip())
        self._log.debug("<")

    def _check_stats(self):
        """Method used to check the stats

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.ul_cl_helper_obj.check_stats()
        self.psa1_helper_obj.check_stats()
        self.psa2_helper_obj.check_stats()
        self.smf_helper_obj.check_stats()
        self.i_smf_helper_obj.check_stats()
        self.dn_helper_obj.check_stats()
        self.local_dn_helper_obj.check_stats()
        self.gnb_helper_obj.check_stats()
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
        self.ul_cl_helper_obj.setup_configuration_script()
        self.psa2_helper_obj.setup_configuration_script()
        self.i_smf_helper_obj.setup_configuration_script()
        self.local_dn_helper_obj.setup_configuration_script()
        self.gnb_helper_obj.setup_configuration_script()
        self._log.info("Completed configuration of scripts on all nodes")
        self._log.debug("<")

    def _stop_stats(self):
        """Method used to start the stats

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.ul_cl_helper_obj.stop_stats()
        self._log.info("Stopped stats script on ULCL node: '%s'", self.ul_cl_helper_obj.get_management_ip())
        self.psa1_helper_obj.stop_stats()
        self._log.info("Stopped stats script on PSA1 node: '%s'", self.psa1_helper_obj.get_management_ip())
        self.psa2_helper_obj.stop_stats()
        self._log.info("Stopped stats script on PSA2 node: '%s'", self.psa2_helper_obj.get_management_ip())
        self.smf_helper_obj.stop_stats()
        self._log.info("Stopped stats script on SMF node: '%s'", self.smf_helper_obj.get_management_ip())
        self.i_smf_helper_obj.stop_stats()
        self._log.info("Stopped stats script on I-SMF node: '%s'", self.i_smf_helper_obj.get_management_ip())
        self.dn_helper_obj.stop_stats()
        self._log.info("Stopped stats script on DN node: '%s'", self.dn_helper_obj.get_management_ip())
        self.local_dn_helper_obj.stop_stats()
        self._log.info("Stopped stats script on LOCAL-DN node: '%s'", self.local_dn_helper_obj.get_management_ip())
        self.gnb_helper_obj.stop_stats()
        self._log.info("Stopped stats script on DN node: '%s'", self.gnb_helper_obj.get_management_ip())
        self._log.debug("<")

    def manage_services(self):
        """Method used to manage the service

        Args:
            None

        Returns:
            None
        """
        self.i_smf_helper_obj.start_services(False)
        self._log.info("Started capturing tcpdump of PFD Management and PFCP Association and Session Establishment for ULCL on I-SMF node.")
        self._log.info("Started I-SMF simulator and sending packets towards ULCL node.")
        self.i_smf_helper_obj.start_services(True)
        self._log.info("Started capturing tcpdump of PFD Management and PFCP Association and Session Establishment for PSA2 on I-SMF node.")
        self._log.info("Started I-SMF simulator and sending packets towards PSA2 node.")
        time.sleep(TestCaseConstants.SLEEP_TIME)
        self.local_dn_helper_obj.start_services(True)
        self._log.info("Started capturing tcpdump of uplink and downlink packets on LOCAL-DN node.")
        self._log.info("Started LOCAL-DN simulator.")
        self.gnb_helper_obj.start_services(True)
        self._log.info("Started capturing tcpdump of uplink and downlink packets on gNodeB node.")
        self._log.info("Started gNodeB simulator.")
        self._log.info("gNodeB sent uplink packet towards ULCL.")
        self._log.info("ULCL sent uplink packet towards PSA2.")
        self._log.info("Waiting {} seconds for exchange uplink and downlink packets to be completed.".format(TestCaseConstants.SLEEP_TIME_FOR_LOCAL_DN))
        time.sleep(TestCaseConstants.SLEEP_TIME_FOR_LOCAL_DN)
        self._log.info("LOCAL-DN received downlink packet from PSA2.")
        self.gnb_helper_obj.stop_services(True)
        self._log.info("Stopped capturing tcpdump of uplink and downlink packets on gNodeB node.")
        self._log.info("Stopped gNodeB simulator.")
        self.local_dn_helper_obj.stop_services(True)
        self._log.info("Stopped capturing tcpdump of uplink and downlink packets on LOCAL-DN node.")
        self._log.info("Stopped LOCAL-DN simulator.")
        self.i_smf_helper_obj.stop_services(False)
        self._log.info("Stopped capturing tcpdump and PFD Management and PFCP Association and Session Establishment for ULCL on I-SMF node.")
        self._log.info("Stopped I-SMF simulator of ULCL script.")
        self.i_smf_helper_obj.stop_services(True)
        self._log.info("Stopped capturing tcpdump and PFD Management and PFCP Association and Session Establishment for PSA2 on I-SMF node.")
        self._log.info("Stopped I-SMF simulator of PSA2 script.")

    def validate_pcap(self):
        """Method used to validate pcap file captured in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self._log.info("Copying captured pcap files from SMF, I-SMF, LOCAL_DN and gNodeB nodes and validating pcap traces.")
        self.i_smf_helper_obj.validate_ulcl_pcap()
        self.local_dn_helper_obj.validate_ulcl_pcap()
        self.gnb_helper_obj.validate_ulcl_pcap()
        self._log.info("PFD Management, PFCP Association, Session Establishment, uplink and downlink packets validated successfully.")
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
            self.ul_cl_helper_obj.restart_upf_server()
            self.psa2_helper_obj.restart_upf_server()
            self.manage_services()
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
