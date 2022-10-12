"""
This module comprise of a class with common app tool functions shared between products
Diameter and Diametriq.
"""

import os
import tempfile
import shutil

# regal libraries
from regal_lib.corelib.common_utility import Utility
import regal_lib.corelib.custom_exception as exception
from regal_lib.repo_manager.repo_mgr_client import RepoMgrClient

class DiametriqAppsUtil(object):
    """
    Class comprises of app functions that are commonly used by both
    Diameter and Diametriq products
    """
    def __init__(self, service_store_obj, name, version):
        class_name = self.__class__.__name__
        self.service_store_obj = service_store_obj
        self._log_mgr_obj = self.service_store_obj.get_log_mgr_obj()
        self._log = self._log_mgr_obj.get_logger(class_name)
        self.repo_mgr_client_obj = RepoMgrClient(self.service_store_obj)
        self._version = version
        self._name = name
        self._temp_dir = None

    def add_slash(self, path):
        """
        Adds '/' to the path if not present
        Args:
            path: str
        Return:
            path: str
        """
        if path[-1] == "/":
            path = path
        else:
            path = "{}{}".format(path, "/")
        return path

    def get_repo_url(self, package_name=None):
        """
        This method used to fetch repo_url of the given package name.
        """
        if "_" in self._version:
            name = self._version.split("_")[0]
            version = self._version.split("_")[1]
        else:
            name = self._name
            version = self._version
        try:
            if package_name:
                name = package_name
            #must include get_repo_url in repo_mgr_client
            _repo_url = self.repo_mgr_client_obj.get_repo_url(name,
                                                             version)
            return _repo_url
        except exception.BuildNotFoundInRepo as ex:
            self._log.critical('%s', str(ex))
            raise ex

    def create_temp_dir(self):
        """
        This method used to create temporary directory
        """
        self._temp_dir = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(__file__)))
        os.chmod(self._temp_dir, 0o775)
        return self._temp_dir

    def _delete_temp_dir(self):
        """
        This method used to delete temporary directory
        """
        shutil.rmtree(self._temp_dir)

    def _render_template(self, template, config_dict, dst_fname):
        template_obj = Utility.get_jinja2_template_obj(template)
        configs = template_obj.render(config_dict)
        file_name = Utility.join_path(self._temp_dir, dst_fname)
        Utility.write_to_file(file_name, configs)
        self._log.debug("Generated the configuration file under {}".format(file_name))
        return file_name
