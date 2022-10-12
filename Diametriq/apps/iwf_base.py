"""
This module is designed to provide interface between legacy
plugins (plugin_MML and plugin_dia_app) and the wrapper
"""
#import sys
#import os
#import traceback
#import tempfile
#import shutil
#
## regal libraries
#"""
#import regal.logger.logger as logger
#from regal.utility import Utility, GetRegal
#from regal.helper.common_helper import CommonHelper
#import regal.custom_exception as exception
#
## Product specific libraries
#from Diametriq.diametriq_constants import Constants as DiametriqConstants
#from Diametriq.apps.diametriq_apps_util import DiametriqAppsUtil
#from Regal.apps.appbase import AppBase
#"""
#IS_PY2 = sys.version_info < (3, 0)
#
#class InvalidConfiguration(Exception):
#    """ Exception will be thrown when configuration is invalid
#    """
#    def __init__(self, err_msg):
#        super(InvalidConfiguration, self).__init__()
#        self._error_msg = err_msg
#
#    def __str__(self):
#        """ Return exception string. """
#        return "{}".format(self._error_msg)
#
#
#class UninstallFailed(Exception):
#    """ Exception will be thrown when Uninstallation is failed
#    """
#    def __init__(self, inst, error_msg):
#        super(UninstallFailed, self).__init__()
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
#        super(InstallFailed, self).__init__()
#        self._inst = inst
#        self._error_msg = error_msg
#
#    def __str__(self):
#        """ Return exception string. """
#        return "Failed to install {} : {}".format(self._inst, self._error_msg)
#
#class IWFStartStatsFailed(Exception):
#    """ Exception will be thrown when iwf start is failed
#    """
#    def __init__(self, node_name, err_msg):
#        super(IWFStartStatsFailed, self).__init__()
#        self._error_msg = err_msg
#        self._node_name = node_name
#
#    def __str__(self):
#        """ Return exception string. """
#        return "{} {}".format(self._error_msg, self._node_name)
#
#class IWFStartStopFailed(Exception):
#    """ Exception will be thrown when iwf start is failed
#    """
#    def __init__(self, node_name, err_msg):
#        super(IWFStartStopFailed, self).__init__()
#        self._error_msg = err_msg
#        self._node_name = node_name
#
#    def __str__(self):
#        """ Return exception string. """
#        return "{} {}".format(self._error_msg, self._node_name)
#
#class IWFBase(AppBase, DiametriqAppsUtil):
#    """
#    Wrapper class for IWF performance tool.
#    """
#
#    def __init__(self, name, version):
#        super(IWFBase, self).__init__(name, version)
#        self._classname = self.__class__.__name__
#        self._log = logger.GetLogger(self._classname)
#        self._dia_inst = {}
#        self._iwf_found_version = None
#        try:
#            self._iwf_rep_url = GetRegal().GetRepoMgr().get_repo_url(self._name)
#        except exception.BuildNotFoundInRepo as ex:
#            self._iwf_rep_url = None
#        try:
#            self._iwf_rep_path = GetRegal().GetRepoMgr().get_repo_path(self._name)
#        except exception.BuildNotFoundInRepo as ex:
#            self._iwf_rep_path = None
#        self.cur_hostid = None
#        self.host_id = "00000000"
#        self._hostid_script_path = os.path.abspath(
#            "../config/change_host_id")
#        self._license_file_path = os.path.abspath(
#            "../product/Diametriq/config/sut/its.lic")
#        self._iwf_config_file = os.path.abspath(
#            "../product/Diametriq/config/sut/iwf/install_default_iwf.cnf")
#        self._servicename = None
#        self._repo_url = None
#
#    def app_match(self, host):
#        """This method is used to check if app version is matching in INITIALIZING state
#
#        Returns:
#            True or False
#
#        Raises:
#            exception.NotImplemented
#            :param : None
#        """
#        try:
#            hosts = [host]
#            cmd = "ls -lrt /opt/diametriq/iwf | grep iwf | cut -d \">\" -f 2 | cut -d \"/\" -f 4 | cut -d \"-\" -f 2,3| wc -l"
#            self._log.debug("App match host is %s", host)
#            result = GetRegal().GetAnsibleUtil().execute_shell(cmd, hosts)
#            if int(result.strip()) == 0:
#                return False
#            cmd = "ls -lrt /opt/diametriq/iwf | grep iwf | cut -d \">\" -f 2 | cut -d \"/\" -f 4 | cut -d \"-\" -f 2,3"
#            info = GetRegal().GetAnsibleUtil().execute_shell(cmd, hosts)
#            self._log.debug("Information derived from the %s node is %s",
#                            host, str(info))
#            self._log.debug("Expected name and version %s, %s",
#                            str(self._name), str(self._version))
#            if info == "":
#                self._log.warning(
#                    "iwf-%s is not installed", str(self._version))
#                return False
#            self._iwf_found_version = info
#            if self._version == self._iwf_found_version:
#                self._log.debug("iwf version matched -%s ",
#                                str(self._version))
#                cmd = "hostid"
#                self.cur_hostid = GetRegal().GetAnsibleUtil().execute_shell(cmd, hosts)
#                self.cur_hostid = str(self.cur_hostid.strip())
#                if int(self.host_id, 16) != int(self.cur_hostid, 16):
#                    self._log.warning("Hostid is %s on node %s",
#                                      self.cur_hostid, host)
#                    return False
#                else:
#                    return True
#
#            else:
#                self._log.warning("iwf %s not found, found version:%s are not matching",
#                                  self._version, self._iwf_found_version)
#                return False
#
#        except exception.ExecuteShellFailed as ex:
#            self._iwf_found_version = None
#            self.cur_hostid = None
#            traceback_ = traceback.format_exc()
#            self._log.error("app_match failed %s", str(ex))
#            self._log.error("Traceback %s", str(traceback_))
#            return False
#
#    def _install_iwf(self):
#        """
#        Overiding the base class method to install
#        IWF defined.
#
#        Args:
#            None
#        Return:
#            None
#        """
#        try:
#            node_ip = self.get_node().get_management_ip()
#            cmd = "netstat -i|grep -v lo|tr -s \" \" | cut -d \" \" -f 1 |head -3 | tail -1"
#            interface_name = GetRegal().GetAnsibleUtil().execute_shell(cmd, node_ip)
#            cmd1 = "hostname"
#            hostname = GetRegal().GetAnsibleUtil().execute_shell(cmd1, node_ip)
#            configuration = {
#                "interface_name": interface_name,
#                "hostname": hostname
#            }
#            _temp_dir = self.create_temp_dir()
#            latest_iwf_conf = self._render_template(self._iwf_config_file, configuration,
#                                                    "install_default_iwf.cnf")
#
#            self._log.debug(
#                "Installing IWF from repo %s",
#                self._iwf_rep_path)
#            extra_vars = {
#                'host': node_ip, 'rep_path': self._iwf_rep_path,
#                'src_hostid_script_path': self._hostid_script_path,
#                'src_licence_file': self._license_file_path,
#                'host_id': self.host_id,
#                'config_src_path': latest_iwf_conf}
#            tags = {'install-iwf'}
#            self.ansible().run_playbook(DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
#            self._log.info(
#                "Successfully installed the IWF on node - %s", node_ip)
#            self._delete_temp_dir()
#        except exception.AnsibleException as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Installation failed on node %s - %s", node_ip, str(ex))
#            self._log.error("Traceback %s", str(traceback_))
#            raise InstallFailed("IWF", str(ex))
#
#    def _uninstall_iwf(self):
#        """
#        Overiding the base class method to uninstall
#        IWF defined.
#        Args:
#            None
#        Return:
#            None
#        """
#        try:
#            node_ip = self.get_node().get_management_ip()
#            self._log.debug("Uninstalling %s-%s", self._name,
#                            self._version)
#            extra_vars = {
#                'host': node_ip,
#                'rep_url': self.get_repo_url(),
#                'host_id': self.host_id
#            }
#            tags = {'uninstall-iwf'}
#            self.ansible().run_playbook(DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
#            self._log.info(
#                "Successfully uninstalled the application %s on node - %s",
#                str(self._name), node_ip)
#            extra_vars['rep_url'] = self._iwf_rep_url
#            self.ansible().run_playbook(DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
#            self._log.info("Successfully uninstalled the application IWF")
#        except exception.AnsibleException as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Uninstall failed on node %s - %s", node_ip, str(ex))
#            self._log.error("Traceback %s", str(traceback_))
#            raise UninstallFailed("IWF", str(ex))
#
#    def install_correct_version(self):
#        """
#        This method is invoked in CORRECTION state to take corrective actions
#        Args:
#            None
#        Returns:
#            bool
#        """
#        try:
#            node_ip = self.get_node().get_management_ip()
#            if self._iwf_found_version is None:
#                self._log.info(
#                    " %s are not found, performing fresh"\
#                    " installation on node - %s",
#                    self._name, node_ip)
#                self._install_iwf()
#                return True
#            elif CommonHelper.check_version_equal(
#                    self._iwf_found_version, self._version):
#                self._log.info(
#                    "%s are already installed to the configured"\
#                    " version on node %s", self._name, node_ip)
#                if int(self.host_id, 16) != int(self.cur_hostid, 16):
#                    self._log.info(
#                        "Host id is not matching - resetting")
#                    self._install_iwf()
#                return True
#            elif CommonHelper.check_version(self._iwf_found_version,
#                                            self._version):
#                self._log.info(
#                    "Lesser version %s is found in target node %s but version\
#                    configured is - %s", str(self._iwf_found_version),
#                    node_ip, str(self._version))
#                self._upgrade_iwf()
#            else:
#                self._log.info(
#                    "Higher version %s is found in target node %s but version\
#                    configured is - %s", str(self._iwf_found_version),
#                    node_ip, str(self._version))
#                self._uninstall_iwf()
#                self._install_iwf()
#                return True
#        except exception.RegalException as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Correction failed on node %s - %s ", node_ip, str(ex))
#            self._log.error("Traceback %s", str(traceback_))
#            return False
#
#    def generate_and_upload_iwf_configuration(self, template_src, itu_xml_file, vars_dict):
#        """This method is used to generate and copy sql_dump file to target
#        node
#
#        Args:
#            template_src(str): sql-dump template file path
#            vars_dict(dict): dictionary which contains default and variable
#            config info
#
#        Returns:
#            None
#        """
#        self._log.debug("Creating iwf sql-dump configuration from template %s", template_src)
#        host = self.get_node().get_management_ip()
#        template_src_path = os.path.abspath(template_src)
#        iwf_itu_src_path = os.path.abspath(itu_xml_file)
#        extra_vars = {'host': host, 'template_src_path': template_src_path, "iwf_itu_src_path": iwf_itu_src_path}
#        extra_vars.update(vars_dict)
#        self._log.debug("generate_and_upload_configuration: %s", str(extra_vars))
#        tags = {'apply-iwf-config'}
#        self.ansible().run_playbook(DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME,
#                                    extra_vars, tags)
#        self._log.info(
#            "Uploaded iwf sql-dump configuration successfully on node %s",
#            str(self.get_node().get_name()))
#
#    def start_iwf(self):
#        """
#        Method to start IWF node
#        """
#        host = self.get_node().get_management_ip()
#        cmd = "service dre status"
#        result = GetRegal().GetAnsibleUtil().execute_shell(cmd, host)
#        if "not" in result:
#            cmd1 = "service dre start"
#            GetRegal().GetAnsibleUtil().execute_shell(cmd1, host)
#            result2 = GetRegal().GetAnsibleUtil().execute_shell(cmd, host)
#            if "is running" in result2:
#                self._log.debug("service dre started successfully")
#            else:
#                raise IWFStartStopFailed(self._node_name, "service dre status")
#
#    def stop_iwf(self):
#        """
#        Method to stop IWF node
#        """
#        host = self.get_node().get_management_ip()
#        cmd = "service dre status"
#        result = GetRegal().GetAnsibleUtil().execute_shell(cmd, host)
#        if not "not" in result:
#            cmd1 = "service dre stop"
#            GetRegal().GetAnsibleUtil().execute_shell(cmd1, host)
#            result = GetRegal().GetAnsibleUtil().execute_shell(cmd, host)
#            if "is not running" in result:
#                self._log.debug("service dre stopped successfully")
#            else:
#                raise IWFStartStopFailed(self._node_name, "service dre status")
#
#    def start_stats(self):
#        """
#        Method to start stats on IWF node
#        """
#        node_ip = self.get_node().get_management_ip()
#        self._servicename = "iwfmsgstats"
#        try:
#            extra_vars = {
#                'host': node_ip,
#                'service': self._servicename,
#                'operation': 'start',
#                }
#            tags = {'manage-service'}
#            self.ansible().run_playbook(DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
#            self._log.info(
#                "Successfully started stats on node - %s", node_ip)
#        except exception.AnsibleException as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Stats start failed on node %s - %s", node_ip, str(ex))
#            self._log.error("Traceback %s", str(traceback_))
#            raise IWFStartStatsFailed(self._node_name, "service iwfmsgstats start")
#
#    def stop_stats(self):
#        """
#        Method to stop stats on IWF node
#        """
#        node_ip = self.get_node().get_management_ip()
#        self._servicename = "iwfmsgstats"
#        try:
#            extra_vars = {
#                'host': node_ip,
#                'service': self._servicename,
#                'operation': 'stop',
#                }
#            tags = {'manage-service'}
#            self.ansible().run_playbook(DiametriqConstants.DIAMETRIQ_PROD_DIR_NAME, extra_vars, tags)
#            self._log.info(
#                "Successfully stopped stats on node - %s", node_ip)
#        except exception.AnsibleException as ex:
#            traceback_ = traceback.format_exc()
#            self._log.error("Stats stop failed on node %s - %s", node_ip, str(ex))
#            self._log.error("Traceback %s", str(traceback_))
#            raise IWFStartStatsFailed(self._node_name, "service iwfmsgstats stop")
#
