"""
#Add module string.
"""
#!/bin/python
import time
import signal
import pexpect
from stats_utility import Utility, ClientStatsSender

COLLECTION_NAME = "IWFMessageStatResult"
IWF_DURATION_KEY = "IWFmsgStatsDuration"
SCRIPT_NAME = "iwfmsgstats"

DATE = "date +%s"

def get_stats_info():
    """ This method returns the collection name and fields which are used in
    this stats.

    Return:
        dict: key=collections name,
              val=Fileds the

    """
    fields = ["timeStamp","RRSMS_Argout_MPS","Cont_Argout_MPS","RRBCSM_Argout_MPS","Continue","REL_Argout_MPS","TcComp_Sent","CCR_ReqOut","CCR_Error"]
    #Eg: fileds = ["CPU(%)", "Load"]
    stats_info_dict = {COLLECTION_NAME: fields}
    return stats_info_dict

class IWFMessageStatResult(object):
    """
    #Add doc string
    """

    def __init__(self, client):
        """ The SystemStats initilize Utility class object.

        Args:
            client(instance): Object of the ClientStatsSender class.

        """
        self._client_obj = client
        self._is_mmlconsole_created = False
        self._bash_var = None
        self._data = []
        self._data2 = []
        self._requestin = None
        self._requestout = None
        self._answerin = None
        self._answerout = None
        self._mml = None
        self._argout_contsms_prev_timestamp = 0
        self._argout_contsms_prev_msg = 0
        self._argout_rrsms_prev_timestamp = 0
        self._argout_rrsms_prev_msg = 0
        self._argout_tc_comp_sent_prev_timestamp = 0
        self._argout_tc_comp_sent_prev_msg = 0
        self._argout_rrbcsm_prev_timestamp = 0
        self._argout_rrbcsm_prev_msg = 0
        self._argout_continue_prev_timestamp = 0
        self._argout_continue_prev_msg = 0
        self._argout_rel_prev_timestamp = 0
        self._argout_rel_prev_msg = 0
        self._ccr_reqout_prev_timestamp = 0
        self._ccr_reqout_prev_msg = 0
        self._start_time = None
        self._end_time = None

    def create_mml_console(self):
        """
        This Method used to create console for the mml 
        """
        self._bash_var = ("bash -norc")
        self._mml = pexpect.spawn(self._bash_var)
        self._change_prompt()
        self._mml.sendline("su root")
        self._mml.sendline("cd /opt/diametriq/iwf/bin")
        self._mml.sendline("./DBGConsole -socket -configFile ../config/dbc_console.ini")
        self._mml.expect(">>")
        self._mml.sendline("enStatistics")
        self._mml.expect(">>")
        self._mml.sendline("EnInterfaceStats")
        self._mml.expect(">>")
        self._mml.is_mmlconsole_created = True

    def _change_prompt(self):
        """ This method changes the newly opened bash command prompt to
        "public_key_share".
        Args:self(instance) - it refers to the variables and the methods to the
        same class.
        Returns:
            None
        """
        cmd = "export PS1=\"iwf_mml_key\""
        self._mml.sendline(cmd)

    def _getstat(self):
        """
        """

    def _close_mml_console(self):
        self._mml.close()
        self.is_mmlconsole_created = False

    def execute_iwfmessagestatresult(self):
        """This method execute stats commands.
        Take avg of start and end time because execution of all commmands
        takig nearly one second .

        Args:
            None:

        Returns:
            None - Nothing is returned

        """
        self._start_time = Utility.command_executer(DATE)
        self._requestout = None
        self._requestin = None
        self._answerin = None
        self._answerout = None
        self._send1 = None
        self._data1 = None
        self._data2 = None
        self._mml.sendline("stats")
        self._mml.expect(['>>', pexpect.TIMEOUT], timeout=10)
        self._data1 = self._mml.before
        self._mml.sendline("getRoStats")
        self._mml.expect(['>>', pexpect.TIMEOUT], timeout=10)
        self._data2 = self._mml.before
        self._stats_data = self._data1.split('\n')
        self._ro_stats_data = self._data2.split('\n')
        for line  in self._stats_data:
            if "ContSMS" in line:
                str1 = line
                str2 = str1.strip('ContSMS    :')
                self._send1 = str2.split('|')
            if "RRSMS" in line:
                str3 = line
                str4 = str3.strip('RRSMS      :')
                self._send2 = str4.split('|')
            if "TcComp Sent" in line:
                str5 = line
                str6 = str5.strip('TcComp Sent:')
                self._send3 = str6.split('|')
            if "RRBCSM" in line:
                str7 = line
                str8 = str7.strip('RRBCSM     :')
                self._send4 = str8.split('|')
            if "Continue" in line:
                str9 = line
                str10 = str9.strip('Continue   :')
                self._send5 = str10.split('|')
            if "REL        :" in line:
                str11 = line
                str12 = str11.strip('REL        :')
                self._send6 = str12.split('|')
        for line  in self._ro_stats_data:
            if "CCR" in line:
                str1 = line
                str2 = str1.strip('CCR/CCA           :')
                self._send30 = str2.split('|')
        self._argout_contsms = self._send1[0].strip()
        self._argout_rrsms = self._send2[0].strip()
        self._argout_tc_comp_sent = self._send3[0].strip()
        self._argout_rrbcsm = self._send4[0].strip()
        self._argout_continue = self._send5[0].strip()
        self._argout_rel = self._send6[0].strip()
        self._ccr_reqout = self._send30[2].strip()
        self._ccr_error = self._send30[5].strip()
        print("argaut %s",self._argout_rrsms)
        print("===")
        print(self._argout_tc_comp_sent)
        print("===")
        print(self._argout_contsms)
        print("self.argout contsms is %s",self._argout_contsms)
        print(self._argout_tc_comp_sent)
        print(self._argout_continue)
        print(self._argout_rrbcsm)
        print(self._argout_rel)
        print("ccr out %s",self._ccr_reqout)
        print(self._ccr_error)
        self._end_time = Utility.command_executer(DATE)

    def _get_argout_contsms_mps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        print ("self.argout contsms is %s",self._argout_contsms)
        interval_msg_count = int(self._argout_contsms) - int(self._argout_contsms_prev_msg)
        interval_duration = self.get_time_stamp() - self._argout_contsms_prev_timestamp
        self._argout_contsms_prev_timestamp = self.get_time_stamp()
        self._argout_contsms_prev_msg = int(self._argout_contsms)
        if not interval_duration:
            return 0
        tps = interval_msg_count/interval_duration
        return round(float(tps), 2)

    def get_argout_rrsms_mps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        interval_msg_count = int(self._argout_rrsms) - int(self._argout_rrsms_prev_msg)
        interval_duration = self.get_time_stamp() - self._argout_rrsms_prev_timestamp
        self._argout_rrsms_prev_timestamp = self.get_time_stamp()
        self._argout_rrsms_prev_msg = int(self._argout_rrsms)
        if not interval_duration:
            return 0
        tps = interval_msg_count/interval_duration
        return round(float(tps), 2)

    def get_argout_tc_comp_sent_mps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        print("=======sfsdfsf===")
        print(int(self._argout_tc_comp_sent))
        print("=======sfsdfsf===")
        interval_msg_count = int(self._argout_tc_comp_sent) - int(self._argout_tc_comp_sent_prev_msg)
        interval_duration = self.get_time_stamp() - self._argout_tc_comp_sent_prev_timestamp
        self._argout_tc_comp_sent_prev_timestamp = self.get_time_stamp()
        self._argout_tc_comp_sent_prev_msg = int(self._argout_tc_comp_sent)
        if not interval_duration:
            return 0
        tps = interval_msg_count/interval_duration
        print("msg count is %s",interval_msg_count)
        #print("tps is ")
        #print(tps)
        return round(float(tps), 2)

    def get_argout_rrbcsm_mps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        interval_msg_count = int(self._argout_rrbcsm) - int(self._argout_rrbcsm_prev_msg)
        if interval_msg_count != 0:
            interval_duration = self.get_time_stamp() - self._argout_rrbcsm_prev_timestamp
            self._argout_rrbcsm_prev_timestamp = self.get_time_stamp()
            self._argout_rrbcsm_prev_msg = int(self._argout_rrbcsm)
            if not interval_duration:
                return 0
            tps = interval_msg_count/interval_duration
            return round(float(tps), 2)
        else:
            return 0

    def get_argout_continue_mps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        interval_msg_count = int(self._argout_continue) - int(self._argout_continue_prev_msg)
        if interval_msg_count != 0:
            interval_duration = self.get_time_stamp() - self._argout_continue_prev_timestamp
            self._argout_continue_prev_timestamp = self.get_time_stamp()
            self._argout_continue_prev_msg = int(self._argout_continue)
            if not interval_duration:
                return 0
            tps = interval_msg_count/interval_duration
            return round(float(tps), 2)
        else:
            return 0

    def get_argout_rel_mps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        interval_msg_count = int(self._argout_rel) - int(self._argout_rel_prev_msg)
        if interval_msg_count != 0:
            interval_duration = self.get_time_stamp() - self._argout_rel_prev_timestamp
            self._argout_rel_prev_timestamp = self.get_time_stamp()
            self._argout_rel_prev_msg = int(self._argout_rel)
            if not interval_duration:
                return 0
            tps = interval_msg_count/interval_duration
            return round(float(tps), 2)
        else:
            return 0

    def get_ccr_reqout_mps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        interval_msg_count = int(self._ccr_reqout) - int(self._ccr_reqout_prev_msg)
        if interval_msg_count != 0:
            interval_duration = self.get_time_stamp() - self._ccr_reqout_prev_timestamp
            self._ccr_reqout_prev_timestamp = self.get_time_stamp()
            self._ccr_reqout_prev_msg = int(self._ccr_reqout)
            if not interval_duration:
                return 0
            tps = interval_msg_count/interval_duration
            return round(float(tps), 2)
        else:
            return 0

    def get_time_stamp(self):
        """This method returns date and time.

        Args:

        Returns:
            int - date and time

        """

        try:
            return (int(self._start_time) + int(self._end_time))/2
        except ValueError:
            return -1

    def send_iwfmessagestatresult(self):
        """This method sends the iwf message stats information to pushgateway
        and stats collector.

        Args:
           None

        Returns:
            None
        """
        #Note: Field name should be in [a-zA-Z_:][a-zA-Z0-9_:]* regex pattern
        #Examples: 
        #1. Field which contains with bracket not supported --> "cpu(%)": self.get_cpu()
        #2. Field which starts with number not supported --> 5xxx_ans_sent":  10
        iwf_dict = {
            "timeStamp":self.get_time_stamp(),
            "RRSMS_Argout_MPS":self.get_argout_rrsms_mps(),
            "Cont_Argout_MPS":self._get_argout_contsms_mps(),
            "RRBCSM_Argout_MPS":self.get_argout_rrbcsm_mps(),
            "Continue":self.get_argout_continue_mps(),
            "REL_Argout_MPS":self.get_argout_rel_mps(),
            "TcComp_Sent":self.get_argout_tc_comp_sent_mps(),
            "CCR_ReqOut":self.get_ccr_reqout_mps(),
            "CCR_Error":self._ccr_error,
            "collectionName": COLLECTION_NAME,
            "otherInfo": {"ScriptName": SCRIPT_NAME}
        }
        self._client_obj.send_stats_to_server(iwf_dict)

if __name__ == '__main__':
    DURATION = Utility.get_duration(IWF_DURATION_KEY)
    CLIENT_OBJ = ClientStatsSender()
    STATS_OBJ = IWFMessageStatResult(CLIENT_OBJ)
    DONE = True
    STATS_OBJ.create_mml_console()
    #STATS_OBJ.execute_iwfmessagestatresult()

    def sigint_handler(signum, frame):
        """ This method catch the signal and perform respective action.
        """
        global DONE
        DONE = False
        STATS_OBJ._close_mml_console()

    signal.signal(signal.SIGINT, sigint_handler)

    while DONE:
        try:
            START_TIME = time.time()
            STATS_OBJ.execute_iwfmessagestatresult()
            #STATS_OBJ.get_argout_tc_comp_sent_mps()
            time.sleep(2)
            END_TIME = time.time()
            STATS_OBJ.send_iwfmessagestatresult()
            time.sleep(DURATION)-(END_TIME-START_TIME)
        except Exception as ex:
            continue
