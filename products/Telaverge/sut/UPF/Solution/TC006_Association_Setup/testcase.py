"""
Total 7-servers [UPF, SMF, DN, gNodeB, UDM, UDR and Unicorn]
Testcase is to validate the pcap file captured in SMF node which is successfully generating the connection.
Steps:
    1. Start UPF node.
    2. Capture packets in SMF node.
    3. Start SMF node.
    4. PFCP Associtaion Setup Request sent from SMF to UPF.
    5. UPF responds back towards SMF with the Associtaion Setup Response.
    6. Stop capturing packets in SMF node.
    7. Stop SMF node.
    8. Copy pcap file from SMF node and Validate pcap traces between UPF and SMF.
    
"""


import time
import traceback

import regal_lib.corelib.custom_exception as exception
from Telaverge.helper.upf_helper import UPFHelper
from Telaverge.telaverge_constans import UPFConstants
from Telaverge.helper.unicorn_helper import UnicornHelper
from test_executor.test_executor.utility import GetRegal

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
        self._log.info("Completed configuration of scripts on all nodes")
        self._log.debug("<")

    def manage_script_services(self):
        """Method used to start the service in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self.smf_helper_obj.manage_smf_server(True)
        self._log.info("Started tcpdump capture on N4 interface.")
        self._log.info("Started SMF node.")
        self._log.info("PFCP Associtaion Setup Request sent from SMF to UPF.")
        self._log.info("Waiting {} seconds for PFCP Association Setup to be completed.".format(UPFConstants.SLEEP_TIME))
        time.sleep(UPFConstants.SLEEP_TIME)
        self.smf_helper_obj.manage_smf_server(False)
        self._log.info("Stopped tcpdump capture on N4 interface.")
        self._log.info("Stopped SMF node.")
        self._log.debug("<")

    def validate_pcap(self):
        """Method used to validate pcap file captured in remote node.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        self._log.info("Copying pcap file from SMF node and validating pcap traces.")
        self.smf_helper_obj.validate_real_node_pcap(UPFConstants.ASSOCIATION_SETUP)
        self._log.info("PFCP Associtaion Setup Response validated successfully.")
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
            self.smf_helper_obj.manage_smf_server(False)
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

