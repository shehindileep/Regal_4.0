""" Helper library to support diameter perf tool
"""
import sys

from Regal.regal_constants import Constants as RegalConstants
from Diametriq.helper.diametriq_helper_util import DiametriqHelperUtil
from Diametriq.helper.diametriq_helper_util import InvalidConfiguration, InsufficientHelperConfig

IS_PY2 = sys.version_info < (3, 0)

class DiameterPerfHelper(DiametriqHelperUtil):
    """ Base class whcih supports the common operation of the titan
    """
    def __init__(self, service_store_obj, node_name, app_name, dia_type):
        super(DiameterPerfHelper, self).__init__(service_store_obj, node_name)
        class_name = self.__class__.__name__
        self.service_store_obj = service_store_obj
        log_mgr_obj = self.service_store_obj.get_log_mgr_obj()
        self._log = log_mgr_obj.get_logger(class_name)
        self._log.debug(">")
        self._node_name = node_name
        self._stats_mgr = self.service_store_obj.get_stat_mgr_obj()
        self._app_name = app_name
        self._topology = self.service_store_obj.get_current_run_topology()
        self._node_obj = self._topology.get_node(node_name)
        self._os_obj = self._node_obj.get_os()
        self._platform_obj = self._os_obj.platform
        self._tool_obj = self._platform_obj.get_app(app_name)
        self._dia_type = dia_type
        self._node_obj = self._topology.get_node(node_name)
        self._topology_node_list = self._topology.get_node_list()
        self._sut_name = self.service_store_obj.get_current_sut()
        self._run_count = self.service_store_obj.get_current_run_id()
        self._suite_name = self.service_store_obj.get_current_suite()
        self._testcase_name = self.service_store_obj.get_current_test_case()
        self._config = self.service_store_obj.get_current_test_case_configuration()
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
        key_list = self._get_keys(config_dict, filter_list)
        tag_dict = {}
        for key in key_list:
            value = config_dict[key]
            tag_dict[key] = self.get_config_value(value)
        return tag_dict

    def setup_tool(self, mml=False):
        """ This method is used to setup the diameter perf tool.

        Returns:
            None

        Raise:
            exception.InsufficientHelperConfig

        """
        self._log.debug(">")
        self._log.info("Setting up the perf tool on node %s.", str(self._node_name))
        node_config = self._config.get_test_case_config(self._node_name)
        if self._app_name == "DSA":
            dsa_config = node_config['application']
        if node_config != '-NA-':
            if self._app_name == 'CTF' or self._app_name == 'OCS':
                tt_config = self._get_ctf_perf_config()
            else:
                tt_config = self.get_tt_config()
            try:
                if  self._app_name == 'DSS' and node_config['instance_1'] and node_config['instance_1']['Mode'] == "dss_stack":
                    if self._app_name == 'DSS':
                        dss_config = node_config['instance_1']['stack']["PerfConfiguration"]["Config_dictionary"]
                        instance = self.get_config_value(dss_config['Instance'])
                        default_config = self.get_tag_dict(dss_config['Default_config'])
                        variable_config = self.get_tag_dict(dss_config["Variable_config"])
                        config = {}
                        config.update(default_config)
                        config.update(variable_config)
                        self._tool_obj.get_config()
                        for index in range(1, instance+1):
                            for key, val in list(variable_config.items()):
                                if isinstance(val, list):
                                    if str(val[1]).strip():
                                        config[key] = "{}{:02d}.{}".format(val[0], index, val[1])
                                    else:
                                        config[key] = "{}{}".format(val[0], index)
                                else:
                                    config[key] = val + index
                            self._tool_obj.setup_dia_inst("s",
                                                          index, config, tt_config, False)

                elif self._app_name == 'DSA' and "PerfConfiguration" in dsa_config:
                    if self._app_name == 'DSA':
                        if "Config_dictionary" in dsa_config["PerfConfiguration"]:
                            perf_config = dsa_config["PerfConfiguration"]["Config_dictionary"]
                            instance = self.get_config_value(perf_config["Instance"])
                            default_config = self.get_tag_dict(perf_config["Default_config"])
                            variable_config = self.get_tag_dict(perf_config["Variable_config"])
                            config = {}
                            config.update(variable_config)
                            config.update(default_config)
                            self._tool_obj.get_config()
                            for index in range(1, instance+1):
                                for key, val in list(variable_config.items()):
                                    if isinstance(val, list):
                                        if str(val[1]).strip():
                                            config[key] = "{}{:02d}.{}".format(val[0], index, val[1])
                                        else:
                                            config[key] = "{}{}".format(val[0], index)
                                    else:
                                        config[key] = val + index
                                self._tool_obj.setup_dia_inst("s", index, config, tt_config, False)
                    self._log.debug("<")   #call function with parsing logic for both dss and dsa
                elif self._app_name == 'MME' or self._app_name == 'HSS'\
                        or self._app_name == 'CTF' or self._app_name == 'OCS':
                    if "PerfConfiguration" in node_config:
                        if "Config_dictionary" in node_config["PerfConfiguration"]:
                            perf_config = node_config["PerfConfiguration"]["Config_dictionary"]
                            self._validate_diaperf_config_fields(perf_config)
                            instance = self.get_config_value(perf_config["Instance"])
                            default_config = self.get_tag_dict(perf_config["Default_config"])
                            variable_config = self.get_tag_dict(perf_config["Variable_config"])
                            config = {}
                            config.update(variable_config)
                            config.update(default_config)
                            self._tool_obj.get_config()
                            if isinstance(tt_config, dict):
                                if not tt_config:
                                    tt_config = '-NA-'
                                imsi_list = self.get_imsi_list(config, instance)
                                self.setup_instance(variable_config, config, tt_config,
                                                    imsi_list, 1, instance, mml)
                            elif isinstance(tt_config, list):
                                instance = self.get_instance_count(tt_config)
                                imsi_list = self.get_imsi_list(config, instance)
                                self.check_and_proceed_ttconfig_list(tt_config, variable_config, config, imsi_list, mml)

                        else:
                            self._log.debug("<")
                            raise InsufficientHelperConfig(self._node_name, "Config_dictionary")

                    else:
                        self._log.debug("<")
                        raise InsufficientHelperConfig(self._node_name, "PerfConfiguration")
            except KeyError as ex:
                raise InvalidConfiguration("{} at node {}".format(ex, self._node_name))
                self._log.debug("<")
        else:
            self._log.debug("<")
            raise InsufficientHelperConfig(self._node_name, self._node_name)
        self._log.info("Set up the perf tool on node %s successfully.", str(self._node_name))
        self._log.debug("<")

    def get_instance_count(self, tt_config):
        """This method is used to get the total instance count if type of
        ttconfig is list

        Args:
            tt-config(dict): traffic tool configuration dict.

        Returns:
            count(int):total instance count

        Raise:
            exception.InsufficientHelperConfig
        """
        count = []
        for ttconfig in tt_config:
            if "start_instance" in ttconfig and "end_instance" in ttconfig and "ttconfig" in ttconfig:
                end_instance = ttconfig["end_instance"]
                count.append(end_instance)
            else:
                self._log.debug("<")
                raise InsufficientHelperConfig(self._node_name, "tt_config")
        return max(count)

    def get_imsi_list(self, config, instance):
         """ This method is used to get the imsi list if it is present in
         testcase_config.json

         Args:
             config(dict): configuration dict.
             instance(int): total instance

         Returns:
             imsi_list(list): list of imsi range

         """
         if 'imsi_range' in config:
             self._log.debug("Distribute IMSI - {}".format(config['distribute_imsi']))
             if 'distribute_imsi' in config and config['distribute_imsi'].lower() == "yes":
                 self._log.info("IMSI is distributed across all the peers in - {}".format(
                     self._node_name))
                 imsi_start, imsi_end = [int(elem) for elem in
                                         config['imsi_range'].split('-')]
                 step = int((imsi_end - imsi_start) / instance)
                 imsi_list = ["{}-{}".format(int(imsi_start + step*i),
                                             int(imsi_start + step*(i+1))) if i == 0 else "{}-{}".format(int(imsi_start + step*i+1),
                                                                                                         int(imsi_start + step*(i+1))) for i in range(instance)]

             else:
                 imsi_list = ["{}".format(config['imsi_range']) for i in range(instance)]

             self._log.info('IMSI range for node {} -{}'.format(
                 self._node_name, imsi_list))
             return imsi_list

    def setup_instance(self, variable_config, config, tt_config, imsi_list,
                       start_instance, end_instance, mml):
        """ This method is used to setup the instance

        Args:
            variable_config(dict): variable configuration dict
            config(dict): configuration dict.
            tt-config(dict): traffic tool configuration dict.
            imsi_list(list): list of imsi range
            start_instance(int): start instance
            end_instance(int): end instance

        Returns:
            None

        """
        for index in range(start_instance, end_instance+1):
            for key, val in list(variable_config.items()):
                if isinstance(val, list):
                    if str(val[1]).strip():
                        if self._app_name == 'CTF' or self._app_name == 'OCS':
                            if end_instance == 1:
                                config[key] = "{}.{}".format(val[0], val[1])
                            else:
                                config[key] = "{}{:02d}.{}".format(val[0], index, val[1])
                        else:
                            config[key] = "{}{:02d}.{}".format(val[0], index, val[1])
                    else:
                        config[key] = "{}{}".format(val[0], index)
                elif isinstance(val, int):
                    if self._app_name == 'CTF' or self._app_name == 'OCS':
                        config[key] = val + index - 1
                    else:
                        config[key] = val + index
                elif isinstance(val, str):
                    if self._app_name == 'CTF' or self._app_name == 'OCS':
                        if end_instance == 1:
                            config[key] = val
                        else:
                            config[key] = "{}{:02d}".format(val, index)
            if 'imsi_range' in config:
                config['imsi_range'] = imsi_list.pop(0)
            self._tool_obj.setup_dia_inst(self._dia_type, index,
                                          config, tt_config, mml)

    def check_and_proceed_ttconfig_list(self, tt_config, variable_config, config, imsi_list, mml):
        """This method is used to setup the instance based on tt_config list

        Args:
            tt_config(list): tt_config list
            variable_config(dict): variable configuration dict
            config(dict): configuration dict.
            imsi_list(list): list of imsi range
            mml(str): setup mml files if true

        Returns:
            None

        Raise:
            exception.InsufficientHelperConfig

        """
        for ttconfig in tt_config:
            if "start_instance" in ttconfig and "end_instance" in ttconfig and "ttconfig" in ttconfig:
                start_instance = ttconfig["start_instance"]
                end_instance = ttconfig["end_instance"]
                tt_config = ttconfig["ttconfig"]
                config["start_val"] = start_instance
                self.setup_instance(variable_config,
                                    config, tt_config, imsi_list,
                                    start_instance, end_instance, mml)
            else:
                self._log.debug("<")
                raise InsufficientHelperConfig(self._node_name, "tt_config")

    def get_node_tt_config(self):
        """ Method read the tt config the node and returns the dict.


        """
        self._log.debug(">")
        node_config = self._config.get_test_case_config(self._node_name)
        if node_config != '-NA-':
            if "tt_config" in node_config:
                self._log.debug("<")
                return node_config["tt_config"]
            else:
                self._log.debug("<")
                return {}
        else:
            self._log.debug("<")
            raise InsufficientHelperConfig(self._node_name, "node_config")

    def get_tc_tt_config(self):
        """ Method return the test case

        Returns:
            dict: The dictionary of the config.

        """
        self._log.debug(">")
        tc_config = self._config.get_test_case_config()
        if "tt_config" in tc_config:
            self._log.debug("<")
            return tc_config["tt_config"]
        else:
            self._log.debug("<")
            raise InsufficientHelperConfig(self._node_name, "tt_config")

    def get_tt_config(self):
        """ Return tt config.

        Returns:
            dict: The tt config
        """
        self._log.debug(">")
        node_tt_config = self.get_node_tt_config()
        if not node_tt_config:
            self._log.debug("<")
            return self.get_tc_tt_config()
        self._log.debug("<")
        return node_tt_config

    def _get_ctf_perf_config(self):
        """ Return perf config.

        Returns:
            dict: The perf config
        """
        self._log.debug(">")
        tc_config = self._config.get_test_case_config()
        if "ctf_perf_config" in tc_config:
            self._log.debug("<")
            return tc_config["ctf_perf_config"]
        else:
            self._log.debug("<")
            raise InsufficientHelperConfig(self._node_name, "ctf_perf_config")

    def _validate_diaperf_traffic_params(self, config_dict):
        """
        """
        self._log.debug(">")
        trafic_param = ["message_burst", "sleep"]
        self._check_key(config_dict, trafic_param)
        self._log.debug("<")

    def get_app_and_client_id(self):
        """
        """
        config = self._config.get_test_case_config()
        if "AppID" in config and "ClientID" in config:
            return config["AppID"], config["ClientID"]
        return None


    def start_tool(self):
        """ This method start the perf tool.

        Returns:
            None

        """
        self._log.debug(">")
        inst_count = self._get_total_inst_count()
        if self._app_name == 'DSA':
            app_id, client_id = self.get_app_and_client_id()
            self._tool_obj.start_dia_inst(-1, self._dia_type, self._node_obj, inst_count, app_id, client_id)
        else:
            self._tool_obj.start_dia_inst(-1, self._dia_type, self._node_obj, inst_count)
        self._log.debug("<")

    def _get_traffic_params(self):
        """
        """
        self._log.debug(">")
        node_config = self._config.get_test_case_config(self._node_name)
        perf_config = node_config["PerfConfiguration"]
        if "traffic_param" in perf_config:
            self._validate_diaperf_traffic_params(perf_config["traffic_param"])
            traffic_config = perf_config["traffic_param"]
            #duration = self.get_config_value(traffic_config["duration"])
            duration = int(self._config.get_test_case_config()["TestRunDuration"])
            burst_size = self.get_config_value(traffic_config["message_burst"])
            sleep = self.get_config_value(traffic_config["sleep"])
            return duration, burst_size, sleep
        else:
            self._log.debug("<")
            raise InsufficientHelperConfig(self._node_name, self._node_name)


    def start_traffic(self):
        """ This method is to start the traffic on perf tool.

        Returns:
            None

        """
        self._log.debug(">")

        duration, burst_size, sleep = self._get_traffic_params()
        inst_count = self._get_total_inst_count()
        self._tool_obj.start_traffic(-1, 'mml', self._node_obj, inst_count, duration, burst_size, sleep)
        self._log.debug("<")

    def stop_traffic(self):
        """ This method is to stop the traffic on perf tool.

        Returns:
            None

        """
        self._log.debug(">")
        inst_count = self._get_total_inst_count()
        self._tool_obj.stop_traffic(-1, 'mml', self._node_obj, inst_count)
        self._log.debug("<")

    def stop_tool(self):
        """ This method stop the perf tool.

        Returns:
            None

        """
        self._log.debug(">")
        inst_count = self._get_total_inst_count()
        self._tool_obj.stop_dia_inst(-1, self._dia_type, self._node_obj, inst_count)
        self._log.debug("<")

    def start_stats(self):
        """ This method starts the stats service script in the mapped machine.

        Returns:
            None

        """
        self._log.debug(">")
        all_stats_list = self._get_stats_list()
        stats_app = self._platform_obj.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.start_service(all_stats_list)
        self._log.info("Started the stats successfully on nodes %s", str(self._node_name))
        self._log.debug("<")

    def stop_stats(self):
        """ This method stops the stats service script in the mapped machine.

        Returns:
            None

        """
        self._log.debug(">")
        all_stats_list = self._get_stats_list()
        stats_app = self._platform_obj.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.stop_service(all_stats_list)
        self._log.debug("<")

    def check_stats(self):
        """ This method checks the stats service script in the mapped machine.

        Args:
            None

        Returns:
            None
        """
        self._log.debug(">")
        all_stats_list = self._get_stats_list()
        stats_app = self._platform_obj.get_app(RegalConstants.STATS_APP_NAME)
        stats_app.check_service_status(all_stats_list)
        self._log.debug("All stats successfully checked on node %s", str(self._node_name))
        self._log.debug("<")

    def _get_total_inst_count(self):
        """Method used to fetch total instance count from testcase_config

        Args:
            None

        Return:
            inst_count(int): total instance
        """
        node_config = self._config.get_test_case_config(self._node_name)
        if self._app_name == 'DSS':
            perf_config = node_config['instance_1']['stack']["PerfConfiguration"]["Config_dictionary"]
        elif self._app_name == 'DSA':
            dsa_config = node_config['application']
            perf_config = dsa_config["PerfConfiguration"]["Config_dictionary"]
        else:
            perf_config = node_config["PerfConfiguration"]["Config_dictionary"]
        inst_count = self.get_config_value(perf_config["Instance"])
        return inst_count

