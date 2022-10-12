"""Used as IWF Dia plugin
"""
import sys
import os
import traceback

# regal libraries
#import regal.logger.logger as logger
#from regal.utility import GetRegal


# Product specific libraries
#from Regal.regal_constants import Constants as RegalConstants
#from Diametriq.apps.iwf_base import IWFBase
#IS_PY2 = sys.version_info < (3, 0)
#
#class UninstallFailed(Exception):
#    """ Exception will be thrown when Uninstallation is failed
#    """
#    def __init__(self, inst, error_msg):
#        Exception.__init__(self)
#        self._inst = inst
#        self._error_msg = error_msg
#
#    def __str__(self):
#        """ Return exception string. """
#        return "Failed to uninstall {} : {}".format(self._inst, self._error_msg)
#
#class InstallFailed(Exception):
#    """ Exception will be thrown when installation failed
#    """
#    def __init__(self, inst, error_msg):
#        Exception.__init__(self)
#        self._inst = inst
#        self._error_msg = error_msg
#
#    def __str__(self):
#        """ Return exception string. """
#        return "Failed to install {} : {}".format(self._inst, self._error_msg)
#
#
#class IWFDiameterTool(IWFBase):
#    """
#    Wrapper class for IWFDiameterTool
#
#    """
#
#    def __init__(self, name, version):
#        super(IWFDiameterTool, self).__init__(name, version)
#        self._classname = self.__class__.__name__
#        self._log = logger.GetLogger(self._classname)
#        self._config = None
#        self._dia_bin_path = None
#        self._dia_template_path = os.path.abspath(
#            "../product/Diametriq/config/sut/dia_tool/")
#        self._its_dia_file = None
#        self._run_file = None
#        self._demo_xml_file = None
#        self._dia_client_templates = {
#            "itsdia": "itsdiaclient.xml",
#            "run_file": "Run.client",
#            "demo_xml": "demo.xml.client"
#        }
#
#    def get_config(self):
#        """
#        This metod fetches the global configurations defined
#        in testcase_conf.json
#
#        Args:
#            None
#        Returns:
#            None
#        """
#        try:
#            self._log.debug(">")
#            self._config = GetRegal().GetCurrentTestConfiguration()
#            self._dia_bin_path = self.add_slash(
#                self._config.get_global_config("dia_perf_bin_path"))
#            self._log.debug("Biinary path configured - %s",
#                            str(self._dia_bin_path))
#            self._log.debug("<")
#        except Exception as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Failed to get test configurations for node %s",
#                            self.get_node().get_management_ip())
#            self._log.error("Exception is - %s", str(ex))
#            self._log.error("Traceback - %s", (traceback_))
#            raise Exception(ex)
#
#    def _set_dia_templates(self, inst_key):
#        """
#        This method decides the name of diameter configuration file names based on the inst_key
#
#        Args:
#            inst_key: int
#
#        Returns:
#            dia_templates: dict
#        Exception:
#            Raises exception in case of failure
#        """
#        try:
#            self._log.debug(">")
#            self._log.debug(
#                "Setting Diameter templates and configuration files for %d", inst_key)
#            dia_templates = self._dia_client_templates
#            self._its_dia_file = "itsdiaclient{}.xml".format(str(inst_key))
#            self._run_file = "Run.client{}".format(str(inst_key))
#            self._demo_xml_file = "demo.xml.client{}".format(str(inst_key))
#            self._log.debug(
#                "Diameter client configuration files %s, %s, %s",
#                self._its_dia_file, self._run_file, self._demo_xml_file)
#            self._log.debug("<")
#            return dia_templates
#        except Exception as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Failed to _set_dia_templates for instance %d on node %s",
#                            inst_key, self.get_node().get_management_ip())
#            self._log.error("Exception is - %s", str(ex))
#            self._log.error("Traceback - %s", (traceback_))
#            raise Exception(ex)
#
#    def _generate_itsdia_script(self, config_dict, template_):
#        """
#        This method generates test configurations for dbc_ini.
#        Args:
#            config_dict: dict
#            template_:
#
#        Returns:
#            None
#        """
#        self._log.info(
#            "Genarating %s test configuration file %s",
#            self._name, str(self._its_dia_file))
#
#        local_other_home_ip = ''
#        peer_other_home_ip = ''
#        sctp_parameters = {
#            "cookie_life": 60000,
#            "hb_on": "yes",
#            "hb_timeout": 10000,
#            "init_timeout": 3000,
#            "max_attempts": 16,
#            "max_in_streams": 12,
#            "num_out_streams": 12,
#            "recv_timeout": "0,0",
#            "send_timeout": "0,0",
#            "shutdown_timeout": 300,
#            "sack_delay": 5,
#            "asoc_max_attempt": 16,
#            "rto_max": 60000,
#            "rto_min": 2000,
#            "rto_initial": 3000,
#            "send_buf_size": 102400,
#            "recv_buf_size": 102400,
#            "pathmaxrxt": 16
#        }
#
#        if config_dict["transport_type"].lower() == "sctp":
#            sctp_begin_comm = ""
#            sctp_end_comm = ""
#            if 'local_other_home_ip' in config_dict:
#                local_other_home_ip = '<OtherHome serverIpAddr = "{}"/>'.format(
#                    config_dict['local_other_home_ip'])
#            if 'peer_other_home_ip' in config_dict:
#                peer_other_home_ip = '<OtherHome serverIpAddr = "{}"/>'.format(
#                    config_dict['peer_other_home_ip'])
#            if 'sctp_parameters' in config_dict:
#                sctp_parameters.update(config_dict['sctp_parameters'])
#
#        elif config_dict["transport_type"].lower() == "tcp":
#            sctp_begin_comm = "!--"
#            sctp_end_comm = "--"
#
#        self._log.debug("SCTP parameters {}".format(sctp_parameters))
#
#        configuration = {
#            "local_host": config_dict["local_host"],
#            "local_realm": config_dict["local_realm"],
#            "transport_type": config_dict["transport_type"],
#            "local_ip": config_dict["local_ip"],
#            "local_port": config_dict["local_port"],
#            "local_other_home_ip": local_other_home_ip,
#            "peer_other_home_ip": peer_other_home_ip,
#            "remote_host": config_dict["remote_host"],
#            "remote_realm": config_dict["remote_realm"],
#            "remote_ip": config_dict["remote_ip"],
#            "remote_port": config_dict["remote_port"],
#            "sctp_begin_comm": sctp_begin_comm,
#            "sctp_end_comm": sctp_end_comm,
#            "cookie_life": sctp_parameters['cookie_life'],
#            "hb_on": sctp_parameters['hb_on'],
#            "hb_timeout": sctp_parameters['hb_timeout'],
#            "init_timeout": sctp_parameters['init_timeout'],
#            "max_attempts": sctp_parameters['max_attempts'],
#            "max_in_streams": sctp_parameters['max_in_streams'],
#            "num_out_streams": sctp_parameters['num_out_streams'],
#            "recv_timeout": sctp_parameters['recv_timeout'],
#            "send_timeout": sctp_parameters['send_timeout'],
#            "shutdown_timeout": sctp_parameters['shutdown_timeout'],
#            "sack_delay": sctp_parameters['sack_delay'],
#            "asoc_max_attempt": sctp_parameters['asoc_max_attempt'],
#            "rto_max": sctp_parameters['rto_max'],
#            "rto_min": sctp_parameters['rto_min'],
#            "rto_initial": sctp_parameters['rto_initial'],
#            "send_buf_size": sctp_parameters['send_buf_size'],
#            "recv_buf_size": sctp_parameters['recv_buf_size'],
#            "pathmaxrxt": sctp_parameters['pathmaxrxt']
#            }
#        self._render_template(template_, configuration, self._its_dia_file)
#        self._log.info(
#            "Genarated %s test configuration file %s",
#            self._name, str(self._its_dia_file))
#
#    def _generate_run_script(self, config_dict, template_):
#        """
#        This method generates test configurations for dbc_ini file.
#        Args:
#            config_dict: dict
#            template_:
#
#        Returns:
#            None
#        """
#        self._log.info(
#            "Genarating %s test configuration file %s",
#            self._name, str(self._run_file))
#
#        configuration = {
#            "sample_binary": config_dict["sample_binary"],
#            "local_host": config_dict["local_host"],
#            "local_realm": config_dict["local_realm"],
#            "dest_host": config_dict["dest_host"],
#            "dest_realm": config_dict["dest_realm"],
#            "demo_xml_file": self._demo_xml_file
#        }
#        self._render_template(template_, configuration, self._run_file)
#        self._log.info(
#            "Genarated %s test configuration file %s",
#            self._name, str(self._run_file))
#
#    def _generate_demo_xml_script(self, template_):
#        """
#        This method generates test configurations for dbc_ini.
#        Args:
#            config_dict: dict
#            template_:
#            mml (bool):
#
#        Returns:
#            None
#        """
#        self._log.info(
#            "Genarating %s test configuration file %s", self._name, str(self._demo_xml_file))
#        configuration = {
#            "its_dia_file": self._its_dia_file
#        }
#        self._render_template(template_, configuration, self._demo_xml_file)
#        self._log.info(
#            "Genarated %s test configuration file %s", self._name, str(self._demo_xml_file))
#
#
#    def _generate_test_scripts(self, inst_key, config_dict):
#        """
#        This method generates test configurations for diameter application.
#        Args:
#            inst_key: int
#            config_dict: dict
#
#        Returns:
#            None
#        Exception:
#            Raises exception in case of failure
#
#        """
#        try:
#            self._log.debug(">")
#            _temp_dir = self.create_temp_dir()
#            node_ip = self.get_node().get_management_ip()
#            self._log.info(
#                "Genarating %s test configuratios for instance - %d on node %s",
#                self._name, inst_key, node_ip)
#
#            dia_templates = self._set_dia_templates(inst_key)
#            for template_key in dia_templates:
#                template_ = "{}{}".format(self.add_slash(
#                    self._dia_template_path), dia_templates[template_key])
#
#                if template_key == "itsdia":
#                    self._generate_itsdia_script(config_dict, template_)
#                elif template_key == "run_file":
#                    self._generate_run_script(config_dict, template_)
#                elif template_key == "demo_xml":
#                    self._generate_demo_xml_script(template_)
#
#            extra_vars = {"host": node_ip,
#                          "destination_path": self._dia_bin_path,
#                          "source_path": os.path.join(_temp_dir, '*')}
#            tags = {'copy-dir-files'}
#            GetRegal().GetAnsibleUtil().run_playbook(
#                RegalConstants.REGAL_PROD_DIR_NAME, extra_vars, tags)
#            self._delete_temp_dir()
#            cmd = "chmod 777 " + self._dia_bin_path + "*"
#            GetRegal().GetAnsibleUtil().execute_shell(cmd, node_ip)
#            self._log.info(
#                "Generated and copied the %s configurations to %s", self._name, node_ip)
#            self._log.debug("<")
#        except Exception as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error(
#                "Failed to generate test configuration files for instance\
#                - %d on node %s", inst_key, node_ip)
#            self._log.error("Exception is - %s", str(ex))
#            self._log.error("Traceback - %s", (traceback_))
#            raise Exception(ex)
#
#
#    def setup_dia_inst(self, inst_key, config_dict):
#        """
#        This method sets up the prerequisites required to run Diamter
#        Args:
#            inst_key: int
#            config_dict: dict
#
#        Returns:
#            None
#        Exception:
#            Raises exception in case of failure
#
#        """
#        try:
#            self._log.debug(">")
#            node_ip = self.get_node().get_management_ip()
#            self._generate_test_scripts(inst_key, config_dict)
#            self._log.debug("<")
#        except Exception as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error(
#                "Failed to setup %s for instance - %d on node %s",
#                self._name, inst_key, node_ip)
#            self._log.error("Failed to setup dia instance %s", str(ex))
#            self._log.error("Traceback - %s", (traceback_))
#            raise Exception(ex)
#
#
