""" Helper library to support iwf diameter tool
"""

#from regal.utility import GetRegal
#import regal.logger.logger as logger
#from regal.constants import Constants
from Diametriq.helper.diametriq_helper_util import DiametriqHelperUtil

class IWFDiaPerfHelper(object):
    """ Base class whcih supports the common operation for iwf dia helper
    """
    def __init__(self, node_name, app_name, dia_type=None):
        self._log = logger.GetLogger("IWFDiaPerfHelper")
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
        self._dia_type = dia_type
        self._ts_config = None
        self._dia_bin_path = None
        self._topology_node_list = self._topology.get_node_list()
        self._config = self._runner.get_test_configuration()
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

    def _verify_status(self):
        """ This private method verifies the node/ machine matched for ss7 perf
        tool status.

        Returns:
            None

        """
        self._platform_obj.restart()
        self._platform_obj.verify_status()

    def setup_dia_tool(self):
        """This method is used to generate and copy the config files to iwf diaperf tool
        bin path

        Returns:
            None

        """
        self._log.debug(">")
        node_config = self._config.get_testcase_config(self._node_name)
        if node_config != '-NA-':
            if "PerfConfiguration" in node_config:
                if "Config_dictionary" in node_config["PerfConfiguration"]:
                    perf_config = node_config["PerfConfiguration"]["Config_dictionary"]
                    self._util._validate_diaperf_config_fields(perf_config)
                    instance = self._util.get_config_value(perf_config["Instance"])
                    default_config = self.get_tag_dict(perf_config["Default_config"])
                    variable_config = self.get_tag_dict(perf_config["Variable_config"])
                    config = {}
                    config.update(variable_config)
                    config.update(default_config)
                    self._tool_obj.get_config()
                    self._setup_dia_instance(variable_config, config, 1, instance)

    def _setup_dia_instance(self, variable_config, config, start_instance, end_instance):
        """ This method is used to setup the instance

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
            self._tool_obj.setup_dia_inst(index, config)

    def start_dia_tool(self):
        """Method used to start iwf dia tool

        Return:
            None
        """
        self._log.debug("<")
        self._log.debug("Iwf dia tool started")
        total_inst, tag = self._get_tc_ts_info()
        self._ts_config = GetRegal().GetCurrentTestConfiguration()
        self._dia_bin_path = self._ts_config.get_global_config("dia_perf_bin_path")
        self._log.debug("Binary path configured - %s", self._dia_bin_path)
        self._node_obj.create_login_session(total_inst, tag)
        for inst_num in range(1, total_inst+1):
            self._node_obj.get_login_session_mngr().execute_command('cd {}'.format(self._dia_bin_path), tag, inst_num)
            self._node_obj.get_login_session_mngr().match_prompt(Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().execute_command('./Run.client{}'.format(inst_num), tag, inst_num)
            self._node_obj.get_login_session_mngr().expected_match(["To exit now"], Constants.PEXPECT_TIMER, tag, inst_num)
            self._node_obj.get_login_session_mngr().get_before_output(tag, inst_num)
            self._node_obj.get_login_session_mngr().get_after_output(tag, inst_num)
        self._log.debug(">")

    def stop_dia_tool(self):
        """Method is used to stop the iwf dia tool

        Return:
            None
        """

        self._log.debug("<")
        self._log.debug("Executing Iwf dia stop tool")
        total_inst, tag = self._get_tc_ts_info()
        for inst_num in range(1, total_inst+1):
            cmd = 'ps -elf | grep sample | grep demo.xml.client{} | grep -v grep | tr -s " " | cut -d " " -f 4'.format(inst_num)
            self._kill_process_id(cmd)
            self._node_obj.get_login_session_mngr().close_session(tag, inst_num)
        self._log.debug(">")

    def _kill_process_id(self, cmd):
        """Method used to kill the process id

        Args:
            cmd: command to get the pid for respective instance

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
        tag = self._dia_type
        return total_inst, tag
