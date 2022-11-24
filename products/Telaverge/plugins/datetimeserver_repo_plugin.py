import re
import os
import tarfile
import sys
import subprocess
from distutils.version import LooseVersion
import zipfile

# from regal_controller.regal_controller.utility import GetServiceStore
from regal_lib.repo_manager.repo_plugin_interfaces import RepoPlugin
import regal_lib.corelib.custom_exception as exception
from Telaverge.telaverge_constans import Constants as TVConstants

class DatetimeserverRepoPlugin(RepoPlugin):
    '''# Add doc string '''
    _user_string = "Datetimeserver_repo_plugin"

    def __init__(self, service_store_obj):
        self.service_store_obj = service_store_obj
        logger = self.service_store_obj.get_log_mgr_obj()
        self._log = logger.get_logger(self.__class__.__name__)
        self._log.debug(">")
        self._log.debug("<")

    def get_package_details(self, package_name, package_path):
        '''
        This method will extract the Name and Version of the build provided in package_name
        Args:
            package_name(str): File name of the package
            package_path(str): package path

        Returns:

        '''
        self._log.debug(">")
        package_details = {"Name": None, "Version": None, "Type": None}
        if re.search("datetime_server-*", package_name):
            p = re.compile("datetime_server-(.*).tar.gz")
            res = p.match(package_name)
            package_details['Version'] = str(res.group(1))
            package_details['Name'] = "datetime_server"
            package_details['Type'] = TVConstants.APPLICATION
        self._log.debug("<")
        return package_details

