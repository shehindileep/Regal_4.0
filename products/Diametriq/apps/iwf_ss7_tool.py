"""
Used for IWF SS7  class
"""
#import sys
#import os
#import traceback
##import regal.logger.logger as logger
##from regal.utility import GetRegal
##from Regal.regal_constants import Constants as RegalConstants
##from Diametriq.apps.iwf_base import IWFBase
#
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
#class IWFSS7Tool(IWFBase):
#    """
#    Wrapper class for IWFSS7Tool
#
#    """
#
#    def __init__(self, name, version):
#        super(IWFSS7Tool, self).__init__(name, version)
#        self._classname = self.__class__.__name__
#        self._log = logger.GetLogger(self._classname)
#        self._ss7_inst = {}
#        self._config = None
#        self._ss7_bin_path = None
#        self._ss7_template_path = os.path.abspath(
#            "../product/Diametriq/config/sut/ss7_tool/")
#        self._tcap_file = None
#        self._run_file = None
#        self._ss7_client_templates = {
#            "tcap_file": "tcap_iwf_itu.xml",
#            "run_file": "Run-SG-ITU"
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
#            self._ss7_bin_path = self.add_slash(
#                self._config.get_global_config("ss7_perf_bin_path"))
#            self._log.debug("Binary path configured - %s",
#                            str(self._ss7_bin_path))
#            self._log.debug("<")
#        except Exception as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Failed to get test configurations for node %s",
#                            self.get_node().get_management_ip())
#            self._log.error("Exception is - %s", str(ex))
#            self._log.error("Traceback - %s", (traceback_))
#            raise Exception(ex)
#
#    def _set_ss7_templates(self, inst_key):
#        """
#        This method decides the name of ss7 configuration file names based on the inst_key
#
#        Args:
#            inst_key: int
#
#        Returns:
#            ss7_templates: dict
#        Exception:
#            Raises exception in case of failure
#        """
#        try:
#            self._log.debug(">")
#            self._log.debug(
#                "Setting SS7 templates and configuration files for %d", inst_key)
#            ss7_templates = self._ss7_client_templates
#            self._tcap_file = "tcap_iwf_itu{}.xml".format(str(inst_key))
#            self._run_file = "Run-SG-ITU{}".format(str(inst_key))
#            self._log.debug(
#                "SS7  configuration files %s, %s", self._tcap_file, self._run_file)
#            self._log.debug("<")
#            return ss7_templates
#        except Exception as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Failed to _set_ss7_templates for instance %d on node %s",
#                            inst_key, self.get_node().get_management_ip())
#            self._log.error("Exception is - %s", str(ex))
#            self._log.error("Traceback - %s", (traceback_))
#            raise Exception(ex)
#
#    def _generate_tcap_script(self, config_dict, template_):
#        """
#        This method generate tcap_iwf_itu.xml files
#        Args:
#            config_dict: dict
#            template_:
#
#        Returns:
#            None
#        """
#        #node_ip = self.get_node().get_management_ip()
#        self._log.info(
#            "Genarating %s test configuration file %s",
#            self._name, str(self._tcap_file))
#
#        configuration = {
#            "ss7_perf_local_ip": config_dict["ss7_perf_local_ip"],
#            "ss7_perf_local_port": config_dict["ss7_perf_local_port"]
#            }
#        self._render_template(template_, configuration, self._tcap_file)
#        self._log.info(
#            "Genarated %s test configuration file %s",
#            self._name, str(self._tcap_file))
#
#    def _generate_run_script(self, template_):
#        """
#        This method generates test configurations  Run-SG-ITU
#        Args:
#            config_dict: dict
#            template_:
#
#        Returns:
#            None
#        """
#        #node_ip = self.get_node().get_management_ip()
#        self._log.info(
#            "Genarating %s test configuration file %s",
#            self._name, str(self._run_file))
#
#        configuration = {
#            "tcap_iwf_itu": self._tcap_file
#        }
#        self._render_template(template_, configuration, self._run_file)
#        self._log.info(
#            "Genarated %s test configuration file %s",
#            self._name, str(self._run_file))
#
#
#    def _generate_test_scripts(self, inst_key, config_dict):
#        """
#        This method generates test configurations for ss7 tool
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
#            ss7_templates = self._set_ss7_templates(inst_key)
#            for template_key in ss7_templates:
#                template_ = "{}{}".format(self.add_slash(
#                    self._ss7_template_path), ss7_templates[template_key])
#
#                if template_key == "tcap_file":
#                    self._generate_tcap_script(config_dict, template_)
#                elif template_key == "run_file":
#                    self._generate_run_script(template_)
#
#            extra_vars = {"host": node_ip,
#                          "destination_path": self._ss7_bin_path,
#                          "source_path": os.path.join(_temp_dir, '*')}
#            tags = {'copy-dir-files'}
#            GetRegal().GetAnsibleUtil().run_playbook(
#                RegalConstants.REGAL_PROD_DIR_NAME, extra_vars, tags)
#            self._delete_temp_dir()
#            cmd = "chmod 777 " + self._ss7_bin_path + "*"
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
#    def setup_ss7_inst(self, inst_key, config_dict):
#        """
#        This method sets up the prerequisites required to run SS7 tool
#        Args:
#            testcase: Test case object
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
#            self._log.error("Failed to setup ss7 instance %s", str(ex))
#            self._log.error("Traceback - %s", (traceback_))
#            raise Exception(ex)
#
#    def _exit(self):
#        """ Method is used to set back the ss7 instance dict to None
#
#        """
#        for inst_key, inst_list in list(self._ss7_inst.items()):
#            for inst in inst_list:
#                inst.agent.close()
#        self._ss7_inst = {}
