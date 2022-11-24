"""
Helper plugin for Unicorn app
"""
import os
from Regal.regal_constants import Constants as RegalConstants
from regal_lib.result.statistics_import import StatisticsImport
from Telaverge.telaverge_constans import UPFConstants
from regal_lib.corelib.common_utility import Utility
import Telaverge.apps.upf_exception as upf_exception
# from regal_lib.pcap.pcap_helper import PcapHelper
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP
from scapy.contrib.pfcp import PFCP

class PcapHelper:
    def __init__(self, service_store_obj):
        """ """
        self.service_store_obj = service_store_obj
        self.log_mgr_obj = self.service_store_obj.get_log_mgr_obj()
        self._log = self.log_mgr_obj.get_logger(self.__class__.__name__)
        self._log.debug("> ")
        self._log.debug("< ")

    def get_session_uuid_from_http_packets(self, file_name):
        """ Method read the pcap file and filter for the HTTP packets
        and get the sessuin UUID.

        Args:
            file_name(str): File path of the pcap

        Returns:
            str: session UUID

        """
        self._log.debug("> ")
        pkts = rdpcap(file_name)
        for pkts in pkts:
            if pkts.haslayer(TCP):
                if pkts[0][2].sport== 8000:
                    if pkts.haslayer(Raw):
                        response = pkts[0][3].load.decode('utf-8')
                        contents = response.split('\n')
                        for content in contents:
                            if 'Location' in content:
                                location_content = content.split('Location:')
                                self._log.debug("< ")
                                return location_content[1].strip()

class UnicornHelper(object):
    """
    Class for implementing Unicorn helper functions.
    """
    def __init__(self,service_store_obj, node_name, app_name):
        #super(UnicornHelper, self).__init__(service_store_obj, node_name, app_name)
        self._classname = self.__class__.__name__
        self.service_store_obj = service_store_obj
        self._log_mgr_obj = self.service_store_obj.get_log_mgr_obj()
        self._log = self._log_mgr_obj.get_logger(self.__class__.__name__)
        self._log.debug(">")
        self._node_name = node_name
        self._stats_mgr = self.service_store_obj.get_stat_mgr_obj()
        self._topology = self.service_store_obj.get_current_run_topology()
        self._node_obj = self._topology.get_node(node_name)
        self._os = self._node_obj.get_os()
        self._platform = self._os.platform
        self._unicorn_app = self._platform.get_app(app_name)
        self.sut_name = self.service_store_obj.get_current_sut()
        self.ts_name = self.service_store_obj.get_current_suite()
        self.tc_name = self.service_store_obj.get_current_test_case()
        self._pcap_helper = PcapHelper(self.service_store_obj)
        self._regal_root_path = os.getenv("REGAL_ROOT_PATH")
        if self._regal_root_path :
            self.root_path = self._regal_root_path
        else:
            self.root_path = "./regal_lib"
        self.unicorn_stats = StatisticsImport(service_store_obj, node_name)
        self._log.debug("<")

    def apply_configuration(self, stat_args_dict=None):
        """This method sets up the stats"""
        self._log.debug(">")
        if not stat_args_dict:
            stat_args_dict = {}
            stat_args_dict[self._node_name] = self.unicorn_stats.get_stats_argumnts()
        stats_app = self._os.platform.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.apply_configuration(stat_args_dict)
        self._log.debug("<")

    def start_stats(self, stats_list=None):
        """ This method starts the stats service script in the mapped machine.

        Returns:
            None

        """
        self._log.debug(">")
        if not stats_list:
            stats_list = self.unicorn_stats.get_stats_list()
        stats_app = self._platform.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.start_service(stats_list)
        self._log.debug("<")

    def stop_stats(self, stats_list= None):
        """ this method stops the stats service script in the mapped machine.

        returns:
            none

        """
        self._log.debug(">")
        if not stats_list:
            stats_list = self.unicorn_stats.get_stats_list()
        stats_app = self._platform.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.stop_service(stats_list)
        self._log.debug("<")

    def check_stats(self, stats_list= None):
        """ This method checks the stats service script in the mapped machine.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        if not stats_list:
            stats_list = self.unicorn_stats.get_stats_list()
        stats_app = self._platform.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.check_service_status(stats_list)
        self._log.debug("All stats successfully checked on node %s", str(self._node_name))
        self._log.debug("<")

    def generate_config_dict_from_topology(self):
        """
        Function to generate config_dict.

        Args:
            None.

        Returns:
            config (dict): Dictionary of node IPs and subnets.
        """
        self._log.debug(">")
        config_dict = self._unicorn_app.generate_config_dict_from_topology(
            self._topology)
        self._log.debug("<")
        return config_dict

    def restart_unicorn(self):
        """
        Start the datetime_server application
        Returns(bool):
            ret(bool): True if datetime_server is stopped or not running

        """
        self._log.debug(">")
        self.service_store_obj.get_login_session_mgr_obj().create_session(self._node_obj, 1, tag="restart_unicorn")
        ret  = self._unicorn_app.restart_unicorn_app(tag="restart_unicorn")
        self.service_store_obj.get_login_session_mgr_obj().close_session(tag="restart_unicorn")
        self._log.debug("<")
        return ret

    def set_configuration_for_tc(self, config_dict, test_dict):
        """
        Set configuration for the a particular testcase.
        Args:
            unicorn_server (str): IP address of the assigned Unicorn server
            node.
            test_dict (dict): Dictionary of testcase informations such as SUT
            name, testsuite name and testcase name.

        Returns:
            None.

        """
        self._log.debug(">")
        self._unicorn_app.set_configuration_for_tc(
            config_dict, test_dict)
        self._log.debug("<")

    def get_sut_list(self):
        """
        Method to fetch the list of SUTs in the app.

        Args:
            None.

        Returns:
            ret(list): List of available SUTs.
        """
        self._log.debug(">")
        status, msg = self._unicorn_app.get_sut_list()
        self._log.debug("<")
        return status, msg

    def get_ts_list(self, sut_name):
        """
        Method to fetch the list of Testsuites in the specified SUT name.

        Args:
            sut_name (str): Name of the SUT.

        Returns:
            ret(list): List of testsuite in the SUT.
        """
        self._log.debug(">")
        status, msg = self._unicorn_app.get_ts_list(sut_name)
        self._log.debug("<")
        return status, msg

    def get_tc_list(self, sut_name, ts_name):
        """
        Method to fetch the list of Testcases in the testsuite of the specified
        SUT.

        Args:
            sut_name (str): Name of the SUT.
            ts_name (str): Name of the Testsuite.

        Returns:
            ret(list): List of testcases in the testsuite of the specified SUT.
        """
        self._log.debug(">")
        status, msg = self._unicorn_app.get_tc_list(sut_name, ts_name)
        self._log.debug("<")
        return status, msg

    def start_tc_execution(self, sut_name, ts_name, tc_name):
        """
        Method to start the testcase execution in the node.

        Args:
            sut_name (str): Name of the SUT.
            ts_name (str): Name of the Testsuite.
            tc_name (str): Testcase name.

        Returns:
            ret (str): Request's response.
        """
        self._log.debug(">")
        status, msg = self._unicorn_app.start_tc_execution(sut_name, ts_name, tc_name)
        self._log.debug("<")
        return status, msg

    def stop_tc_execution(self, sut_name, ts_name, tc_name):
        """
        Method to start the testcase execution in the node.

        Args:
            sut_name (str): Name of the SUT.
            ts_name (str): Name of the Testsuite.
            tc_name (str): Testcase name.

        Returns:
            ret(str): Request's response.
        """
        self._log.debug(">")
        status, msg = self._unicorn_app.stop_tc_execution(sut_name, ts_name, tc_name)
        self._log.debug("<")
        return status, msg

    def get_tc_exec_status(self, sut_name, ts_name, tc_name):
        """
        Method to fetch the result of testcase execution in the node.

        Args:
            sut_name (str): Name of the SUT.
            ts_name (str): Name of the Testsuite.
            tc_name (str): Testcase name.

        Returns:
            ret(str): Response result.
        """
        self._log.debug(">")
        status, msg = self._unicorn_app.get_tc_exec_status(sut_name, ts_name, tc_name)
        self._log.debug("<")
        return status, msg

    def get_stats(self, sut_name, ts_name, tc_name):
        """
        Method to fetch the client stats.

        Args:
            sut_name (str): Name of the SUT.
            ts_name (str): Name of the Testsuite.
            tc_name (str): Testcase name.

        Returns:
            ret(str): Response result.
        """
        self._log.debug(">")
        status, msg = self._unicorn_app.get_stats(sut_name, ts_name, tc_name)
        self._log.debug("<")
        return status, msg

    def setup_real_node_script(self, capture_tcpdump, api_operation, session_uuid=None):
        """ Method used to copy the template, scripts and service file from regal to nodes.
        
        Args:
            None

        Return:
            None
        """
        self._log.debug(">")
        self.service_store_obj.get_login_session_mgr_obj().create_session(self._node_obj, 1, self._node_name)
        smf_node_obj = self._topology.get_node(UPFConstants.SMF)
        node_ip = smf_node_obj.get_management_ip()
        self._log.debug("> host ip smf%s", str(node_ip))
        if api_operation == UPFConstants.SESSION_CREATION:
            src_paths, template_args, dir_names = self.get_arguments_for_session_creation()
            template_args.update({"host_ip":node_ip, "uuid":session_uuid})
            self._copy_unicorn_testcase(src_paths, template_args, dir_names, capture_tcpdump)
        if api_operation == UPFConstants.SESSION_MODIFICATION:
            src_paths, template_args, dir_names = self.get_arguments_for_session_modification()
            template_args.update({"host_ip":node_ip, "uuid":session_uuid})
            self._copy_unicorn_testcase(src_paths, template_args, dir_names, capture_tcpdump)
        if api_operation == UPFConstants.SESSION_DELETION:
            src_paths, template_args, dir_names = self.get_arguments_for_session_deletion()
            template_args.update({"host_ip":node_ip, "uuid":session_uuid})
            self._copy_unicorn_testcase(src_paths, template_args, dir_names, capture_tcpdump)
        self._os.reload_system(self._node_name)
        self.service_store_obj.get_login_session_mgr_obj().close_session(self._node_name)
        self._log.debug("<")

    def _copy_unicorn_testcase(self, src_paths, template_args, dir_names, capture_tcpdump):
        """
        Method used to copy unicorn testcases.

        Args:
            None

        Return:
            None
        """
        self._log.debug(">")
        request_body_dest_path = "/opt/unicorn/testcases/{}/{}/{}/config/".format(dir_names[0], dir_names[1], dir_names[2])
        client_request_dest_path =  "/opt/unicorn/testcases/{}/{}/{}/test_config.json".format(dir_names[0], dir_names[1], dir_names[2])
        #creating new testcases
        mkdir_cmd = "mkdir -p /opt/unicorn/testcases/{}/{}/{}/config".format(dir_names[0], dir_names[1], dir_names[2])
        self.service_store_obj.get_login_session_mgr_obj().perform_operation(mkdir_cmd,
                        self._node_name, time_out=UPFConstants.PEXPECT_TIMER)
        #copying files to the node
        self.service_store_obj.get_login_session_mgr_obj().copy_files_to_node(self._node_obj, 
                        src_paths[0], request_body_dest_path)
        #copying template file to the node
        self._copy_template_file_to_remote_node(src_paths[1], client_request_dest_path, template_args)
        #copy capturing tcpdump script ans service file.
        if capture_tcpdump:
            tcp_dump_config = {"execute_upf_tcpdump_file":UPFConstants.RUN_TCP_DUMP_UNICORN,\
                                    "interface_name_1":"any",\
                                       "file_name_1":UPFConstants.DEST_PATH_FOR_UNICORN + self._node_name + "_pcap.pcap" }
            src_files = self._get_script_and_service_files_path([UPFConstants.RUN_SERVICE_TCP_DUMP_UPF, UPFConstants.TCP_DUMP_SERVICE_FILE_PATH_UPF])
            self._copy_template_file_to_remote_node(src_files[0], UPFConstants.DEST_PATH_FOR_UNICORN, tcp_dump_config)
            self._copy_template_file_to_remote_node(src_files[1], UPFConstants.DEST_PATH_FOR_SERVICE, tcp_dump_config)
        self._log.debug("<")
    
    def _copy_template_file_to_remote_node(self, src_path, dest_path, args):
        """ Method used to copy template file to remote node.
        
        Args:
            src_path : Source of a template file.
            dest_path: Destination of a template file. 
            args: Arguments which should be in render.

        Return:
            None
        """
        self._log.debug(">")
        self.service_store_obj.get_login_session_mgr_obj().copy_template_to_node(self._node_obj, \
                    src_path, dest_path, args)
        self._log.debug("<")

    def get_arguments_for_session_creation(self):
        """ Method used to create curl command and return args for client request body.
        
        Args:
            None

        Return:
            None
        """
        self._log.debug(">")
        dir_names = [UPFConstants.UPF_CREATION, UPFConstants.SOLUTION_CREATION, UPFConstants.SESSION_CREATION]
        src_paths = self._get_script_and_service_files_path([UPFConstants.SESSION_CREATION_JSON_PATH, UPFConstants.CLIENT_CREATION_JSON_PATH])
        session_creation_request_body = "/opt/unicorn/testcases/{}/{}/{}/config/{}".format(dir_names[0], dir_names[1], dir_names[2], 
                        UPFConstants.SESSION_CREATION_FILENAME)
        template_args = {"session_creation_request_body": session_creation_request_body}
        self._log.debug("<")
        return src_paths, template_args, dir_names

    def get_arguments_for_session_modification(self):
        """ Method used to create curl command and return args for client request body.
        
        Args:
            None

        Return:
            None
        """
        self._log.debug(">")
        dir_names = [UPFConstants.UPF_MODIFICATION, UPFConstants.SOLUTION_MODIFICATION, UPFConstants.SESSION_MODIFICATION]
        src_paths = self._get_script_and_service_files_path([UPFConstants.SESSION_MODIFICATION_JSON_PATH, UPFConstants.CLIENT_MODIFICATION_JSON_PATH])
        session_modification_request_body = "/opt/unicorn/testcases/{}/{}/{}/config/{}".format(dir_names[0], dir_names[1], dir_names[2],
                         UPFConstants.SESSION_MODIFICATION_FILENAME)
        template_args = {"session_modification_request_body": session_modification_request_body}
        self._log.debug("<")
        return src_paths, template_args, dir_names

    def get_arguments_for_session_deletion(self):
        """ Method used to create curl command and return args for client request body.
        
        Args:
            None

        Return:
            None
        """
        self._log.debug(">")
        dir_names = [UPFConstants.UPF_DELETION, UPFConstants.SOLUTION_DELETION, UPFConstants.SESSION_DELETION]
        src_paths = self._get_script_and_service_files_path([UPFConstants.SESSION_DELETION_JSON_PATH, UPFConstants.CLIENT_DELETION_JSON_PATH])
        session_deletion_request_body = "/opt/unicorn/testcases/{}/{}/{}/config/{}".format(dir_names[0], dir_names[1], dir_names[2], 
                    UPFConstants.SESSION_DELETION_FILENAME)
        template_args = {"session_deletion_request_body": session_deletion_request_body}
        self._log.debug("<")
        return src_paths, template_args, dir_names

    def get_management_ip(self, node_name=None):
        """ This private method returns the management ip of teh node given.

        Args:
            node_name(str): name of the node.

        Returns:
            str: management ip

        Raise:
            exception.InvalidConfiguration

        """
        self._log.debug(">")
        if not node_name:
            self._log.debug("<")
            return self._node_obj.get_management_ip()
        for node_obj in self._topology_node_list:
            if node_obj.get_name() == node_name:
                self._log.debug("<")
                return node_obj.get_management_ip()
        self._log.debug("<")
        raise upf_exception.InvalidConfiguration(
                "node {} is not having management_ip".format(node_name))

    def _get_script_and_service_files_path(self, host_file_paths):
        """ Method used to join the paths with root_path
        
        Args:
            host_file_paths: It contains list of host node script and service paths.

        Return:
            list: path_list
        """
        self._log.debug(">")
        path_list = []
        if not isinstance(host_file_paths, list):
            path_list.append(Utility.join_path(self.root_path, host_file_paths))
        else:
            for path in host_file_paths:
                path_list.append(Utility.join_path(self.root_path, path))
        self._log.debug("<")
        return path_list

    def capture_tcpdump_on_unicorn(self, action="start"):
        """ Method used to start the tcpdump on unicorn
        
        Args:
            action: action required to start/stop capturing tcpdump.

        Return:
            None
        """
        self._log.debug(">")
        self.service_store_obj.get_login_session_mgr_obj().create_session(self._node_obj, 1, self._node_name)
        command = "systemctl {} {}".format(action, UPFConstants.UPF_TCP_DUMP_SERVICE_NAME)
        self.service_store_obj.get_login_session_mgr_obj().perform_operation(command,
                     self._node_name, time_out=UPFConstants.PEXPECT_TIMER)
        if action == "start":
            check_status = "systemctl status {}".format(UPFConstants.UPF_TCP_DUMP_SERVICE_NAME)
            before_output = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
                        check_status, self._node_name, time_out=UPFConstants.PEXPECT_TIMER)
            if "active (running)" not in str(before_output):
                self._log.debug("< service is not running")
                raise upf_exception.FailedToStartService(
                    "Unable start service {}".format(UPFConstants.UPF_TCP_DUMP_SERVICE_NAME)
                )
        self.service_store_obj.get_login_session_mgr_obj().close_session(self._node_name)
        self._log.debug("<")

    def copy_pcap_file_and_get_session_uuid(self):
        """Method used to copy the file from remote host to regal.

        Args:
        
        Returns:
            None
        """
        self._log.debug(">")
        current_dir = self.service_store_obj.get_workspace_dir_path()
        dest_path = current_dir + "/"
        remote_src_path = Utility.join_path(UPFConstants.DEST_PATH_FOR_UNICORN, UPFConstants.UNICORN_PCAP_FILE_NAME)
        self.service_store_obj.get_login_session_mgr_obj().copy_files_from_node(self._node_obj, 
                            remote_src_path, dest_path)
        file_name = Utility.join_path(dest_path, UPFConstants.UNICORN_PCAP_FILE_NAME)
        session_uuid = self._pcap_helper.get_session_uuid_from_http_packets(file_name)
        self._log.debug("<")
        return session_uuid.strip()

