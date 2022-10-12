""" Helper library to support iwf ss7 tool
"""

#from regal.utility import GetRegal
#import regal.logger.logger as logger
#from regal.constants import Constants
from Diametriq.helper.diametriq_helper_util import DiametriqHelperUtil

class IWFSS7PerfHelper(object):
    """ Base class whcih supports the common operation for iwf ss7 helper
    """
    def __init__(self, node_name, app_name, ss7_type=None):
        self._log = logger.GetLogger("IWFSS7PerfHelper")
        self._log.debug(">")
        self._node_name = node_name
        self._app_name = app_name
        self._topology = GetRegal().GetCurrentRunTopology()
        self._sut_name = GetRegal().GetCurrentSutName()
        self._run_count = GetRegal().GetCurrentRunCount()
        self._runner = GetRegal().GetRunMgr().get_runner(
            self._run_count, self._sut_name)
        self._suite_name = self._runner.get_suite_name()
        self._testcase_name = self._runner.get_tc_name()
        self._node_obj = self._topology.get_node(node_name)
        self._os_obj = self._node_obj.get_os()
        self._platform_obj = self._os_obj.platform
        self._tool_obj = self._platform_obj.get_app(app_name)
        self._topology_node_list = self._topology.get_node_list()
        self._config = self._runner.get_test_configuration()
        self._ts_config = None
        self._ss7_bin_path = None
        self._ss7_type = ss7_type
        self._util = DiametriqHelperUtil(node_name)
        self._log.debug("<")

    def get_tag_dict(self, config_dict, filter_list=None):
        """ This public method creats the tag_dict for configuartion.

        Args:
            config_data(dict): restore tag configuration

        Returns:
            dict: tag dictionary.

        """
        if not filter_list:
            filter_list = []
        key_list = self._util._get_keys(config_dict, filter_list)
        tag_dict = {}
        for key in key_list:
            value = config_dict[key]
            tag_dict[key] = self._util.get_config_value(value)
        return tag_dict

    def setup_ss7_tool(self):
        """This method is used to generate and copy the config files to iwf ss7 perf tool
        bin path

        Return:
            None

        """
        self._log.debug(">")
        node_config = self._config.get_testcase_config(self._node_name)
        if node_config != '-NA-':
            if "PerfConfiguration" in node_config:
                if "Config_dictionary" in node_config["PerfConfiguration"]:
                    perf_config = node_config["PerfConfiguration"]["Config_dictionary"]
                    self._validate_ss7perf_config_fields(perf_config)
                    instance = self._util.get_config_value(perf_config["Instance"])
                    default_config = self.get_tag_dict(perf_config["Default_config"])
                    variable_config = self.get_tag_dict(perf_config["Variable_config"])
                    config = {}
                    config.update(variable_config)
                    config.update(default_config)
                    self._tool_obj.get_config()
                    self._setup_ss7_instance(variable_config, config, 1, instance)

    def _setup_ss7_instance(self, variable_config, config, start_instance, end_instance):
        """ This method is used to setup the ss7 perf instance

        Args:
            variable_config(dict): variable configuration dict
            config(dict): configuration dict.
            start_instance(int): start instance
            end_instance(int): end instance

        Returns:
            None

        """
        for index in range(start_instance, end_instance+1):
            for key, val in list(variable_config.items()):
                if isinstance(val, list):
                    if str(val[1]).strip():
                        config[key] = "{}{:02d}.{}".format(val[0], index, val[1])
                    else:
                        config[key] = "{}{}".format(val[0], index)
                else:
                    config[key] = val + index
            self._tool_obj.setup_ss7_inst(index, config)

    def _validate_ss7perf_config_fields(self, config_dict):
        """
        """
        self._log.debug(">")
        config_mandatory_fileds = ["Instance", "Default_config",
                                   "Variable_config"]
        self._util._check_key(config_dict, config_mandatory_fileds)
        self._log.debug("<")

    def start_ss7_tool(self):
        """Method used to start iwf ss7 tool and send traffic to iwf node

        Return:
            None

        """
        self._log.debug("<")
        self._log.debug("Iwf ss7 tool started")
        total_inst, tag = self._get_tc_ts_info()
        self._ts_config = GetRegal().GetCurrentTestConfiguration()
        self._ss7_bin_path = self._ts_config.get_global_config("ss7_perf_bin_path")
        self._log.debug("Binary path configured - %s", self._ss7_bin_path)
        opc, dpc, msg_burst, dest_ssn, src_ssn, no_of_mesg, sleep, include_sccp_address, gtt, inter_routing, msg_choice = self._fetch_tc_config_traffic_param_info()
        self._node_obj.create_login_session(total_inst, tag)
        for inst_num in range(1, total_inst+1):
            self._node_obj.get_login_session_mngr().execute_command('cd {}'.format(self._ss7_bin_path), tag, inst_num)
            self._node_obj.get_login_session_mngr().match_prompt(Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command('./Run-SG-ITU{}'.format(inst_num), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(["=== >Enter OPC:"], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(opc).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(["=== >Enter DPC:"], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(dpc).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(['SCCP Address'], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(include_sccp_address).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(["=== >Enter Destination SSN:"], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(dest_ssn).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(["=== >Enter Source SSN:"], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(src_ssn).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(['GTT enter'], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(gtt).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(['SetInternationalRouting'], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(inter_routing).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(["Number of Messages"], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(no_of_mesg).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(['Enter Burst Size'], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(msg_burst).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(['Enter Sleep Time between bursts'], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(sleep).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(['Choice'], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command(repr(msg_choice).encode('utf-8'), tag, inst_num)
            self._node_obj.get_login_session_mngr().get_before_output(tag, inst_num)
            self._node_obj.get_login_session_mngr().get_after_output(tag, inst_num)
        self._log.debug(">")

    def _fetch_tc_config_traffic_param_info(self):
        """Method is used to fetch testcase config traffic_param info
        """
        node_config = self._config.get_testcase_config(self._node_name)
        traffic_param = self.get_tag_dict(node_config["PerfConfiguration"]["Config_dictionary"]["traffic_param"])
        opc = traffic_param["opc"]
        dpc = traffic_param["dpc"]
        msg_burst = traffic_param["message_burst"]
        dest_ssn = traffic_param["destination_ssn"]
        src_ssn = traffic_param["source_ssn"]
        no_of_mesg = traffic_param["num_of_messages"]
        sleep = traffic_param["sleep"]
        include_sccp_address = traffic_param["include_sccp_address"]
        gtt = traffic_param["gtt"]
        inter_routing = traffic_param["international_routing"]
        msg_choice = traffic_param["message_choice"]
        return opc, dpc, msg_burst, dest_ssn, src_ssn, no_of_mesg, sleep, include_sccp_address, gtt, inter_routing, msg_choice


    def stop_ss7_tool(self):
        """Method is used to stop the iwf ss7 tool

        Return:
            None
        """

        self._log.debug("<")
        self._log.debug("Executing Iwf ss7 stop tool")
        total_inst, tag = self._get_tc_ts_info()
        for inst_num in range(1, total_inst+1):
            cmd = 'ps -elf | grep sample | grep tcap_iwf_itu{}.xml | grep -v grep | tr -s " " | cut -d " " -f 4'.format(inst_num)
            self._kill_process_id(cmd)
            self._node_obj.get_login_session_mngr().close_session(tag, inst_num)
        self._log.debug(">")

    def _kill_process_id(self, cmd):
        """Method used to kill the process id

        Args:
            res: command to get the pid for respective instance

        Returns:
            None
        """
        node_ip = self._util._get_management_ip(self._node_name)
        pid = GetRegal().GetAnsibleUtil().execute_shell(cmd, node_ip)
        kill_pid = 'kill -9 {}'.format(pid)
        GetRegal().GetAnsibleUtil().execute_shell(kill_pid, node_ip)

    def _get_tc_ts_info(self):
        """Method is used to get the testcase and testsuite config info
        """
        node_config = self._config.get_testcase_config(self._node_name)
        perf_config = node_config["PerfConfiguration"]["Config_dictionary"]
        total_inst = self._util.get_config_value(perf_config["Instance"])
        tag = self._ss7_type
        return total_inst, tag

