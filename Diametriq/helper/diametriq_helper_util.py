"""This module comprise of a class with common helper tool functions shared between
products Diameter and Diametriq.
"""
import sys
from Regal.regal_constants import Constants as RegalConstants

class InvalidConfiguration(Exception):
    """ Exception will be thrown when configuration is invalid
    """
    def __init__(self, err_msg):
        super(InvalidConfiguration, self).__init__()
        self._error_msg = err_msg

    def __str__(self):
        """ Return exception string. """
        return "{}".format(self._error_msg)

class InsufficientHelperConfig(Exception):
    """ Exception will be thrown when insufficient configuration key
    """
    def __init__(self, node_name, key):
        super(InsufficientHelperConfig, self).__init__()
        self._key = key
        self._node_name = node_name

    def __str__(self):
        """ Return exception string. """
        return "Key {} for Diameter helper is not configured for node {}".format(
                self._key, self._node_name)

class DiametriqHelperUtil(object):
    """
    Class comprises of helper functions that are commonly used by both
    Diameter and Diametriq products
    """
    def __init__(self, service_store_obj, node_name):
        class_name = self.__class__.__name__
        self.service_store_obj = service_store_obj
        log_mgr_obj = self.service_store_obj.get_log_mgr_obj()
        self._log = log_mgr_obj.get_logger(class_name)
        self._log.debug(">")
        self._node_name = node_name
        self._sut_name = self.service_store_obj.get_current_sut()
        self._run_count = self.service_store_obj.get_current_run_id()
        self._stats_mgr = self.service_store_obj.get_stat_mgr_obj()
        self._topology = self.service_store_obj.get_current_run_topology()
        self._node_obj = self._topology.get_node(node_name)
        self._os_obj = self._node_obj.get_os()
        self._topology_node_list = self._topology.get_node_list()
        self._config = self.service_store_obj.get_current_test_case_configuration()
        self._log.debug("<")

    def _get_keys(self, data_dict, filter_list):
        """ This private method keys of teh dictionary  and filter off any
        thing mentioned.

        Args:
            data_dict(dict): configuration dict.
            filter_list(list): list of filters.

        Returns:
            list: list of dictionary keys.

        """
        key_list = list(data_dict.keys())
        for item in filter_list:
            key_list.remove(item)
        return key_list

    def _validate_diaperf_config_fields(self, config_dict):
        """
        """
        self._log.debug(">")
        config_mandatory_fileds = ["Instance", "Default_config",
                                   "Variable_config"]
        self._check_key(config_dict, config_mandatory_fileds)
        self._log.debug("<")

    def _check_key(self, config_dict, key_list):
        """
        """
        self._log.debug(">")
        for key in key_list:
            if key not in config_dict:
                self._log.debug("<")
                raise InsufficientHelperConfig(self._node_name, key)
        self._log.debug("<")

    def get_config_value(self, data_dict):
        """ This method the titan configuration such as template file
        name and tag_dict.

        Args:
            data_dict(dict): configuration dict.

        Returns:
            str: value of requeted field.

        Raise:
            exception.InvalidConfiguration

        """
        try:
            if data_dict["Type"] == "constant":
                if "Realm" in data_dict:
                    return [data_dict["Value"], data_dict["Realm"]]
                if "Instance" in data_dict:
                    return data_dict["Value"], data_dict["Instance"]
                return data_dict["Value"]
            elif data_dict["Type"] == "interface_name":
                node_name = data_dict["Node"]
                node_mip = self._get_management_ip(node_name)
                subnet = data_dict["Subnet"]
                return self._os_obj.get_interface_name_from_subnet_group(node_mip, subnet)
            elif data_dict["Type"] == "ip":
                node_name = data_dict["Node"]
                node_mip = self._get_management_ip(node_name)
                subnet = data_dict["Subnet"]
                output = self._os_obj.get_ips_from_subnet_group(node_mip,
                        subnet)
                if output:
                    return output[0]
                raise InvalidConfiguration(
                        "No ip found for subnet {} at titan helper".format(subnet))
            elif data_dict["Type"] == 'management_ip':
                node_name = data_dict["Node"]
                return self._get_management_ip(node_name)
            elif data_dict["Type"] == 'server_ip':
                self._log.debug("data_dict is server_ip")
                self._log.debug("data_dict SubnetIP - %s", data_dict["SubnetIP"])
                return data_dict["SubnetIP"]
        except KeyError as ex:
            raise InvalidConfiguration("{} at node {}".format(ex,
                self._node_name))

    def _get_management_ip(self, node_name):
        """ This private method returns the management ip of teh node given.

        Args:
            node_name(str): name of the node.

        Returns:
            str: management ip

        Raise:
            exception.InvalidConfiguration

        """
        for node_obj in self._topology_node_list:
            if node_obj.get_name() == node_name:
                return node_obj.get_management_ip()
        raise InvalidConfiguration(
                "node {} is not having management_ip".format(node_name))

    def apply_configuration(self):
        """ This method sets up the stats service rpms in the mapped machine.

        Returns:
            None

        """
        self._log.debug(">")
        self._log.info("Setting up the stats on nodes %s",
                str(self._node_name))
        stat_args_dict = {}
        stats_args_dict = self._get_stats_argumnts()
        stat_args_dict[self._get_node_name()] = stats_args_dict
        stats_app = self._os_obj.platform.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.apply_configuration(stat_args_dict)
        self._log.info("Set up the stats on nodes %s is successful.",
                str(self._get_node_name()))
        self._log.debug("<")

    def _get_stats_argumnts(self):
        """ This private method returns the stats arguments.


        Returns:
            dict: arguments of stats.

        Raise:
            InvalidConfiguration

        """
        args_dict = {}
        data_dict = self._get_stats_info()
        self._log.info("Stat_info dict is {}".format(data_dict))
        if "Arguments" in data_dict:
            data_dict = data_dict["Arguments"]
            args_dict = self.get_config_value(data_dict)
            if not isinstance(args_dict, dict):
                raise InvalidConfiguration(
                        "Excpected a dict type of value for stats arguments of node {}".format(
                            self._node_name))
        return args_dict

    def _get_stats_info(self):
        """ This private method returns the stats from configuration.


        Returns:
            dict: complete stats information.

        Raise:
            InsufficientHelperConfig
            InvalidConfiguration

        """
        node_config = self._config.get_test_case_config(self._node_name)
        if node_config != '-NA-':
            if "StatsInfo" in node_config:
                return node_config["StatsInfo"]
            else:
                raise InsufficientHelperConfig(self._node_name, "StatsInfo")
        else:
             raise InsufficientHelperConfig(self._node_name, self._node_name)

    def _get_node_name(self):
        """ This method returns the node name

        Returns:
            str: node name.

        """
        return self._node_name

    def _get_stats_list(self):
        """ This private method returns the stats list value configured in the
        configuartion.


        Returns:
            list: configured list value.

        Raise:
            InsufficientHelperConfig
            InvalidConfiguration

        """
        data_dict = self._get_stats_info()

        if "Stats" in data_dict:
            data_dict = data_dict["Stats"]
            output = self.get_config_value(data_dict)
            if isinstance(output, list):
                return output
            raise InvalidConfiguration(
                    "Excpected a list type of value for stats list of node {}".format(
                        self._node_name))
        else:
            raise InsufficientHelperConfig(self._node_name, "Stats")
