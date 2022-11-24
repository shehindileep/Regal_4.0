"""
Total 7-servers [UPF, SMF, DN, gNodeB, UDM, UDR and Unicorn]
Testcase is to validate the pcap file captured in SMF node which is successfully generating the connection.
Steps:
    1. Start UPF node.
    2. Capture packets in SMF node.
    3. Start SMF node.   
    4. PFCP Associtaion Setup Request sent from SMF to UPF.   
    5. UPF responds back towards SMF with the Associtaion Setup Response.   
    6. Create SMF context request sending from Unicorn simultaor.   
    7. PFCP Session Estashblishment Request sent from SMF to UPF.   
    9. PFCP Session Estashblishment Response sent from UPF to SMF. 
    10. Create SMF context request sent from Unicorn simultaor. 
    11. Capture packets in DN, gNodeB and Unicorn nodes.
    12. Start DN and gNodeB simulator.
    13. gNodeB simulator will send a packet towards UPF.
    14. UPF will process it and send it towards DN.
    15. DN simulator recieve the packet from UPF and inturn DN will send a packet towards UPF. 
    16. UPF will process the packet and send it towards gNodeB.
    17. Stop capturing packets DN and gNodeB nodes.
    18. Copy pcap file from DN and gNodeB.
    19. Validate Data transfer between gNodeb and DN nodes.
    21. Copy pcap file from unicorn node and get session ID and send it with Unicorn request.
    21. Modify SMF context request sending from Unicorn simultaor.   
    22. PFCP Session Modification Request sent from SMF to UPF.   
    23. PFCP Session Modification Response sent from UPF to SMF.   
    24. Modify SMF context request sent from Unicorn simultaor.
    25. Capture packets in DN and gNodeB nodes.
    26. Start DN and gNodeB simulator.
    27. gNodeB simulator will send a packet towards UPF.
    28. UPF will process it and send it towards DN.
    29. DN simulator recieve the packet from UPF and inturn DN will send a packet towards UPF. 
    30. UPF will process the packet but not send packet towards gNodeB.
    31. Stop capturing packets DN and gNodeB nodes.
    32. Copy pcap file from DN and gNodeB.
    33. Validated uplink data transfer between gNodeb and DN nodes. 
    34. Validate PFCP Associtaion Setup, Session Estashblishment and Session Modification packets.
"""

import time
import traceback

import regal_lib.corelib.custom_exception as exception
from Telaverge.helper.upf_helper import UPFHelper
from Telaverge.telaverge_constans import UPFConstants
from Telaverge.helper.unicorn_helper import UnicornHelper
from test_executor.test_executor.utility import GetRegal

class TestCaseConstants:
    SLEEP_TIME = 5

class UPFTest():
    """
    Initialize all the required parameter to start the test case.
        1. Create the upf node object.
        2. Create smf node object.
    """

    def __init__(self):
        # test executor service libraries
        self.regal_api = GetRegal()
        log_mgr_obj = self.regal_api.get_log_mgr_obj()
        self._log = log_mgr_obj.get_logger(self.__class__.__name__)
        self._log.debug(">")
        self.upf_helper_obj = UPFHelper(self.regal_api, UPFConstants.UPF_NODE_NAME, UPFConstants.UPF_APP)
        self.smf_helper_obj = UPFHelper(self.regal_api, UPFConstants.SMF_NODE_NAME, UPFConstants.SMF_5G_APP)
        self.unicorn_helper_obj = UnicornHelper(self.regal_api, UPFConstants.UNICORN_NODE_NAME, UPFConstants.UNICORN_APP)
        self.dn_helper_obj = UPFHelper(self.regal_api, UPFConstants.DN_NODE_NAME, UPFConstants.DN_APP)
        self.gnb_helper_obj = UPFHelper(self.regal_api, UPFConstants.GNB_NODE_NAME, UPFConstants.GNB_APP)    
        self.udm_helper_obj = UPFHelper(self.regal_api, UPFConstants.UDM_NODE_NAME, UPFConstants.UDM_APP)
        self.udr_helper_obj = UPFHelper(self.regal_api, UPFConstants.UDR_NODE_NAME, UPFConstants.UDR_APP)    
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
        self.upf_helper_obj.apply_configuration()
        self.smf_helper_obj.apply_configuration()
        self.unicorn_helper_obj.apply_configuration()
        self.dn_helper_obj.apply_configuration()
        self.gnb_helper_obj.apply_configuration()
        self.udm_helper_obj.apply_configuration()
        self.udr_helper_obj.apply_configuration()
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
        self.unicorn_helper_obj.check_stats()
        self.dn_helper_obj.check_stats()
        self.gnb_helper_obj.check_stats()
        self.udm_helper_obj.check_stats()
        self.udr_helper_obj.check_stats()
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
        self.unicorn_helper_obj.start_stats()
        self._log.info("Started stats script on Unicorn node: '%s'", self.unicorn_helper_obj.get_management_ip())
        self.dn_helper_obj.start_stats()
        self._log.info("Started stats script on DN node: '%s'", self.dn_helper_obj.get_management_ip())
        self.gnb_helper_obj.start_stats()
        self._log.info("Started stats script on gNodeB node: '%s'", self.gnb_helper_obj.get_management_ip())
        self.udm_helper_obj.start_stats()
        self._log.info("Started stats script on UDM node: '%s'", self.udm_helper_obj.get_management_ip())
        self.udr_helper_obj.start_stats()
        self._log.info("Started stats script on UDR node: '%s'", self.udr_helper_obj.get_management_ip())
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
        self.unicorn_helper_obj.stop_stats()
        self._log.info("Stopped stats script on Unicorn node: '%s'", self.unicorn_helper_obj.get_management_ip())
        self.dn_helper_obj.stop_stats()
        self._log.info("Stopped stats script on DN node: '%s'", self.dn_helper_obj.get_management_ip())
        self.gnb_helper_obj.stop_stats()
        self._log.info("Stopped stats script on gNodeB node: '%s'", self.gnb_helper_obj.get_management_ip())
        self.udm_helper_obj.stop_stats()
        self._log.info("Stopped stats script on UDM node: '%s'", self.udm_helper_obj.get_management_ip())
        self.udr_helper_obj.stop_stats()
        self._log.info("Stopped stats script on UDR node: '%s'", self.udr_helper_obj.get_management_ip())
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
        self.smf_helper_obj.setup_real_node_script()
        self.unicorn_helper_obj.setup_real_node_script(True, UPFConstants.SESSION_CREATION)
        self.dn_helper_obj.setup_script()
        self.gnb_helper_obj.setup_script()
        self._log.info("Completed configuration of scripts on all nodes")
        self._log.debug("<")

    def setup_scripts_and_manage_services(self):
        """Method used to setup the scripts in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.setup_scripts()
        self.upf_helper_obj.restart_upf_server()
        self.unicorn_helper_obj.capture_tcpdump_on_unicorn()
        self._log.info("Started tcpdump capture on Unicorn.")
        self.smf_helper_obj.manage_smf_server(True)
        self._log.info("Started tcpdump capture on N4 interface.")
        self._log.info("Started SMF node.")
        self._log.info("Waiting {} seconds for PFCP Association Setup to be completed.".format(UPFConstants.SLEEP_TIME))
        time.sleep(UPFConstants.SLEEP_TIME)
        self._log.info("Copying pcap file from SMF node and validating pcap traces.")
        self.smf_helper_obj.validate_session_pcap_file(UPFConstants.ASSOCIATION_SETUP)
        self._log.info("PFCP Associtaion Setup Response validated successfully.")
        self._log.info("Create SMF context sending from AMF simultaor")
        self._log.info("Waiting {} seconds for PFCP Session Estashblishment to be completed.".format(UPFConstants.SLEEP_TIME))
        time.sleep(UPFConstants.SLEEP_TIME)
        self.unicorn_helper_obj.start_tc_execution(UPFConstants.UPF_CREATION, UPFConstants.SOLUTION_CREATION, UPFConstants.SESSION_CREATION)
        self._log.info("Create SMF context sent from AMF simultaor")
        self._log.info("PFCP Session Estashblishment Request sent from SMF to UPF.")
        self._log.info("Copying pcap file from SMF node and validationg pcap traces.")
        self.smf_helper_obj.validate_session_pcap_file(UPFConstants.SESSION_CREATION)
        self._log.info("PFCP Session Estashblishment Response validated successfully.")
        self.unicorn_helper_obj.capture_tcpdump_on_unicorn("stop")
        self._log.info("Stopped tcpdump capture on Unicorn.")
        session_uuid = self.unicorn_helper_obj.copy_pcap_file_and_get_session_uuid()
        self._log.info("Copied pcap file from Unicorn to get Session ID to perform Session Modification.")
        self.start_data_exchange_between_gnodeb_and_dn()
        self.validate_gnodeb_and_dn_data_exchange()
        self.unicorn_helper_obj.setup_real_node_script(False, UPFConstants.SESSION_MODIFICATION, session_uuid)
        self._log.info("Copied Session Modification Request json file to Unicorn.")
        self.unicorn_helper_obj.start_tc_execution(UPFConstants.UPF_MODIFICATION, UPFConstants.SOLUTION_MODIFICATION, UPFConstants.SESSION_MODIFICATION)
        self._log.info("PFCP Session Modification Request sent from SMF to UPF.")
        self._log.info("Modify SMF context sent from AMF simultaor.")
        self.start_data_exchange_between_gnodeb_and_dn()
        self.smf_helper_obj.manage_smf_server(False)
        self._log.info("Stopped tcpdump capture on N4 interface.")
        self._log.info("Stopped SMF node.")
        self._log.info("Copying pcap file from SMF node and validationg pcap traces.")
        self.smf_helper_obj.validate_real_node_pcap(UPFConstants.SESSION_MODIFICATION)
        self._log.info("PFCP Session Modification Response validated successfully.")
        self.validate_gnodeb_and_dn_data_exchange(True)
        self._log.debug("<")

    def validate_gnodeb_and_dn_data_exchange(self, session_modification=None):
        """Method used to validate pcap file captured in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self._log.info("Copying pcap file from DN and gNode nodes and validating Data Transfer.")
        self.dn_helper_obj.validate_pcap()
        if not session_modification:
            self.gnb_helper_obj.validate_pcap()
        else:
            self.gnb_helper_obj.validate_gnodeb_pcap_after_session_modification_and_deletion(UPFConstants.SESSION_MODIFICATION)
        self._log.info("Upllink data transfer validated successfully between gNodeB and DN.")
        self._log.debug("<")

    def start_data_exchange_between_gnodeb_and_dn(self):
        """Method used to start the service in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.dn_helper_obj.start_services(True)
        self._log.info("Started capturing tcpdump of uplink and downlink packets on DN node.")
        self._log.info("Started DN simulator.")
        self.gnb_helper_obj.start_services(True)
        self._log.info("Started capturing tcpdump of uplink and downlink packets on gNodeB node.")
        self._log.info("Started gNodeB simulator.")
        self._log.info("gNodeB sent uplink packet towards UPF.")
        self._log.info("Waiting {} seconds for uplink and downlink packets to be completed.".format(TestCaseConstants.SLEEP_TIME))
        time.sleep(TestCaseConstants.SLEEP_TIME)
        self.dn_helper_obj.stop_services(True)
        self._log.info("Stopped capturing of uplink and downlink packets on DN node.")
        self._log.info("Stopped DN simulator.")
        self.gnb_helper_obj.stop_services(True)
        self._log.info("Stopped capturing of uplink and downlink packets on gNodeB node.")
        self._log.info("Stopped gNodeB simulator.")
        self._log.debug("<")

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
            self.setup_scripts_and_manage_services()
            self._stop_stats()
            self._log.debug("<")
        except Exception as ex:
            trace_back = traceback.format_exc()
            self._log.error("Exception caught while running test %s", str(ex))
            self._log.error("Traceback: %s", str(trace_back))
            self._stop_stats()
            self.smf_helper_obj.manage_smf_server(False)
            self.unicorn_helper_obj.capture_tcpdump_on_unicorn("stop")
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

