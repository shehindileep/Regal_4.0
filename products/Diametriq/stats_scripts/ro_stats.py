"""
#Add module string.
"""
#!/bin/python
import time
import signal
import pexpect
from commands import getoutput
from stats_utility import Utility, ClientStatsSender

COLLECTION_NAME = "ROStatResult"
RO_DURATION_KEY = "ROStatsDuration"
SCRIPT_NAME = "rostats"

DATE = "date +%s"
CPU_CORE = "nproc"
CPU = "ps -C sampleRoR14App -o %cpu="
RSS = "ps -C sampleRoR14App -o rss="
VSZ = "ps -C sampleRoR14App -o vsize="

def get_stats_info():
    """ This method returns the collection name and fields which are used in
    this stats.

    Return:
        dict: key=collections name,
              val=Fileds the

    """
    fields = ["timeStamp", "TPS", "ReqIn", "ReqOut", "AnsIn", "AnsOut", "CPU", "RSS", " VSZ"]
    #Eg: fileds = ["CPU(%)", "Load"]
    stats_info_dict = {COLLECTION_NAME: fields}
    return stats_info_dict

class ROMessageStatResult(object):
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
        self._rss = None
        self._cpu = None
        self._vsz = None
        self._error = None
        self._answer_sent_prev_timestamp = 0
        self._answer_sent_prev_msg = 0
        self._start_time = None
        self._end_time = None

    def create_mml_console(self):
        """
        This Method used to create console for the mml
        """
        self._kill_DBGConsole()
        self._bash_var = ("bash -norc")
        self._mml = pexpect.spawn(self._bash_var)
        self._change_prompt()
        mml_path, bin_path = Utility.get_dss_mml_and_bin_path()
        self._mml.sendline(". {}".format(mml_path))
        self._mml.sendline("cd {}".format(bin_path))
        self._mml.sendline("./DBGConsole -socket -configFile dbc_console.client1.ini")
        self._mml.expect(">>")
        self._mml.sendline("enStatistics")
        self._mml.expect(">>")
        self._mml.is_mmlconsole_created = True

    def _kill_DBGConsole(self):
        process_id = getoutput('ps -elf | grep DBGConsole | grep -v grep | tr -s " " | cut -d " " -f 4')
        getoutput("kill -9 {}".format(process_id))

    def _change_prompt(self):
        """ This method changes the newly opened bash command prompt to
        "public_key_share".
        Args:self(instance) - it refers to the variables and the methods to the
        same class.
        Returns:
            None
        """
        cmd = "export PS1=\"ro_mml_key\""
        self._mml.sendline(cmd)

    def _getstat(self):
        """
        """

    def _close_mml_console(self):
        self._mml.close()
        self.is_mmlconsole_created = False

    def execute_romessagestatresult(self):
        """This method execute stats commands.
        Take avg of start and end time because execution of all commmands
        takig nearly one second .

        Args:
            None:

        Returns:
            None - Nothing is returned

        """
        self._start_time = Utility.command_executer("{}".format(DATE))
        self._requestout = None
        self._requestin = None
        self._answerin = None
        self._error = None
        self._answerout = None
        self._send1 = None
        self._data = None
        self._data2 = None
        self._mml.sendline("getStackStats")
        self._mml.expect(['>>', 'Error', pexpect.TIMEOUT], timeout=10)
        self._data = self._mml.before
        self._data2 = self._data.split('\n')
        for line  in self._data2:
            if "Application Based" in line:
                str1 = line
                str2 = str1.strip('Application Based:')
                self._send1 = str2.split('|')
        for line  in self._data2:
            if "Msg with 'E' bit set" in line:
                str3 = line
                str4 = str3.strip("Msg with 'E' bit set  :")
                self._send2 = str4.split('|')
        self._requestin = self._send1[3].strip()
        #print self._requestin
        self._requestout = self._send1[1].strip()
        #print self._requestout
        self._answerin = self._send1[2].strip()
        #print self._answerin
        self._answerout = self._send1[0].strip()
        #print self._answerout
        self._error = self._send2[2].strip()
        self._cpu = float(Utility.command_executer("{}".format(CPU)))
        self._rss = Utility.command_executer("{}".format(RSS))
        self._vsz = Utility.command_executer("{}".format(VSZ))
        self._end_time = Utility.command_executer("{}".format(DATE))

    def get_requestout_tps(self):
        """This Method  returns request out tps
        Returns:
            str: Tps of the 2xx answer sent.
        """
        interval_msg_count = int(self._answerin) - int(self._answer_sent_prev_msg)
        interval_duration = self.get_time_stamp() - self._answer_sent_prev_timestamp
        self._answer_sent_prev_timestamp = self.get_time_stamp()
        self._answer_sent_prev_msg = int(self._answerin)
        if not interval_duration:
            return 0
        tps = interval_msg_count/interval_duration
        return round(float(tps), 2)

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

    def get_requestin(self):
        """This method returns request in count.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            float: requestin count

        """
        try:
            return float(self._requestin)
        except ValueError:
            return -1

    def get_requestout(self):
        """This method returns request out count.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            float: requestout count

        """
        try:
            return float(self._requestout)
        except ValueError:
            return -1

    def get_answerin(self):
        """This method returns answer in count.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            float: answerin count

        """
        try:
            return float(self._answerin)
        except ValueError:
            return -1

    def get_answerout(self):
        """This method returns answer out count.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            float: answerout count

        """
        try:
            return float(self._answerout)
        except ValueError:
            return -1

    def get_error(self):
        """This method returns error count.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            float: error count

        """
        try:
            return float(self._error)
        except ValueError:
            return -1

    def get_cpu(self):
        """This method returns cpu usage.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            float: cpu usage

        """
        try:
            core = float(Utility.command_executer("{}".format(CPU_CORE)))
            return float(self._cpu/core)
        except ValueError:
            return -1

    def get_rss(self):
        """This method returns rss usage.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            int: rss usage

        """
        try:
            return int(self._rss)
        except ValueError:
            return -1

    def get_vsz(self):
        """This method returns vsz usage.

        Args:
            self (instance) - it refers to the variables and methods of the
            same class.

        Returns:
            int: vsz usage

        """
        try:
            return int(self._vsz)
        except ValueError:
            return -1

    def send_romessagestatresult(self):
        """This method sends the ro message stats information to pushgateway
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

        ro_dict = {
            "timeStamp":self.get_time_stamp(),
            "TPS":self.get_requestout_tps(),
            "collectionName": COLLECTION_NAME,
            "ReqOut":self.get_requestout(),
            "AnsIn":self.get_answerin(),
            "AnsOut":self.get_answerout(),
            "Error":self.get_error(),
            "CPU":self.get_cpu(),
            "RSS":self.get_rss(),
            "VSZ":self.get_vsz(),
            "otherInfo": {"ScriptName": SCRIPT_NAME}
        }
        self._client_obj.send_stats_to_server(ro_dict)

if __name__ == '__main__':
    DURATION = Utility.get_duration(RO_DURATION_KEY)
    CLIENT_OBJ = ClientStatsSender()
    STATS_OBJ = ROMessageStatResult(CLIENT_OBJ)
    DONE = True
    STATS_OBJ.create_mml_console()
    STATS_OBJ.execute_romessagestatresult()
    time.sleep(10)
    STATS_OBJ.execute_romessagestatresult()

    def sigint_handler(signum, frame):
        """ This method catch the signal and perform respective action.
        """
        global DONE
        DONE = False
        STATS_OBJ._close_mml_console()

    while DONE:
        START_TIME = time.time()
        STATS_OBJ.execute_romessagestatresult()
        END_TIME = time.time()
        STATS_OBJ.send_romessagestatresult()
        time.sleep(DURATION-(END_TIME-START_TIME))
