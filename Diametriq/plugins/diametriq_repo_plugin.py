import re
from distutils.version import LooseVersion

from regal_lib.repo_manager.repo_plugin_interfaces import RepoPlugin
from Diametriq.diametriq_constants import Constants as DiametriqConstants


class DiametriqRepoPlugin(RepoPlugin):
    '''# Add doc string '''
    _user_string = "Diametriq_repo_plugin"

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
            dict: Name and Version of the package

        '''
        self._log.debug(">")
        package_details = {"Name": None, "Version": None}
        if "iwf-ss7" in package_name:
            #iwf package
            p = re.compile("iwf-ss7-(.*).bin")
            res = p.match(package_name)
            package_details['Version'] = str(res.group(1))
            package_details['Name'] = "iwf-ss7"
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif "iwf-dia" in package_name:
            #iwf package
            p = re.compile("iwf-dia-(.*).bin")
            res = p.match(package_name)
            package_details['Version'] = str(res.group(1))
            package_details['Name'] = "iwf-dia"
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif "iwf" in package_name:
            #iwf package
            p = re.compile("iwf-(.*).bin")
            res = p.match(package_name)
            package_details['Version'] = str(res.group(1))
            package_details['Name'] = "iwf"
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif re.search(".*\.rpm$", package_name):
            package_details = self._get_rpm_details(package_path)

        self._log.debug("<")
        return package_details


class NNRepoPlugin(RepoPlugin):
    """Base class for NNOS"""
    _user_string = "nn_repo_plugin"

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
        if "IMSDIA" in package_name:
            p = re.compile("(.*)-GA-(.*)-NRD-x86_64.linux-gnu-g\+\+.tgz")
            res = p.match(package_name)
            package_details['Version'] = str(res.group(2))
            package_details['Name'] = str(res.group(1))
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif "S6A-R" in package_name:
            p = re.compile("(.*)-(.*)-x86_64.linux-gnu-g\+\+.tgz")
            res = p.match(package_name)
            package_details['Version'] = "{}_{}".format(str(res.group(1)), str(res.group(2)))
            package_details['Name'] = ["MME", "HSS"]
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif "GY-R" in package_name:
            p = re.compile("(.*)-(.*)-x86_64.linux-gnu-g\+\+.tgz")
            res = p.match(package_name)
            package_details['Version'] = "{}_{}".format(str(res.group(1)), str(res.group(2)))
            package_details['Name'] = "MME"
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif "DSS" in package_name:
            p = re.compile("(.*)-(.*)-NRD-(.*).linux-gnu-g\+\+")
            res = p.match(package_name)
            package_details['Version'] = "{}_{}".format(str(res.group(1)), str(res.group(2)))
            package_details['Name'] = str(res.group(1))
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif "DSA" in package_name:
            p = re.compile("(.*)-(.*)-(.*)-NRD-(.*).linux-gnu-g\+\+")
            res = p.match(package_name)
            package_details['Version'] = "{}-{}_{}".format(str(res.group(1)), str(res.group(2)), str(res.group(3)))
            package_details['Name'] = str(res.group(1))
            package_details['Type'] = DiametriqConstants.APPLICATION

        elif "RO-R" in package_name:
            p = re.compile("(.*)-(.*)-x86_64.linux-gnu-g\+\+.tgz")
            res = p.match(package_name)
            package_details['Version'] = "{}_{}".format(str(res.group(1)), str(res.group(2)))
            package_details['Name'] = ["CTF", "OCS"]
            package_details['Type'] = DiametriqConstants.APPLICATION

        self._log.debug("Package details %s", str(package_details))
        self._log.debug("<")
        return package_details

    def version_comparator(self, version_one, version_two):
        """
        Comparator function to sort the verison list
        Args:
            version_one: Version 1
            version_two: Version 2

        Returns: 1 if version_one > version_two
                 0 if version_one == version_two
                 -1 if version_one < version_two

        """
        if re.match(".*-.*", version_one):
            # cases like (version two = 2.2.2 > version one = 2.2.2-123)
            if re.match("^\d.\d.\d$", version_two):
                if version_two in version_one:
                    return -1
        elif re.match(".*-.*", version_two):
            # cases like (version one = 2.2.2 > version two = 2.2.2-123)
            if re.match("^\d.\d.\d$", version_one):
                if version_one in version_two:
                    return 1
        elif LooseVersion(version_one) > LooseVersion(version_two):
            return 1
        elif LooseVersion(version_one) == LooseVersion(version_two):
            return 0
        else:
            return -1
