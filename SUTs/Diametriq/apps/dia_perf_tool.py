"""
This module is designed to provide interface between legacy
plugins (plugin_MML and plugin_dia_app) and the wrapper
"""
import sys
import os
import json
import traceback
import tempfile
import shutil
from jinja2 import Template

# regal libraries
from regal_lib.corelib.constants import Constants
from regal_lib.corelib.common_utility import Utility
import regal_lib.corelib.custom_exception as exception
from regal_lib.repo_manager.repo_mgr_client import RepoMgrClient

# Product specific libraries
from Diametriq.diametriq_constants import Constants as DiametriqConstants
from Diametriq.apps.diametriq_apps_util import DiametriqAppsUtil
from Regal.apps.appbase import AppBase
from Regal.regal_constants import Constants as RegalConstants
from regal_lib.sut.sut_user_info_mgr import SUTUserInfoMgr

IS_PY2 = sys.version_info < (3, 0)


class UninstallFailed(Exception):
    """ Exception will be thrown when Uninstalation is failed
    """

    def __init__(self, inst, error_msg):
        Exception.__init__(self)
        self._inst = inst
        self._error_msg = error_msg

    def __str__(self):
        """ Return exception string. """
        return "Failed to uninstall {} : {}".format(self._inst, self._error_msg)


class InstallFailed(Exception):
    """ Exception will be thrown when installatuion fialed
    """

    def __init__(self, inst, error_msg):
        Exception.__init__(self)
        self._inst = inst
        self._error_msg = error_msg

    def __str__(self):
        """ Return exception string. """
        return "Failed to install {} : {}".format(self._inst, self._error_msg)


class TimeOutException(Exception):
    """ Exception will be thrown during timeout 
    """

    def __init__(self, error_msg):
        Exception.__init__(self)
        self._error_msg = error_msg

    def __str__(self):
        """ Return exception string. """
        return "{}".format(self._error_msg)


class DiaPerfTool(AppBase, DiametriqAppsUtil):
    """
    Wrapper class for diameter performance tool, provides the functionalities
    required to performance benchmark

    """

    def __init__(self, service_store_obj, name, version):
        super(DiaPerfTool, self).__init__(service_store_obj, name, version)
        class_name = self.__class__.__name__
        self.service_store_obj = service_store_obj
        self._log_mgr_obj = self.service_store_obj.get_log_mgr_obj()
        self._log = self._log_mgr_obj.get_logger(class_name)
        self.repo_mgr_client_obj = RepoMgrClient(self.service_store_obj)
        self._internal_name = None
        self._internal_version = None
        self._imsdia_found_version = None
        self.app_found_version = None
        self._update_app_details()
        self._config = None
        self._bin_path = None
        self._profile_path = None
        self._mml_path = None
        self._tt_config = None
        self.host_id = "00000000"
        self.regal_root_path = os.getenv("REGAL_ROOT_PATH")
        if self.regal_root_path:
            self._hostid_script_path = "{}/config/change_host_id".format(
                self.regal_root_path)
        else:
            self._hostid_script_path = os.path.abspath(
                "./regal_lib/config/change_host_id")
        self._its_dia_file = None
        self._run_file = None
        self._demo_xml_file = None
        self._dbc_console_file = None
        self._dia_client_templates = {
            "itsdia": "itsdiaclient.xml",
            "run_file": "Run.client",
            "demo_xml": "demo.xml.client",
            "dbc_ini": "dbc_console.client.ini"
        }
        self._dia_server_templates = {
            "itsdia": "itsdiaserver.xml",
            "run_file": "Run.server",
            "demo_xml": "demo.xml.server",
            "dbc_ini": "dbc_console.server.ini"
        }

    def _update_app_details(self):
        self._log.debug(">")
        if "_" in self._version:
            self._internal_name = self._version.split("_")[0]
            self._internal_version = self._version.split("_")[1]
            self._log.debug("<")
        else:
            self._internal_name = self._name
            self._internal_version = self._version
            self._log.debug("<")

    def get_imsdia_repo_url(self):
        self._log.debug(">")
        name = 'IMSDIA'
        self._imsdia_repo_path = self.get_repo_url(name)
        self._log.debug("<")
        return self._imsdia_repo_path

    def get_imsdia_repo_path(self):
        self._log.debug(">")
        name = 'IMSDIA'
        self._imsdia_repo_path = self.get_repo_path(name)
        self._log.debug("<")
        return self._imsdia_repo_path

    def get_config(self):
        """
        This metod fetches the global configurations defined
        in testcase_conf.json

        Args:
            None
        Returns:
            None
        """
        try:
            self._log.debug(">")
            #self._config = GetRegal().GetCurrentTestConfiguration()
            self._config = self.service_store_obj.get_current_test_suite_configuration()
            if self._name == "MME" or self._name == "HSS"\
                    or self._name == 'CTF' or self._name == 'OCS':
                self._bin_path = self.add_slash(
                    self._config.get_global_config("bin_path"))
                self._log.debug("Binary path configured - %s",
                                str(self._bin_path))
                self._profile_path = self.add_slash(
                    self._config.get_global_config("dia_profile_path"))
                self._log.debug("Profile path configured - %s",
                                str(self._profile_path))
                self._mml_path = self.add_slash(
                    self._config.get_global_config("mml_path"))
                self._log.debug("MML path configured - %s",
                                str(self._mml_path))

            elif self._name == "DSS":
                self._bin_path = self.add_slash(
                    self._config.get_global_config("dss_bin_path"))
                self._log.debug("Binare path configured - %s",
                                str(self._bin_path))
                self._profile_path = self.add_slash(
                    self._config.get_global_config("dss_profile_path"))
                self._log.debug("Profile path configured - %s",
                                str(self._profile_path))
                self._mml_path = self.add_slash(
                    self._config.get_global_config("dss_mml_path"))
                self._log.debug("MML path configured - %s",
                                str(self._mml_path))

            elif self._name == "DSA":
                self._bin_path = self.add_slash(
                    self._config.get_global_config("dsa_bin_path"))
                self._log.debug("Binary path configured - %s",
                                str(self._bin_path))
                self._profile_path = self.add_slash(
                    self._config.get_global_config("dsa_profile_path"))
                self._log.debug("Profile path configured - %s",
                                str(self._profile_path))

            self._log.debug("<")
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.error("Failed to get test configurations for node %s",
                            self.get_node().get_management_ip())
            self._log.error("Exception is - %s", str(ex))
            self._log.error("Traceback - %s", (traceback_))
            raise Exception(ex)

    def _set_dia_templates(self, peer_type, inst_key):
        """
        This method decides the name of diameter configuration file names based on the
        peer_type and inst_key

        Args:
            peer_type: str
            inst_key: int

        Returns:
            dia_templates: dict
        Exception:
            Raises exceptuion in case of failure
        """
        try:
            self._log.debug(">")
            self._log.debug(
                "Setting Diameter templates and configuration files for %d", inst_key)
            if self._name == "MME" or self._name == "HSS" or\
                    self._name == 'CTF' or self._name == 'OCS':
                if peer_type.lower() == 'c':
                    dia_templates = self._dia_client_templates
                    self._its_dia_file = "itsdiaclient{}.xml".format(
                        str(inst_key))
                    self._run_file = "Run.client{}".format(str(inst_key))
                    self._demo_xml_file = "demo.xml.client{}".format(
                        str(inst_key))
                    self._dbc_console_file = "dbc_console.client{}.ini".format(
                        str(inst_key))
                    self._log.debug(
                        "Diameter client configuration files %s, %s, %s, %s",
                        self._its_dia_file, self._run_file, self._demo_xml_file,
                        self._dbc_console_file)
                elif peer_type.lower() == 's':
                    dia_templates = self._dia_server_templates
                    self._its_dia_file = "itsdiaserver{}.xml".format(
                        str(inst_key))
                    self._run_file = "Run.server{}".format(str(inst_key))
                    self._demo_xml_file = "demo.xml.server{}".format(
                        str(inst_key))
                    self._dbc_console_file = "dbc_console.server{}.ini".format(
                        str(inst_key))
                    self._log.debug(
                        "Diameter server configuration files %s, %s, %s, %s",
                        self._its_dia_file, self._run_file, self._demo_xml_file,
                        self._dbc_console_file)
            elif self._name == "DSS":
                if peer_type.lower() == 's':
                    dia_templates = self._dia_server_templates
                    self._its_dia_file = "itsdiaserver{}.xml".format(
                        str(inst_key))
                    self._run_file = "Run.server{}".format(str(inst_key))
                    self._demo_xml_file = "demo.xml.server{}".format(
                        str(inst_key))
                    self._dbc_console_file = "dbc_console.server{}.ini".format(
                        str(inst_key))
                    self._log.debug(
                        "DSS Server configuration files %s, %s, %s, %s",
                        self._its_dia_file, self._run_file, self._demo_xml_file,
                        self._dbc_console_file)
            elif self._name == "DSA":
                if peer_type.lower() == 's':
                    dia_templates = {
                        "run_file": "Run.server"
                    }

                    self._run_file = "Run.server{}".format(str(inst_key))
            self._log.debug("<")
            return dia_templates
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.error("Failed to _set_dia_templates for instance %d on node %s",
                            inst_key, self.get_node().get_management_ip())
            self._log.error("Exception is - %s", str(ex))
            self._log.error("Traceback - %s", (traceback_))
            raise Exception(ex)

    def _generate_itsdia_script(self, config_dict, template_):
        """
        This method generates test configurations for dbc_ini.
        Args:
            config_dict: dict
            template_:

        Returns:
            None
        """
        self._log.debug(">")
        configuration = {}
        node_ip = self.get_node().get_management_ip()
        self._log.info(
            "Genarating %s test configuration file %s",
            self._name, str(self._its_dia_file))

        local_other_home_ip = ''
        peer_other_home_ip = ''
        sctp_parameters = {
            "cookie_life": 60000,
            "hb_on": "yes",
            "hb_timeout": 10000,
            "init_timeout": 3000,
            "max_attempts": 16,
            "max_in_streams": 12,
            "num_out_streams": 12,
            "recv_timeout": "0,0",
            "send_timeout": "0,0",
            "shutdown_timeout": 300,
            "sack_delay": 5,
            "asoc_max_attempt": 16,
            "rto_max": 60000,
            "rto_min": 2000,
            "rto_initial": 3000,
            "send_buf_size": 102400,
            "recv_buf_size": 102400,
            "pathmaxrxt": 16
        }

        if config_dict["transport_type"].lower() == "sctp":
            sctp_begin_comm = ""
            sctp_end_comm = ""
            if 'local_other_home_ip' in config_dict:
                local_other_home_ip = '<OtherHome serverIpAddr = "{}"/>'.format(
                    config_dict['local_other_home_ip'])
            if 'peer_other_home_ip' in config_dict:
                peer_other_home_ip = '<OtherHome serverIpAddr = "{}"/>'.format(
                    config_dict['peer_other_home_ip'])
            if 'sctp_parameters' in config_dict:
                sctp_parameters.update(config_dict['sctp_parameters'])

        elif config_dict["transport_type"].lower() == "tcp":
            sctp_begin_comm = "!--"
            sctp_end_comm = "--"

        if self._name == "MME" or self.name == "HSS"\
                or self._name == 'CTF' or self._name == 'OCS':
            configuration = {
                "initiate_conn": config_dict["initiate_conn"],
                "auth_application_id": config_dict["auth_application_id"],
                "local_host": config_dict["local_host"],
                "local_realm": config_dict["local_realm"],
                "transport_type": config_dict["transport_type"],
                "local_ip": config_dict["local_ip"],
                "local_port": config_dict["local_port"],
                "local_other_home_ip": local_other_home_ip,
                "peer_other_home_ip": peer_other_home_ip,
                "remote_host": config_dict["remote_host"],
                "dest_host": config_dict["dest_host"],
                "remote_realm": config_dict["remote_realm"],
                "remote_ip": config_dict["remote_ip"],
                "dest_realm": config_dict["dest_realm"],
                "remote_port": config_dict["remote_port"],
                "sctp_begin_comm": sctp_begin_comm,
                "sctp_end_comm": sctp_end_comm,
                "cookie_life": sctp_parameters['cookie_life'],
                "hb_on": sctp_parameters['hb_on'],
                "hb_timeout": sctp_parameters['hb_timeout'],
                "init_timeout": sctp_parameters['init_timeout'],
                "max_attempts": sctp_parameters['max_attempts'],
                "max_in_streams": sctp_parameters['max_in_streams'],
                "num_out_streams": sctp_parameters['num_out_streams'],
                "recv_timeout": sctp_parameters['recv_timeout'],
                "send_timeout": sctp_parameters['send_timeout'],
                "shutdown_timeout": sctp_parameters['shutdown_timeout'],
                "sack_delay": sctp_parameters['sack_delay'],
                "asoc_max_attempt": sctp_parameters['asoc_max_attempt'],
                "rto_max": sctp_parameters['rto_max'],
                "rto_min": sctp_parameters['rto_min'],
                "rto_initial": sctp_parameters['rto_initial'],
                "send_buf_size": sctp_parameters['send_buf_size'],
                "recv_buf_size": sctp_parameters['recv_buf_size'],
                "pathmaxrxt": sctp_parameters['pathmaxrxt']
            }
        elif self.name == "DSS":
            configuration.update({
                "msgrouterthread": config_dict["msgrouterthread"],
                "initiate_conn": config_dict["initiate_conn"],
                "auth_application_id": config_dict["auth_application_id"],
                "local_host": config_dict["local_host"],
                "local_realm": config_dict["local_realm"],
                "transport_type": config_dict["transport_type"],
                "local_ip": config_dict["local_ip"],
                "local_port": config_dict["local_port"],
                "remote_host": config_dict["remote_host"],
                "remote_realm": config_dict["remote_realm"],
                "remote_ip": config_dict["remote_ip"],
                "remote_port": config_dict["remote_port"],
            })

        self._render_template(template_, configuration, self._its_dia_file)
        self._log.info(
            "Genarated %s test configuration file %s",
            self._name, str(self._its_dia_file))
        self._log.debug("<")

    def _generate_run_script(self, config_dict, template_):
        """
        This method generates test configurations for dbc_ini.
        Args:
            config_dict: dict
            template_:

        Returns:
            None
        """
        self._log.debug(">")
        node_ip = self.get_node().get_management_ip()
        self._log.info(
            "Genarating %s test configuration file %s",
            self._name, str(self._run_file))
        configuration = {}
        imsi_range = ''
        if 'imsi_range' in config_dict:
            imsi_start, imsi_end = config_dict['imsi_range'].split('-')
            imsi_range = '-imsistart {} -imsiend {}'.format(
                imsi_start, imsi_end)
        tt_config = ''
        if 'start_val' in config_dict:
            tt_config = '-tt_config_file {}'.format(self._ttconfig_fname)
        if self._name == "MME" or self._name == "HSS"\
                or self._name == 'CTF' or self._name == 'OCS':
            configuration = {
                "sample_binary": config_dict["sample_binary"],
                "local_host": config_dict["local_host"],
                "local_realm": config_dict["local_realm"],
                "dest_host": config_dict["dest_host"],
                "dest_realm": config_dict["dest_realm"],
                "sender_thread": config_dict["sender_thread"],
                "reciever_thread": config_dict["reciever_thread"],
                "demo_xml_file": self._demo_xml_file,
                "imsi_range": imsi_range,
                "tt_config": tt_config
            }
        elif self._name == "DSS":
            configuration.update({
                "stack_binary": config_dict["stack_binary"],
                "demo_xml_file": self._demo_xml_file
            })

        elif self._name == "DSA":
            configuration.update({
                "sample_binary": config_dict["sample_binary"],
                "local_host": config_dict["local_host"],
                "local_realm": config_dict["local_realm"],
                "dest_host": config_dict["dest_host"],
                "dest_realm": config_dict["dest_realm"],
                "dss_ids_port": config_dict["dss_ids_port"],
                "dss_ids_ip": config_dict["dss_ids_ip"]
            })

        self._render_template(template_, configuration, self._run_file)
        self._log.info(
            "Genarated %s test configuration file %s",
            self._name, str(self._run_file))
        self._log.debug("<")

    def _generate_demo_xml_script(self, config_dict, template_, mml):
        """
        This method generates test configurations for dbc_ini.
        Args:
            config_dict: dict
            template_:
            mml (bool):

        Returns:
            None
        """
        self._log.debug(">")
        configuration = {}
        node_ip = self.get_node().get_management_ip()
        self._log.info(
            "Genarating %s test configuration file %s", self._name, str(self._demo_xml_file))
        if mml is True:
            mml_port = config_dict["mml_port"]
        else:
            mml_port = "NA"
        if self._name == "DSS":
            configuration.update({
                "mml_port": config_dict["mml_port"],
                "its_dia_file": self._its_dia_file,
                "dss_ids_ip": config_dict["dss_ids_ip"],
                "dss_ids_port": config_dict["dss_ids_port"]
            })
        elif self._name == "MME" or self._name == "HSS"\
                or self._name == 'CTF' or self._name == 'OCS':
            configuration.update({
                "its_dia_file": self._its_dia_file,
                "mml_port": mml_port,
            })

        self._render_template(template_, configuration, self._demo_xml_file)
        self._log.info(
            "Genarated %s test configuration file %s", self._name, str(self._demo_xml_file))
        self._log.debug("<")

    def _generate_dbc_ini_script(self, config_dict, template_):
        """
        This method generates test configurations for dbc_ini.
        Args:
            config_dict: dict
            template_:

        Returns:
            None
        """
        self._log.debug(">")

        node_ip = self.get_node().get_management_ip()
        self._log.info("Genarating %s test configuration file %s",
                       self._name, str(self._dbc_console_file))
        configuration = {
            "mml_port": config_dict["mml_port"]
        }
        dest = "{}{}".format(
            self._mml_path, self._dbc_console_file)
        self.service_store_obj.get_login_session_mgr_obj().copy_template_to_node(
            self.get_node(), template_, dest, configuration,
            Constants.PEXPECT_TIMER)
        self._log.info("Genarating %s testconfiguration file %s", self._name, str(
            self._dbc_console_file))
        self._log.debug("<")

    def _generate_tt_config_script(self, tt_config, ttconfig_fname=None):
        self._log.debug(">")
        node_ip = self.get_node().get_management_ip()
        if self._name == 'CTF':
            ttconfig_fname = "perf_config.json"
            self._tt_config_file = self._perf_config_file
        configuration = {}
        configuration["tt_config"] = json.dumps(tt_config)
        if not ttconfig_fname:
            self._render_template(self._tt_config_file, configuration,
                                  "tt_config.json")
        else:
            self._render_template(self._tt_config_file,
                                  configuration, ttconfig_fname)

        self._log.info(
            "Genarated %s test configuration file %s", self._name,
            str(self._tt_config_file))
        self._log.debug("<")

    def _generate_test_scripts(self, peer_type, inst_key, config_dict,
                               tt_config, mml):
        """
        This method generates test configurations for diameter application.
        Args:
            peer_type: str
            inst_key: int
            config_dict: dict
            mml: bool

        Returns:
            None
        Exception:
            Raises exception in case of failure

        """
        try:
            self._log.debug(">")
            _temp_dir = self.create_temp_dir()
            node_ip = self.get_node().get_management_ip()
            self._log.info(
                "Genarating %s test configuratios for instance - %d on node %s",
                self._name, inst_key, node_ip)

            if peer_type.lower() == 'c' and "start_val" in config_dict and \
                    inst_key == config_dict["start_val"] and tt_config != '-NA-':
                self._ttconfig_fname = "tt_config_{}.json".format(
                    config_dict["start_val"])
                self._generate_tt_config_script(
                    tt_config, self._ttconfig_fname)

            elif peer_type.lower() == 'c' and inst_key == 1 and \
                    tt_config != '-NA-':
                self._generate_tt_config_script(tt_config)

            dia_templates = self._set_dia_templates(peer_type, inst_key)
            for template_key in dia_templates:
                if self._name == "MME" or self._name == "HSS":
                    template_ = "{}{}".format(self.add_slash(
                        self._dia_template_path), dia_templates[template_key])
                elif self.name == "CTF" or self._name == "OCS":
                    template_ = "{}{}".format(self.add_slash(
                        self._ocs_template_path), dia_templates[template_key])
                elif self.name == "DSS":
                    template_ = "{}{}".format(self.add_slash(
                        "{}/config/sut/dss_templates/".format(self.product_path)), dia_templates[template_key])

                elif self.name == "DSA":
                    template_ = "{}{}".format(self.add_slash(
                        "{}/config/sut/dsa_templates/".format(self.product_path)), dia_templates[template_key])

                """
                with open(template_, "r") as config_file_fd:
                    template_ = config_file_fd.read()
                    #template_ = config_file_fd.read().replace("\n", "")
                """

                #template_ = Template(str(template_))

                if template_key == "itsdia":
                    self._generate_itsdia_script(config_dict, template_)
                elif template_key == "run_file":
                    self._generate_run_script(config_dict, template_)
                elif template_key == "demo_xml":
                    self._generate_demo_xml_script(config_dict, template_, mml)
                elif template_key == "dbc_ini" and mml is True:
                    self._generate_dbc_ini_script(config_dict, template_)

            src_files = Utility.get_file_list(_temp_dir)
            self.service_store_obj.get_login_session_mgr_obj().copy_files_to_node(
                self.get_node(), src_files, self._bin_path,
                Constants.PEXPECT_TIMER)
            self._delete_temp_dir()
            self._log.info(
                "Generated and copied the %s configurations to %s", self._name, node_ip)
            self._log.debug("<")
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.error(
                "Failed to generate test configuration files for instance\
                - %d on node %s", inst_key, node_ip)
            self._log.error("Exception is - %s", str(ex))
            self._log.error("Traceback - %s", (traceback_))
            raise Exception(ex)

    def _check_imsdia(self, hosts):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self.update_persist_data(
            infra_ref, "imsdia_found_version", None, self._sw_type)
        self.update_persist_data(
            infra_ref, "app_found_version", None, self._sw_type)
        cmd = "ls /opt/Diametriq/ 2> /dev/null | grep IMSDIA | grep -v tgz| wc -l"
        self._log.debug("App match host is %s", hosts)
        result = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        if int(result.strip()) != 1:
            self._log.debug("<")
            return False
        cmd = "ls /opt/Diametriq/ | grep IMSDIA | grep -v tgz"
        info = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        self._log.debug("Information derived from the %s node is %s",
                        hosts, str(info))
        self._log.debug("Expected Imsdia and version %s",
                        str(self._internal_version))
        if info == "":
            self._log.warning(
                "Imsdia-%s is not installed", str(self._internal_version))
            self._log.debug("<")
            return False
        imsdia_info = info.split('-')
        _imsdia_found_version = imsdia_info[2]
        self._log.debug("The software type is %s", str(self._sw_type))
        self.update_persist_data(
            infra_ref, "imsdia_found_version", _imsdia_found_version, self._sw_type)
        if self._internal_version == _imsdia_found_version:
            self._log.debug("Imsdia version matched -%s ",
                            str(self._internal_version))
        else:
            self._log.warning("imsdia %s not found, found version:%s are not matching",
                              self._internal_version, _imsdia_found_version)
            self._log.debug("<")
            return False

        lib_app_status = self._check_lib_apps(hosts)
        self._log.debug("<")
        return lib_app_status

    def _check_dss(self, hosts):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self.update_persist_data(
            infra_ref, "app_found_version", None, self._sw_type)
        cmd = "ls /opt/Diametriq/ 2> /dev/null | grep DSS | grep -v tgz | wc -l"
        self._log.debug("App match for host is %s", hosts)
        result = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        if int(result.strip()) != 1:
            return False
        cmd = "ls /opt/Diametriq/ | grep DSS | grep -v tgz"
        info = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        self._log.debug("Information derived from the %s node is %s",
                        hosts, str(info))
        self._log.debug("Expected DSS and version %s",
                        str(self._internal_version))
        if info == "":
            self._log.warning(
                "DSS-%s is not installed", str(self._internal_version))
            self._log.debug("<")
            return False
        dss_info = info.split('-')
        app_found_version = dss_info[1]
        self._log.debug("The software type is %s", str(self._sw_type))
        self.update_persist_data(
            infra_ref, "app_found_version", app_found_version, self._sw_type)
        if self._internal_version == app_found_version:
            self._log.debug("DSS version matched -%s ",
                            str(self._internal_version))
            self._log.debug("<")
            return True
        else:
            self._log.warning("DSS %s not found, found version:%s are not matching",
                              self._internal_version, app_found_version)
            self._log.debug("<")
            return False

    def _check_dsa(self, hosts):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self.update_persist_data(
            infra_ref, "app_found_version", None, self._sw_type)
        cmd = "ls /opt/Diametriq/ 2> /dev/null | grep DSA | grep -v tgz | wc -l"
        self._log.debug("App match for host is %s", hosts)
        result = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        if int(result.strip()) != 1:
            self._log.debug("<")
            return False
        cmd = "ls /opt/Diametriq/ | grep DSA | grep -v tgz"
        info = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        self._log.debug("Information derived from the %s node is %s",
                        hosts, str(info))
        self._log.debug("Expected DSA and version %s",
                        str(self._internal_version))
        if info == "":
            self._log.warning(
                "DSA-%s is not installed", str(self._internal_version))
            self._log.debug("<")
            return False
        dsa_info = info.split('-')
        app_found_version = dsa_info[2]
        self._log.debug("The software type is %s", str(self._sw_type))
        self.update_persist_data(
            infra_ref, "app_found_version", app_found_version, self._sw_type)
        if self._internal_version == app_found_version:
            self._log.debug("DSA version matched -%s ",
                            str(self._internal_version))
            self._log.debug("<")
            return True
        else:
            self._log.warning("DSA %s not found, found version:%s are not matching",
                              str(self._internal_version), str(app_found_version))
            self._log.debug("<")
            return False

    def _check_lib_apps(self, hosts):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        cmd = "ls /opt/Diametriq/ | grep {} | grep -v tgz | wc -l".format(
            self._internal_name.upper())
        result = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        if int(result.strip()) != 1:
            self._log.debug("<")
            return False
        cmd = "ls /opt/Diametriq/ | grep {} | grep -v tgz".format(
            self._internal_name.upper())
        self._log.debug("App match host is %s", hosts)
        self._log.debug("App match Command is %s", str(cmd))
        info = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        self._log.debug("Information derived from the %s node is %s",
                        hosts, str(info))
        self._log.debug("Expected %s application and version %s", str(
            self._internal_name), str(self._internal_version))
        if info == "":
            self._log.warning("Application %s-%s is not installed",
                              str(self._internal_name), str(self._internal_version))
            self._log.debug("<")
            return False
        module_info = info.split('-')
        app_found_version = module_info[2]
        self._log.debug("The software type is %s", str(self._sw_type))
        self.update_persist_data(
            infra_ref, "app_found_version", app_found_version, self._sw_type)
        if self._internal_version == app_found_version:
            self._log.debug("Found application %s-%s ",
                            str(self._internal_name), str(self._internal_version))
            cmd = "hostid"
            cur_hostid = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
                cmd, time_out=Constants.PEXPECT_TIMER)
            cur_hostid = str(cur_hostid.strip())
            self.update_persist_data(
                infra_ref, "cur_hostid", cur_hostid, self._sw_type)
            if int(self.host_id) != int(cur_hostid):
                self._log.warning("Hostid is %s on node %s",
                                  cur_hostid, hosts)
                self._log.debug("<")
                return False
            else:
                self._log.debug("<")
                return True
        else:
            self._log.warning(
                "Application %s not found, found version:%s",
                self._internal_version, app_found_version)
            self._log.debug("<")
            return False

    def _install_correct_imsdia(self, node_ip):
        """
        """
        self._log.debug(">")
        node_ip = self.get_node().get_management_ip()
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self._log.debug("The software type is %s", str(self._sw_type))
        _imsdia_found_version = self.get_persist_data(
            infra_ref, "imsdia_found_version", self._sw_type)
        app_found_version = self.get_persist_data(
            infra_ref, "app_found_version", self._sw_type)
        if _imsdia_found_version is None and app_found_version is None:
            self._log.info(
                "imsdia and  %s are not found, performing fresh"
                " installation on node - %s",
                self._internal_name, node_ip)
            self.install()
            self._log.debug("<")
            return True

        elif (_imsdia_found_version and app_found_version) and Utility.check_version_equal(
                _imsdia_found_version, self._internal_version) and Utility.check_version_equal(
                    app_found_version, self._internal_version):
            self._log.info(
                "imsdia and  %s are already installed to the configured"
                " version on node %s", self._internal_name, node_ip)
            cur_hostid = self.get_persist_data(
                infra_ref, "cur_hostid", self._sw_type)
            if int(self.host_id) != int(cur_hostid):
                self._log.info(
                    "Host id is not matching - resetting")
                self._log.debug(">")
                self.install()
            return True
        else:
            self._log.info(
                "imsdia and %s are already installed but version\
                configured is not matching on node - %s",
                self._internal_name, node_ip)
            self.uninstall()
            self.install()
            self._log.debug("<")
            return True

    def _install_correct_dss(self, node_ip):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self._log.debug("The software type is %s", str(self._sw_type))
        app_found_version = self.get_persist_data(
            infra_ref, "app_found_version", self._sw_type)
        if app_found_version is None:
            self._log.info(
                "DSS is not found, performing fresh"
                " installation on node - %s", node_ip)
            self.install()
            self._log.debug("<")
            return True

        elif Utility.check_version_equal(
                app_found_version, self._internal_version):
            self._log.info(
                "DSS is  already installed to the configured"
                " version on node %s", node_ip)
            # where we updating the cur host id for dss check during
            # app match
            cur_hostid = self.get_persist_data(
                infra_ref, "cur_hostid", self._sw_type)
            if int(self.host_id) != int(cur_hostid):
                self._log.info(
                    "Host id is not matching - resetting")
                self.install()
            self._log.debug("<")
            return True

        else:
            self._log.info(
                "DSS is already installed but version\
                configured is not matching on node - %s", node_ip)
            self.uninstall()
            self.install()
            self._log.debug("<")
            return True

    def _install_correct_dsa(self, node_ip):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self._log.debug("The software type is %s", str(self._sw_type))
        app_found_version = self.get_persist_data(
            infra_ref, "app_found_version", self._sw_type)
        if app_found_version is None:
            self._log.info(
                "DSA is not found, performing fresh"
                " installation on node - %s", node_ip)
            self.install()
            self._log.debug("<")
            return True

        elif Utility.check_version_equal(
                app_found_version, self._internal_version):
            self._log.info(
                "DSA is  already installed to the configured"
                " version on node %s", node_ip)
            # where we updating the cur host id for dsa check during
            # app match
            cur_hostid = self.get_persist_data(
                infra_ref, "cur_hostid", self._sw_type)
            if int(self.host_id) != int(cur_hostid):
                self._log.info(
                    "Host id is not matching - resetting")
                self.install()
            self._log.debug("<")
            return True

        else:
            self._log.info(
                "DSA is already installed but version\
                configured is not matching on node - %s", node_ip)
            self.uninstall()
            self.install()
            self._log.debug("<")
            return True

    def _install_imsdia_and_app(self, node_ip):
        """
        """
        self._log.debug(">")
        self._log.debug(
            "Installing IMSDIA from repo %s",
            self.get_imsdia_repo_path())
        #raise exception.MandatoryArgumentIsNotPresent("Cloud Platform")
        extra_vars = {
            'host': node_ip, 'rep_path': self.get_imsdia_repo_path(),
            'src_hostid_script_path': self._hostid_script_path,
            'src_licence_file': self._license_file_path,
            'host_id': self.host_id}
        tags = {'setup-diameter-stack'}
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(
                DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
        self._log.info(
            "Successfully installed the IMSDIA on node - %s", node_ip)
        self._log.debug(
            "Installing %s from repo %s", self._internal_name, self.get_repo_path())
        extra_vars['rep_path'] = self.get_repo_path()
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(
                DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
        self._log.info("Successfully installed the application imsdia")
        self._log.debug("<")

    def _install_dss(self, node_ip):
        """
        """
        self._log.debug(">")
        dss_repo_path = self.get_repo_path()
        self._log.debug(
            "Installing DSS from repo %s",
            dss_repo_path)
        extra_vars = {
            'host': node_ip, 'rep_path': dss_repo_path,
            'src_hostid_script_path': self._hostid_script_path,
            'src_licence_file': self._license_file_path,
            'host_id': self.host_id}
        tags = {'setup-distributed-stack'}
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(
                DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
        self._log.info(
            "Successfully installed the DSS on node - %s", node_ip)
        self._log.debug("<")

    def _install_dsa(self, node_ip):
        """
        """
        self._log.debug(">")
        dsa_repo_path = self.get_repo_path()
        self._log.debug(
            "Installing DSA from repo %s",
            dsa_repo_path)
        extra_vars = {
            'host': node_ip, 'rep_path': dsa_repo_path,
            'src_hostid_script_path': self._hostid_script_path,
            'src_licence_file': self._license_file_path,
            'host_id': self.host_id}
        tags = {'setup-distributed-application'}
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(
                DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
        self._log.info(
            "Successfully installed the DSA on node - %s", node_ip)
        self._log.debug("<")

    def _uninstall_imsdia_and_app(self, node_ip):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self._log.debug("The software type is %s", str(self._sw_type))
        app_found_version = self.get_persist_data(
            infra_ref, "app_found_version", self._sw_type)
        self._log.debug("Uninstalling %s-%s", self._internal_name,
                        app_found_version)
        extra_vars = {
            'host': node_ip,
            'package_name_req': self._internal_name,
            'version_req': self._internal_version,
            'host_id': self.host_id
        }
        tags = {'uninstall-diameter-stack'}
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(
                DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
        self._log.info(
            "Successfully uninstalled the application %s on node - %s",
            str(self._internal_name), node_ip)
        extra_vars['package_name_req'] = 'IMSDIA'
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(
                DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
        self._log.info("Successfully uninstalled the application imsdia")
        self._log.debug("<")

    def _uninstall_dss(self, node_ip):
        """
        """
        self._log.debug(">")
        infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
        self._log.debug("The software type is %s", str(self._sw_type))
        app_found_version = self.get_persist_data(
            infra_ref, "app_found_version", self._sw_type)
        self._log.debug("Uninstalling %s-%s", self._internal_name,
                        app_found_version)
        extra_vars = {
            'host': node_ip,
            'rep_url': self.get_repo_url(),
            'host_id': self.host_id
        }
        tags = {'uninstall-distributed-stack'}
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(
                DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
        self._log.info(
            "Successfully uninstalled the application %s on node - %s",
            str(self._internal_name), node_ip)
        self._log.debug("<")

    def setup_dia_inst(self, peer_type, inst_key, config_dict,
                       tt_config, mml=False):
        """
        This method sets up the prerequisites required to run Diamter and MML
        Args:
            peer_type: str
            inst_key: int
            config_dict: dict
            tt_config: dict
            mml: bool

        Returns:
            None
        Exception:
            Raises exception in case of failure

        """
        try:
            self._log.debug(">")
            self._sut_user_info_mgr = SUTUserInfoMgr(
                self.service_store_obj, self.service_store_obj.get_current_user_id(), self.service_store_obj.get_current_sut_name())
            self.product_path = self._sut_user_info_mgr.get_user_product_path()
            self._license_file_path = "{}/config/sut/load_test/its.lic".format(
                self.product_path)
            self._dia_template_path = "{}/config/sut/load_test/".format(
                self.product_path)
            self._ocs_template_path = "{}/config/sut/ocs_test/".format(
                self.product_path)
            self._tt_config_file = "{}/config/sut/load_test/tt_config.json".format(
                self.product_path)
            self._perf_config_file = "{}/config/sut/ocs_test/ctf_perf_config.json".format(
                self.product_path)
            node_ip = self.get_node().get_management_ip()
            if self._config.get_global_config("generate_test_configs").lower() == 'yes':
                self._generate_test_scripts(peer_type, inst_key, config_dict,
                                            tt_config, mml)
            self._log.info(
                "Creating %s instance %d on %s", self._name, inst_key, node_ip)
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.error(
                "Failed to setup %s for instance - %d on node %s",
                self._name, inst_key, node_ip)
            self._log.error("Failed to setup dia instance %s", str(ex))
            self._log.error("Traceback - %s", (traceback_))
            raise Exception(ex)

    def start_dia_inst(self, inst_key, tag, node_obj, inst_count, app_id=None, client_id=None):
        """
        This method starts all the diameter instance based on inst_key
        1. If inst_key is -1 then  it will start all the available instances in the node
        2. Else will start the mentioned instance

        Args:
            inst_key(int): If inst_key is -1, it will start all the available
                           instances in the node
            tag(str): tag can be "c" or "s"
            node_obj: node object
            inst_count(int): total instance count
            app_id : int or None
            client_id: int or None

        Returns:
                None
        """
        self._log.debug(">")
        self.get_config()
        self.service_store_obj.get_login_session_mgr_obj(
        ).create_session(node_obj, inst_count, tag)
        if inst_key == -1:
            for inst_key_ in range(1, inst_count+1):
                self._start_dia_instance(inst_key_, tag, node_obj, app_id,
                                         client_id)
            self._log.debug("<")
        else:
            self._start_dia_instance(
                inst_key, tag, node_obj, app_id, client_id)
            self._log.debug("<")

    def _start_dia_instance(self, instance_num, tag, node_obj, app_id, client_id):
        """Method used to start dia instance

        Args:
            instance_num(int): instance number
            tag(str) : tag can be 'c' or 's'
            node_obj
            app_id : int or None
            client_id: int or None

        Return:
            None
        """
        try:
            self._log.debug(">")
            node_ip = self.get_node().get_management_ip()
            self._log.info(
                "Starting %s instance %d on node - %s",
                self._name, instance_num, node_ip)
            self.service_store_obj.get_login_session_mgr_obj().execute_command('. {}config/Profile'.format(self._profile_path), tag,
                                                                               instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['.*$'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().execute_command(
                'cd {}'.format(self._bin_path), tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['.*$'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj(
            ).execute_command('chmod +x *', tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['.*$'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            if self._name == "DSS":
                self._start_dss_inst(instance_num, tag, node_obj)
            elif self._name == "DSA":
                self._start_dsa_inst(
                    instance_num, tag, node_obj, app_id, client_id)
            else:
                self._start_dia_stack_inst(instance_num, tag, node_obj)
            self._log.info(
                "%s instance %d is started successfully on node - %s.",
                self._name, instance_num, node_ip)
            self._log.debug("<")
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.error(
                "Failed to start %s instance - %d on node %s",
                self._name, instance_num, node_ip)
            self._log.error("Exception is %s", str(ex))
            self._log.error("Traceback - %s", (traceback_))
            raise Exception(ex)

    def _start_dss_inst(self, inst_num, tag, node_obj):
        """Method used to start distribute-stack dss instance

        Args:
            instance_num(int): instance number
            tag(str) : tag can be 'c' or 's'
            node_obj

        Return:
            None
        """
        self._log.debug(">")
        self.service_store_obj.get_login_session_mgr_obj().execute_command('./Run.server{}'.format(inst_num),
                                                                           tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().expected_match(
            ['Output sent to stdout'], Constants.PEXPECT_TIMER, tag, inst_num)
        self._log.debug("<")

    def _start_dsa_inst(self, inst_num, tag, node_obj, app_id, client_id):
        """Method used to start distribute-stack dsa instance

        Args:
            instance_num(int): instance number
            tag(str) : tag can be 'c' or 's'
            node_obj
            app_id : int
            client_id: int

        Return:
            None
        """
        self._log.debug(">")
        self.service_store_obj.get_login_session_mgr_obj().execute_command('./Run.server{}'.format(inst_num),
                                                                           tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().expected_match(
            ['Choice'], Constants.PEXPECT_TIMER, tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().execute_command(
            repr(1).encode('utf-8'), tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().expected_match(
            ['Choice'], Constants.PEXPECT_TIMER, tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().execute_command(
            repr(2).encode('utf-8'), tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().expected_match(
            ['Client ID'], Constants.PEXPECT_TIMER, tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().execute_command(repr(client_id).encode('utf-8'), tag,
                                                                           inst_num)
        self.service_store_obj.get_login_session_mgr_obj().expected_match(
            ['App ID'], Constants.PEXPECT_TIMER, tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().execute_command(repr(app_id).encode('utf-8'), tag,
                                                                           inst_num)
        self.service_store_obj.get_login_session_mgr_obj().expected_match(
            ['Acct AppId'], Constants.PEXPECT_TIMER, tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().execute_command(
            repr(0).encode('utf-8'), tag, inst_num)
        self.service_store_obj.get_login_session_mgr_obj().expected_match(
            ['Registered with server port:'], Constants.PEXPECT_TIMER, tag, inst_num)
        self._log.debug("<")

    def _check_ctf_ocs_connection(self, inst_num, tag):
        """Method used to check connection with server

        Args:
            inst_num(int): instance number
            tag(str) : tag can be 'c' or 's'

        Return:
            None
        """
        self._log.debug(">")
        node_name = self.get_node().get_name()
        self.service_store_obj.get_login_session_mgr_obj(
        ).create_session(self.get_node(), 1, "connection")
        node_config = self._config.get_test_case_config(node_name)
        remote_ip = node_config["PerfConfiguration"]["Config_dictionary"]["Default_config"]["remote_ip"]["SubnetIP"]
        remote_port = node_config["PerfConfiguration"]["Config_dictionary"]["Variable_config"]["remote_port"]["Value"]
        self.service_store_obj.get_login_session_mgr_obj().execute_command(
            #'netstat -anp | grep -i {}:{} | grep ESTABLISHED'.format(remote_ip, remote_port+inst_num),
            'netstat -anp | grep -i {}:{} | grep ESTABLISHED'.format(
                remote_ip, remote_port),
            "connection", 1)
        try:
            self.service_store_obj.get_login_session_mgr_obj().expected_match(
                ['ESTABLISHED'], Constants.PEXPECT_TIMER, "connection", 1)
            self._log.info(
                "Connection is successfully established between client and server")
            self._log.debug("<")
        except exception.TimeOutException as ex:
            self._log.error("Exception - %s", str(ex))
            self._log.debug("<")
            raise TimeOutException(
                "Connection is not established from client to server with subnet_ip-{} and port-{}".format(remote_ip, remote_port+inst_num))
        finally:
            self._log.debug(">")
            self.service_store_obj.get_login_session_mgr_obj().close_session("connection", 1)
            self._log.debug("<")

        self._log.debug("<")

    def _start_dia_stack_inst(self, inst_num, tag, node_obj):
        """Method used to start dia-stack instance

        Args:
            instance_num(int): instance number
            tag(str) : tag can be 'c' or 's'
            node_obj

        Return:
            None
        """
        self._log.debug(">")
        self._config = self.service_store_obj.get_current_test_case_configuration()
        host = self.get_node().get_management_ip()
        if tag == 'c':
            self._log.debug(">")
            if self._name == 'CTF':
                cmd = 'ipcs | grep -i key -A 1 |  head -2 | tail -1  | cut -d " " -f 2 | ipcrm -q `xargs -0`'
                self.service_store_obj.get_login_session_mgr_obj().execute_command(cmd, tag, inst_num)
                self.service_store_obj.get_login_session_mgr_obj().expected_match(['.*$'],
                                                                                  Constants.PEXPECT_TIMER, tag, inst_num)
            self.service_store_obj.get_login_session_mgr_obj().execute_command(
                './Run.client{}'.format(inst_num), tag, inst_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(
                ['Setup for Load Testing'], Constants.PEXPECT_TIMER, tag, inst_num)
            if self._name == 'CTF':
                self._check_ctf_ocs_connection(inst_num, tag)
            self._log.debug("<")
        else:
            self._log.debug(">")
            self.service_store_obj.get_login_session_mgr_obj().execute_command(
                './Run.server{}'.format(inst_num), tag, inst_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(
                ['Setup for Load Testing'], Constants.PEXPECT_TIMER, tag, inst_num)
            self._log.debug("<")

    def start_traffic(self, inst_key, tag, node_obj, inst_count, duration, burst_size, sleep):
        """
        This method start the traffic for the instance based on inst_key
        1. If inst_key is -1 then  it will start the
            traffic on all the available instances in the node
        2. Else will start the traffic only for mentioned instance

        Args:
            inst_key; int
            tag(str) : tag will be 'mml'
            node_obj
            inst_count(int): total instance count
            duration(int): If duration is -1 then it will run
                           infinite duration.
            burst_size: int
            sleep : int

        Returns:
            None
        """
        self._log.debug(">")
        self.get_config()
        self.service_store_obj.get_login_session_mgr_obj(
        ).create_session(node_obj, inst_count, tag)
        if duration == -1:
            duration = DiametriqConstants.TEST_INFINITY_DURATION
        if inst_key == -1:
            for inst_key_ in range(1, inst_count+1):
                self._start_traffic(inst_key_, tag, node_obj,
                                    duration, burst_size, sleep)
            self._log.debug("<")
        else:
            self._start_traffic(inst_key, tag, node_obj,
                                duration, burst_size, sleep)
            self._log.debug("<")

    def _start_traffic(self, instance_num, tag, node_obj, duration, burst_size, sleep):
        """Method used to start the traffic

        Args:
            inst_key; int
            tag(str) : tag will be 'mml'
            node_obj
            duration(int): If duration is -1 then it will run
                           infinite duration.
            burst_size: int
            sleep : int

        Returns:
            None
        """
        try:
            self._log.debug(">")
            node_ip = self.get_node().get_management_ip()
            self.service_store_obj.get_login_session_mgr_obj().execute_command('. {}/config/Profile'.format(self._profile_path), tag,
                                                                               instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['.*$'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().execute_command(
                'cd {}'.format(self._mml_path), tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['.*$'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().execute_command(
                './DBGConsole -socket -configFile dbc_console.client{}.ini'.format(instance_num), tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['>>'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj(
            ).execute_command('enStatistics', tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['>>'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self._log.info(
                "Enabled stack stats for %s inst - %d on node %s.",
                self._name, instance_num, node_ip)
            self.service_store_obj.get_login_session_mgr_obj().execute_command(
                'start-traffic {} {} {}'.format(duration, burst_size, sleep), tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['Test Started at'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self._log.info(
                "%s instance %d started traffic on node - %s.",
                self._name, instance_num, node_ip)
            self._log.debug("<")
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.error(
                "Failed to start traffic for %s instance %d on node - %s",
                instance_num, node_ip)
            self._log.error("Exception is -%s", str(ex))
            self._log.error("Traceback - %s", (traceback_))
            raise Exception(ex)

    def stop_dia_inst(self, inst_key, tag, node_obj, inst_count):
        """This method stops all the instance based on inst_key
            1. If inst_key is -1 then  it will stop all the available instances in
            the node
            2. Else will stop the mentioned instance

        Args:
            inst_key(int): If inst_key is -1, it will start all the available
                           instances in the node
            tag(str): tag can be "c" or "s"
            node_obj: node object
            inst_count(int): total instance count

        Returns:
            None
        """
        self._log.debug(">")
        for inum in range(inst_count, 0, -1):
            if tag == 'c':
                res = 'ps -elf | grep sample | grep demo.xml.client{} | grep -v grep | tr -s " " | cut -d " " -f 4'.format(
                    inum)
                self._kill_process_id(res)
                if self._name == 'CTF':
                    cmd = 'ipcs | grep -i key -A 1 |  head -2 | tail -1  | cut -d " " -f 2 | ipcrm -q `xargs -0`'
                    self.service_store_obj.get_login_session_mgr_obj().execute_command(cmd,
                                                                                       tag, inst_count)
                    self.service_store_obj.get_login_session_mgr_obj().expected_match(['.*$'],
                                                                                      Constants.PEXPECT_TIMER, tag, inst_count)
            else:
                if self._name != 'DSS' and self._name != 'DSA':
                    res = 'ps -elf | grep sample | grep demo.xml.server{} | grep -v grep | tr -s " " | cut -d " " -f 4'.format(
                        inum)
                    self._kill_process_id(res)
                else:
                    self._log.debug("<")
                    pass
        try:
            if inst_key == -1:
                for inst_key_ in range(1, inst_count+1):
                    self.service_store_obj.get_login_session_mgr_obj().close_session(tag, inst_key_)
                    self._log.info(
                        "%s instance %d is stopped sccessfully.", self._name, inst_key_)
            else:
                self.service_store_obj.get_login_session_mgr_obj().close_session(tag, inst_key)
                self._log.info("%s instance %d is stopped sccessfully.",
                               self._name, inst_key)
            self._log.debug("<")
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.info("%s instance %d is failed to stop.",
                           self._name, inst_key)
            self._log.error("%s instance %s is failed to stop.",
                            self._name, str(ex))
            self._log.error("Traceback - %s", (traceback_))
            raise Exception(ex)

    def _kill_process_id(self, res):
        """Method used to kill the process id

        Args:
            res: command to get the pid for respective instance

        Returns:
            None
        """
        self._log.debug(">")
        self.service_store_obj.get_login_session_mgr_obj(
        ).create_session(self.get_node(), 1, "kill_process")
        node_ip = self.get_node().get_management_ip()
        result = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            res, "kill_process", 1, time_out=Constants.PEXPECT_TIMER)
        pid_list = result.splitlines()
        for pid_ in pid_list:
            kill_pid = 'kill -9 {}'.format(pid_)
            self.service_store_obj.get_login_session_mgr_obj().perform_operation(
                kill_pid, "kill_process", 1, time_out=Constants.PEXPECT_TIMER)
        self.service_store_obj.get_login_session_mgr_obj(
        ).close_session("kill_process", 1)
        self._log.debug("<")

    def stop_traffic(self, inst_key, tag, node_obj, inst_count):
        """This method stop the traffic for the instance based on inst_key
            1. If inst_key is -1 then  it will stop the
            traffic on all the available instances in the node Then close_session
            for all mml_instance
            2. Else will stop the traffic only for mentioned instance and
            close_session for corressponding mml instance.

        Args:
            inst_key; int
            tag(str) : tag will be 'mml'
            node_obj
            inst_count(int): total instance count

        Return:
            None
        """
        self._log.debug(">")
        if inst_key == -1:
            for inst_key_ in range(1, inst_count+1):
                self._stop_traffic(inst_key_, tag, node_obj)
            self._log.debug("<")
        else:
            self._stop_traffic(inst_key, tag, node_obj)
            self._log.debug("<")

    def _stop_traffic(self, instance_num, tag, node_obj):
        """Method used to stop traffic

        Args:
            instnace_num(int): instance number
            tag(str): tag will be 'mml'
            node_obj

        Returns:
            None
        """
        try:
            self._log.debug(">")
            node_ip = self.get_node().get_management_ip()
            self.service_store_obj.get_login_session_mgr_obj().execute_command('stop-traffic',
                                                                               tag, instance_num)
            self.service_store_obj.get_login_session_mgr_obj().expected_match(['Traffic Generation Stopped'],
                                                                              Constants.PEXPECT_TIMER, tag, instance_num)
            self._log.info(
                "%s instance %d traffic is stopped successfully on"
                " node - %s.", self._name, instance_num, node_ip)
            self.service_store_obj.get_login_session_mgr_obj().close_session(tag, instance_num)
            self._log.debug("<")
        except Exception as ex:
            traceback_ = traceback.format_exc()
            self._log.info("%s instance %d is failed to stop traffic on node"
                           " - %s", self._name, instance_num, node_ip)
            self._log.error("Failed to stop trafic - {}".format(ex))
            self._log.error("Traceback %s", str(traceback_))
            raise Exception(ex)

    def app_match(self, host):
        """This method is used to check if app version is matching in INITIALIZING state

        Returns:
            True or False

        Raises:
            exception.NotImplemented
            :param : None
        """
        try:
            self._log.debug(">")
            self._sut_user_info_mgr = SUTUserInfoMgr(
                self.service_store_obj, self.service_store_obj.get_current_user_id(), self.service_store_obj.get_current_sut_name())
            self.product_path = self._sut_user_info_mgr.get_user_product_path()
            self._license_file_path = "{}/config/sut/load_test/its.lic".format(
                self.product_path)
            self._dia_template_path = "{}/config/sut/load_test/".format(
                self.product_path)
            self._ocs_template_path = "{}/config/sut/ocs_test/".format(
                self.product_path)
            self._tt_config_file = "{}/config/sut/load_test/tt_config.json".format(
                self.product_path)
            self._perf_config_file = "{}/config/sut/ocs_test/ctf_perf_config.json".format(
                self.product_path)
            self.service_store_obj.get_login_session_mgr_obj().create_session(self.get_node(),
                                                                              1)
            iptables_flush = "iptables -F"
            self.service_store_obj.get_login_session_mgr_obj().perform_operation(
                iptables_flush, time_out=Constants.PEXPECT_TIMER)
            infra_ref = self.service_store_obj.get_current_infra_profile().get_db_infra_profile_obj()
            self.update_persist_data(
                infra_ref, "cur_hostid", None, self._sw_type)
            hosts = [host]
            if self._name == "MME" or self._name == "HSS"\
                    or self._name == 'CTF' or self._name == 'OCS':
                self._log.debug("<")
                return self._check_imsdia(hosts)
            elif self._name == "DSS":
                self._log.debug("<")
                return self._check_dss(hosts)
            elif self._name == "DSA":
                self._log.debug("<")
                return self._check_dsa(hosts)
            else:
                self._log.debug("The software type is %s", str(self._sw_type))
                _imsdia_found_version = self.get_persist_data(
                    infra_ref, "imsdia_found_version", self._sw_type)
                self._log.warning("imsdia %s not found, found version:%s are not matching",
                                  self._internal_version, _imsdia_found_version)
                self._log.debug("<")
                return False
            # Removed the unreachable code
        except exception.ExecuteShellFailed as ex:
            self._log.debug("The software type is %s", str(self._sw_type))
            self.update_persist_data(
                infra_ref, "app_found_version", app_found_version, self._sw_type)
            _imsdia_found_version = None
            self.update_persist_data(
                infra_ref, "imsdia_found_version", _imsdia_found_version, self._sw_type)
            traceback_ = traceback.format_exc()
            self._log.error("app_match failed %s", str(ex))
            self._log.error("Traceback %s", str(traceback_))
            return False
        finally:
            self._log.debug("> finally block")
            self.service_store_obj.get_login_session_mgr_obj().close_session()
            self._log.debug("< finally block")

    def _get_python_version(self, host):
        """This method return the version of the python installed in given host.

        Args:
            host(str): ipaddress of the machine

        Returns:
            str: Version of the python.

        """
        self._log.debug(">")
        cmd = "python -c 'import sys; print((sys.version_info)<(3,0))'"
        info = self.service_store_obj.get_login_session_mgr_obj().execute_cmd_and_get_output(
            cmd, time_out=Constants.PEXPECT_TIMER)
        if info == "False":
            self._log.debug("<")
            return 'python3'
        self._log.debug("<")
        return 'python2'

    def install(self):
        """
        Overiding the base class method to install
        IMSDIA and application defined.

        Args:
            None
        Return:
            None
        """
        try:
            self._log.debug(">")
            node_ip = self.get_node().get_management_ip()
            if self._name == "DSS":
                version = self._get_python_version(node_ip)
                self.install_dependencies(version)
                self._install_dss(node_ip)
            elif self._name == "DSA":
                self._install_dsa(node_ip)
            else:
                version = self._get_python_version(node_ip)
                self.install_dependencies(version)
                self._install_imsdia_and_app(node_ip)

            self._log.debug("<")
        except exception.AnsibleException as ex:
            traceback_ = traceback.format_exc()
            self._log.error(
                "Installation failed on node %s - %s", node_ip, str(ex))
            self._log.error("Traceback %s", str(traceback_))
            raise InstallFailed("IMSDIA", str(ex))

    def install_dependencies(self, version='python2'):
        """
        """
        self._log.debug(">")
        self._log.debug("install_dependencies >")
        host = self.get_node().get_management_ip()
        node_name = self.get_node().get_name()
        if version == 'python2':
            pip_url = self.repo_mgr_client_obj.get_repo_path('python2-pip')
            pip_ = 'pip2'
            extra_vars = {
                'host': host,
                'src_path': [pip_url]
            }
            tags = {'install-rpm'}
            self.get_deployment_mgr_client_wrapper_obj().\
                run_playbook(RegalConstants.REGAL_PROD_DIR_NAME,
                             extra_vars, tags)
            self._log.debug("<")
        else:
            # python 3.6 is not supported now.
            self._log.debug("<")
            raise exception.PythonVersionNotSupported(host, node_name, version)

        dependency_files = []
        dependency_files.append(
            self.repo_mgr_client_obj.get_repo_path("pexpect"))
        dependency_files.append(
            self.repo_mgr_client_obj.get_repo_path("requests"))

        extra_vars = {
            'host': host,
            'source_path': dependency_files
        }
        tags = {'install-python-dependencies'}
        self.get_deployment_mgr_client_wrapper_obj().\
            run_playbook(RegalConstants.REGAL_PROD_DIR_NAME, extra_vars, tags)
        self._log.debug("<")

    def uninstall(self):
        """
        Overiding the base class method to uninstall
        IMSDIA and application defined.
        Args:
            None
        Return:
            None
        """
        try:
            self._log.debug(">")
            node_ip = self.get_node().get_management_ip()
            if self._name == "DSS":
                self._uninstall_dss(node_ip)
            elif self._name == "DSA":
                self._uninstall_dsa(node_ip)
            else:
                self._uninstall_imsdia_and_app(node_ip)

            self._log.debug("<")
        except exception.AnsibleException as ex:
            traceback_ = traceback.format_exc()
            self._log.error("Uninstall failed on node %s - %s",
                            node_ip, str(ex))
            self._log.error("Traceback %s", str(traceback_))
            raise UninstallFailed("IMSDIA", str(ex))

    def install_correct_version(self):
        """
        This method is invoked in CORRECTION state to take corrective actions
        Args:
            None
        Returns:
            bool
        """
        try:
            self._log.debug(">")
            self._sut_user_info_mgr = SUTUserInfoMgr(
                self.service_store_obj, self.service_store_obj.get_current_user_id(), self.service_store_obj.get_current_sut_name())
            self.product_path = self._sut_user_info_mgr.get_user_product_path()
            self._license_file_path = "{}/config/sut/load_test/its.lic".format(
                self.product_path)
            self._dia_template_path = "{}/config/sut/load_test/".format(
                self.product_path)
            self._ocs_template_path = "{}/config/sut/ocs_test/".format(
                self.product_path)
            self._tt_config_file = "{}/config/sut/load_test/tt_config.json".format(
                self.product_path)
            self._perf_config_file = "{}/config/sut/ocs_test/ctf_perf_config.json".format(
                self.product_path)
            self.service_store_obj.get_login_session_mgr_obj().create_session(self.get_node(),
                                                                              1)
            node_ip = self.get_node().get_management_ip()
            if self._name == "MME" or self._name == "HSS"\
                    or self._name == 'CTF' or self._name == 'OCS':
                return self._install_correct_imsdia(node_ip)
            elif self._name == "DSS":
                return self._install_correct_dss(node_ip)
            elif self._name == "DSA":
                return self._install_correct_dsa(node_ip)
            self._log.debug("<")
        except exception.RegalException as ex:
            traceback_ = traceback.format_exc()
            self._log.error(
                "Correction failed on node %s - %s ", node_ip, str(ex))
            self._log.error("Traceback %s", str(traceback_))
            self._log.debug("<")
            return False
        finally:
            self._log.debug("> finally block")
            self.service_store_obj.get_login_session_mgr_obj().close_session()
            self._log.debug("< finally block")

    def get_repo_path(self, package_name=None):
        """method used to get repo path for respective app.

        args:
            none

        returns:
            repo_path(str): repo path

        raise:
            exception
        """
        self._log.debug("> ")
        if self._name == "MME" or self._name == "HSS" or self._name == "DSS" or self._name == "DSA"\
                or self._name == 'CTF' or self._name == 'OCS':
            name = self._name
            version = self._version
        elif "_" in self._version:
            name = self._version.split("_")[0]
            version = self._version.split("_")[1]
        else:
            name = self._name
            version = self._version
        self._log.debug("Get repo path for app_name: \"%s\", version: \"%s\"",
                        str(name), str(version))
        try:
            if package_name:
                name = package_name
                if package_name == "IMSDIA":
                    version = version.split("_")[1]
            repo_path = \
                self.service_store_obj.get_repo_mgr_client_obj().get_repo_path(name, version)
            repo_path = os.path.abspath(repo_path)
            self._log.debug("< Returning repo path: %s", str(repo_path))
            self._log.debug("< ")
            return repo_path
        except Exception as ex:
            self._log.error("Not able to get repo path for %s-%s",
                            str(name), str(version))
            self._log.error(traceback.format_exc())
            self._log.debug("< ")
            raise ex
