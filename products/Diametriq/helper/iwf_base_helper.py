""" Helper library to support iwf node
"""
#import regal.logger.logger as logger
#from regal.utility import GetRegal
from Diametriq.helper.diametriq_helper_util import DiametriqHelperUtil
from Diametriq.helper.diametriq_helper_util import InsufficientHelperConfig

class IWFHelper(DiametriqHelperUtil):
    """ Base class whcih supports the common operation for iwf helper
    """
    def __init__(self, node_name, app_name):
        super(IWFHelper, self).__init__(node_name)
        self._log = logger.GetLogger("IWFHelper")
        self._log.debug(">")
        self._app_name = app_name
        self._platform_obj = self._os_obj.platform
        self._tool_obj = self._platform_obj.get_app(app_name)
        # Clear the instance info if alredy present in the tool object
        #self._tool_obj._exit()
        self._log.debug("<")

    def generate_and_upload_iwf_config(self):
        """This method is used to generate and upload sql-dump config to iwf-node

        Returns:
            None

        """
        self._log.debug(">")
        node_config = self._config.get_testcase_config(self._node_name)
        if node_config != '-NA-':
            if "CreateRestoreConfig" in node_config:
                config_data = node_config["CreateRestoreConfig"]
                tem_file, itu_xml_file, tag_dict = self._get_iwf_template_and_tag_dict(config_data)
            else:
                raise InsufficientHelperConfig(self._node_name, "CreateRestoreConfig")
        else:
            raise InsufficientHelperConfig(self._node_name, self._node_name)
        self._tool_obj.generate_and_upload_iwf_configuration(tem_file, itu_xml_file, tag_dict)
        self._log.info("Successfully copied mysql dump on node %s", str(
            self._node_name))

    def _get_iwf_template_and_tag_dict(self, config_dict):
        """
        """
        self._log.debug(">")
        #hostip = self._get_management_ip(self._node_name)
        #cmd = "hostname"
        hostname = GetRegal().GetAnsibleUtil().execute_shell("hostname",
                self._get_management_ip(self._node_name))
        config = {
            "hostname" : hostname
            }
        self._validate_iwf_config_keys(config_dict)
        deafult_keys = self.get_tag_dict(config_dict["Default_config"])
        template_file = self.get_config_value(config_dict["TemplateFile"])
        itu_xml_file = self.get_config_value(config_dict["IwfItuXmlFile"])
        variable_keys = {}
        variable_config = config_dict["Variable_config"]
        variable_config_keys = list(variable_config.keys())

        for variable_key in variable_config_keys:
            value, instance = self.get_config_value(variable_config[variable_key])
            variable_keys.update(IWFHelper._increment_key_and_value(variable_key, value, instance))

        tag_dict = {}
        tag_dict.update(deafult_keys)
        tag_dict.update(variable_keys)
        tag_dict.update(config)
        self._log.debug("<")
        return template_file, itu_xml_file, tag_dict

    def _validate_iwf_config_keys(self, config_dict):
        """
        """
        self._log.debug(">")
        config_keys = ["Variable_config", "Default_config", "TemplateFile"]
        self._check_key(config_dict, config_keys)
        self._log.debug("<")


    @staticmethod
    def _increment_key_and_value(key, val, instence):
        increment_dict = {}
        for instance_ in range(1, instence+1):
            val = val + 1
            increment_dict["{}_{:02d}".format(key, instance_)] = val
        return increment_dict

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

    def start_iwf(self):
        """Method to start iwf

        Returns:
            None

        """
        self._tool_obj.start_iwf()

    def stop_iwf(self):
        """Method to stop iwf

        Returns:
            None

        """
        self._tool_obj.stop_iwf()

    def start_stats(self):
        """ This method starts the stats service script in the mapped machine.

        Returns:
            None

        """
        self._tool_obj.start_stats()

    def stop_stats(self):
        """ This method starts the stats service script in the mapped machine.

        Returns:
            None

        """
        self._tool_obj.stop_stats()
