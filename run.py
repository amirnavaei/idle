import os, subprocess, re, plistlib, json, logging, glob
from collections import OrderedDict
from time import gmtime, strftime, localtime

admin = 'sheida'
# currentDir=os.getcwd()
tools_path = "/Users/" + admin + "/Desktop/idle_J680/idle_brk"
currentDir = "/Users/" + admin + "/Desktop/idle_J680/idle_brk"
os.chdir(currentDir)
print("path:" + currentDir)

launch_command = 'run.command'

status_file = "status.txt"
feature_list_file = "idlelist.txt"

Info_accel_plist = "Info_accel.plist"
Info_contr_plist = "Info_contr.plist"
'''
accel_dict_txt = 'accel_dict.txt'
accel_dict_plist='accel_dict.plist'
contr_dict_plist='contr_dict.plist'
'''
device_type = "ATY,Japura"  # J680: "ATY,Palena"

key_accel_3_lv = ["IOKitPersonalities", "AMDVega10" + "GraphicsAccelerator",
                  "cail_properties"]  # IO class# AMDRadeonX5000_AMDVega10GraphicsAccelerator" or "AMDBaffinGraphicsAccelerator"
key_contr_3_lv = ["IOKitPersonalities", "Controller", device_type]
key_contr_4_lv = ["IOKitPersonalities", "Controller", device_type, "aty_config", "aty_properties"]

# list of scripts that should be run for the feature off scenario
reg_file_list = ['yclk.atirs.txt', 'sclk.atirs.txt', 'aspm.atirs.txt']  # check with Rajeev reset is gen1 or gen3
reg_value_list_off = [1, 3, 0]
reg_value_list_on = [0, 3, 3]

# list of ALL script with their KEYWORDS and their file names
# script_list =['PCIE','ASPM','YCG']
# script_list_file_name=['pcie_gen1.atirs.txt','aspm.atirs.txt','yclk.atirs.txt']
script_list = ['YCG', 'SCLK', 'ASPM']
script_list_file_name = ['yclk.atirs.txt', 'sclk.atirs.txt', 'aspm.atirs.txt']

# plist_accel_kext_path="/System/Library/Extensions/AMDRadeonX5000.kext/Contents"
# plist_contr_kext_path="/System/Library/Extensions/AMD10000Controller.kext/Contents"
plist_accel_kext_path = currentDir + "/accel_plist"
plist_contr_kext_path = currentDir + "/contr_plist"

# systems="J680"
systems = "J137"
s = systems
feature_dict_txt = os.path.join(currentDir, "feature_dict.txt")
feature_on_dict_txt = os.path.join(currentDir, "feature_on_dict.txt")  # list of all features to be on
feature_dict_plist = "feature_dict_plist"


# feature_dict_plist = os.path.join (currentDir, "feature_dict.plist")


class idle_pwr:
    os.chdir(currentDir)

    def __init__(self):
        self.none = None
        self.accel = None
        self.logger = None

    ####################################
    # initialize status file with zero
    ####################################
    def status_reset(self):
        if not os.path.exists(currentDir):
            os.makedirs(currentDir)
        file = open(currentDir + '/' + status_file, "w")
        file.write(str(0))
        file.close()
        print("Initialized status file")

    ####################################
    # Remove previous log file
    ####################################
    def remove_log(self):
        if os.path.isfile(currentDir + "/log.log"):
            os.remove(currentDir + "/log.log")
            print("Removed log file")
        else:
            print("info: log.log not found")

    ####################################
    # keep record of status of idle break down
    # name: output
    # inputList: idle List that contains the list of idle features
    # dirPath: path of the directory that the output should be written
    #####################################
    def record_status(self, status_file, index, dir_path):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='w')
        logging.info("--------------------")
        logging.info("record_status:Started")
        logging.info('index:' + str(dir_path))

        # status_file = dir_path + '/' + status_file
        # writeFile = dir_path + '/' + status_file
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file = open(dir_path + '/' + status_file, "w")
        file.write(str(index))
        logging.info('index:' + str(index))
        file.close()
        logging.info('record_status:Finished')

    ####################################
    # read the status file to load the recent status_index
    ####################################
    def read_features(self):
        status_h = open(status_file, "r")
        status_index = int(list(status_h)[-1])
        status_h.close()

        if (status_index == 0):
            self.remove_log()

        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("read_features:Started")

        # call the read feature list function
        self.read_feature_list(status_index)

        logging.info('read_features:Finished')

    ####################################
    # recieves the status_index
    ####################################
    def read_features_with_index(self, status_index):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("read_features_with_index:Started")
        # call the read feature list function
        self.read_feature_list(status_index)
        logging.info('read_features_with_index:Finished')

    ####################################
    #
    ####################################
    def read_feature_list(self, status_index):
        # read feature file
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("read_feature_list:Started")
        feature_list_file_wt_path = currentDir + '/' + feature_list_file
        idleList_h = open(feature_list_file_wt_path, "r")

        # create plist from feature_list.txt
        self.text_to_dict(feature_dict_txt, feature_dict_plist, systems)

        # create plist accel_dict.plist from accel_dict.txt
        # self.text_to_dict(accel_dict_txt, accel_dict_plist, key_accel_3_lv[2], 0)

        # create plist contrl_dict.plist from contr_dict.txt -> to do
        # text_to_dict("contrl_dict.txt", 'contr_dict.plist')

        # loop through the feature list
        for line in idleList_h:
            try:
                line_idlelist = line.split(":")
                ID_index = int(line_idlelist[1].split(",")[0])  # before was: split("-")
                logging.info("ID_index: " + str(ID_index))

                # line already read
                if (ID_index < status_index):
                    logging.info("ID_index < status_index")
                    continue

                # check the line for the second time (after reboot) to run the scripts
                elif ID_index == status_index:
                    logging.info("ID_index = status_index")

                    # run the script modifier and then run the script
                    if (self.detect_kext("ALL_FEATURES_OFF", line)):
                        logging.info("detect_kext(ALL_FEATURES_OFF)")

                        for idx, script in enumerate(reg_file_list):
                            self.modify_reg_txt(reg_file_list[idx], reg_value_list_off[idx])
                            self.run_reg_script(reg_file_list[idx])

                    # Added not tested
                    # run the script modifier and then run the script
                    elif (self.detect_kext("ALL_FEATURES_ON", line)):
                        logging.info("detect_kext(ALL_FEATURES_ON)")

                        self.run_reg_script('pcie_gen1.atirs.txt')  # ask Rajeev :

                        for idx, script in enumerate(reg_file_list):
                            self.modify_reg_txt(reg_file_list[idx], reg_value_list_on[idx])
                            self.run_reg_script(reg_file_list[idx])

                    # for MC or SYS case first run the PCIE+ASPM+YCLK script then run all the scripts found in that line
                    elif (self.detect_kext("MC", line) or self.detect_kext("SYS_", line) or self.detect_kext("QUICKPG",
                                                                                                             line)):
                        logging.info("detect_kext(MC or SYS_ or QUICKPG)")

                        self.run_reg_script('pcie_gen1.atirs.txt')

                        for idx, script in enumerate(script_list):
                            self.modify_reg_txt(reg_file_list[idx], reg_value_list_on[idx])  # added
                            self.run_reg_script(reg_file_list[idx])

                    # for other cases that the line doesnt include MC or SYS, just run all the scripts found in the line
                    else:
                        logging.info("detect_kext(accel or contr)")

                        if (self.detect_kext('PCIE', line)):  # added
                            self.run_reg_script('pcie_gen1.atirs.txt')  # added

                        for idx, script in enumerate(script_list):
                            if (self.detect_kext(script, line)):
                                self.modify_reg_txt(reg_file_list[idx], reg_value_list_on[idx])  # added
                                self.run_reg_script(reg_file_list[idx])

                    # capture smci measurement
                    if line.find("smci") != -1:
                        self.smcif(tools_path, ID_index)

                # run the new line
                else:
                    logging.info("ID_index > status_index")

                    self.record_status(status_file, ID_index, currentDir)

                    self.read_feature_line(line_idlelist[1])

                    if line.find("smci") != -1:
                        self.smcif(tools_path, ID_index)
            except:
                print ("couldnt run the Index ID " + str(ID_index))
                logging.info("couldnt run the Index ID " + str(ID_index))

        logging.info("read_feature_list:Finished")

    ####################################
    #
    ####################################
    def read_feature_line(self, line):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("read_feature_line:Started")

        # reset plist --> status_index MUST be zero for the first time
        if (self.detect_kext("ALL_FEATURES_OFF", line)):
            logging.info("detect_kext (ALL_FEATURES_OFF)")
            self.feature_reset()

        elif (self.detect_kext("ALL_FEATURES_ON", line)):
            logging.info("detect_kext (ALL_FEATURES_ON)")
            self.feature_set(feature_on_dict_txt)

        # AMDRadeon
        elif (
        self.detect_kext("AMDRadeon", line)):  # To do: AMDRadeon should be replaced with unit_name from json function
            logging.info("detect_kext (AMDRadeon)")

            feature_name = line.split(" ")[1]
            key = key_accel_3_lv

            self.read_write_plist(Info_accel_plist, key, feature_name, plist_accel_kext_path)

            # clear cache and reboot
            self.clear_cache_reboot_launch()

        # Controller
        elif (self.detect_kext("Controller", line)):
            logging.info("detect_kext (Controller)")

            # feature_key = line.split(" ")[0]
            feature_name = line.split(" ")[1]
            key = key_contr_4_lv

            self.read_write_plist(Info_contr_plist, key, feature_name, plist_contr_kext_path)

            # clear cache and reboot
            self.clear_cache_reboot_launch()

        # run the scripts -> in case the line doesnt include any of above cases
        else:
            logging.info("detect_kext (else)")

            if (self.detect_kext('PCIE', line)):
                self.run_reg_script('pcie_gen1.atirs.txt')

            for idx, script in enumerate(script_list):
                logging.info("detect_kext (script)")
                if (self.detect_kext(script, line)):
                    logging.info("run_reg_script")
                    self.run_reg_script(script_list_file_name[idx])

        logging.info("read_feature_line:Finished")

    ####################################
    # Disable all the features
    ####################################
    def feature_reset(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("feature_reset:Started")

        # reset accel
        key = key_accel_3_lv
        # self.load_plist(Info_accel_plist, accel_dict_plist, key,plist_accel_kext_path)
        self.load_plist(Info_accel_plist, feature_dict_plist, key_accel_3_lv, plist_accel_kext_path)

        # reset controller
        key = key_contr_3_lv
        # self.load_plist(Info_contr_plist, contr_dict_plist, key,plist_contr_kext_path)
        self.load_plist(Info_contr_plist, feature_dict_plist, key_contr_4_lv, plist_contr_kext_path)

        # clear cache and reboot
        self.clear_cache_reboot_launch()

    ####################################
    # Enable all the features
    ####################################
    def feature_set(self, feature_on_dict_txt):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("feature_set:Started")

        # set accel
        key = key_accel_3_lv
        self.text_to_dict(feature_on_dict_txt, feature_dict_plist, systems)
        self.load_plist(Info_accel_plist, feature_dict_plist, key_accel_3_lv, plist_accel_kext_path)

        # set controller
        key = key_contr_3_lv
        self.text_to_dict(feature_on_dict_txt, feature_dict_plist, systems)
        self.load_plist(Info_contr_plist, feature_dict_plist, key_contr_4_lv, plist_contr_kext_path)

        # clear cache and reboot
        self.clear_cache_reboot_launch()

        logging.info("feature_set:Finished")

    ####################################
    # clear cache and reboot
    ####################################
    def clear_cache_reboot_launch(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("clear_cache_reboot_launch:Started")
        self.clear_cache(admin)

        self.load_auto_launch(launch_command)

        self.reboot(admin)

        os.system("sleep 60")
        self.write_in_terminal()

        # logging.info("rm_auto_launch:Started")
        # self.rm_auto_launch(launch_command)

        logging.info('clear_cache_reboot_launch:Finished')

    ####################################
    # unit_name: AMDRadeon or Controller
    # line: feature list line
    ####################################
    def detect_kext(self, unit_name, line):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        return re.search(unit_name, line)

    ####################################
    # plist_name: the Info plist (Info.plist)
    # dict_list: the input dictionary to be replaced in plist_name
    # key: array of nested keys that needs to be replaced
    ####################################
    def load_plist(self, plist_name, dict_list, key,
                   plist_kext_path):  # plist_name   #dict_list:feature_dict.plist   key:
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log",
                            mode='a')  # to do : rename to load_plist_value
        logging.info("load_plist:Started")
        # read the original plist
        # plistfile=os.path.expanduser(plist_name)   # the plist that is already loaded from kernel ext Info_accel.plist

        # read plist from kext
        plistfile = self.cp_plist_from(plist_kext_path, currentDir, plist_name)

        self.ExecSys("echo " + str(admin) + "| sudo -S chmod 777 " + plistfile)
        # os.system("echo " + str(admin) + "| sudo -S chmod 777 " + plistfile)
        plistelements = plistlib.readPlist(plistfile)

        # del the key
        # print "plist elements is "+ str(plistelements[key[0]][key[1]][key[2]])
        # del plistelements[key[0]][key[1]][key[2]]

        # read the input dictionary plist
        dict_file = os.path.expanduser(dict_list)
        item = plistlib.readPlist(dict_file)

        # print len(key)

        # load the input dictionary

        if len(key) == 3:
            # load Accelerator
            # first compare driver (plistemenets) with item (input),
            # if any key of driver does not exist in input plist, update input plist accordignly .
            #  Then load input plist (item) into the driver
            # revisit
            for k in plistelements[key[0]][key[1]][key[2]]:
                if k not in item[key[2]]:
                    item[key[2]].update(k, plistelements[key[0]][key[1]][key[2]][k])

            # print item[key[2]]
            plistelements[key[0]][key[1]][key[2]].update(item[key[2]])
            # print plistelements[key[0]][key[1]][key[2]]
        elif len(key) == 5:
            # load controller
            # print plistelements[key[0]][key[1]][key[2]][key[3]]
            # print item[key[3]]
            # print plistelements[key[0]][key[1]][key[2]][key[3]]
            # revisit
            for k in plistelements[key[0]][key[1]][key[2]][key[3]]:
                if k not in item[key[3]]:
                    item[key[3]][k] = plistelements[key[0]][key[1]][key[2]][key[3]][k]

            # print key[3], key[4]
            plistelements[key[0]][key[1]][key[2]][key[3]].update(item[key[3]])

            for k in plistelements[key[0]][key[1]][key[2]][key[4]]:
                if k not in item[key[4]]:
                    item[key[4]][k] = plistelements[key[0]][key[1]][key[2]][key[4]][k]
            plistelements[key[0]][key[1]][key[2]][key[4]].update(item[key[4]])

            # plistelements[key[0]][key[1]][key[2]][key[3]] = item[key[3]]
            # plistelements[key[0]][key[1]][key[2]][key[4]] = item[key[4]]

        # print the modified plist
        os.system("echo " + str(admin) + "| sudo -S chmod 777 " + plistfile)
        plistlib.writePlist(plistelements, plistfile)

        # plistlib.Dict.update(plistelements, plistfile)

        # save plistfile in kext
        self.save_plist_to(currentDir, plist_name, plist_kext_path)
        logging.info('load_plist:Finished')

    ####################################
    # plist_name: the Info plist (Info.plist)
    # key: array of nested keys that needs to be replaced
    # feature_name: feature under the key
    ####################################
    def read_write_plist(self, plist_name, key, feature_name, plist_kext_path):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("read_write_plist:Started")
        # read the original plist
        # plistfile=os.path.expanduser(plist_name)

        # read plist from kext
        plistfile = self.cp_plist_from(plist_kext_path, currentDir, plist_name)

        os.system("echo " + str(admin) + "| sudo -S chmod 777 " + plistfile)
        plistelements = plistlib.readPlist(plistfile)

        # for controller
        if (len(key) == 5):
            if feature_name in plistelements[key[0]][key[1]][key[2]][key[3]]:
                value = plistelements[key[0]][key[1]][key[2]][key[3]][feature_name]
                if (value == True):
                    value = False
                else:
                    value = True
                plistelements[key[0]][key[1]][key[2]][key[3]][feature_name] = value
            if feature_name in plistelements[key[0]][key[1]][key[2]][key[4]]:
                value = plistelements[key[0]][key[1]][key[2]][key[4]][feature_name]
                if (value == 0):
                    value = 1
                else:
                    value = 0
                plistelements[key[0]][key[1]][key[2]][key[4]][feature_name] = value
        # for accelarator
        else:

            value = plistelements[key[0]][key[1]][key[2]][feature_name]
            if (value == 0):
                value = 1
            else:
                value = 0
            plistelements[key[0]][key[1]][key[2]][feature_name] = value

        # print the modified plist
        os.system("echo " + str(admin) + "| sudo -S chmod 777 " + plistfile)
        plistlib.writePlist(plistelements, plistfile)

        # save plistfile in kext
        self.save_plist_to(currentDir, plist_name, plist_kext_path)
        logging.info('read_write_plist:Finished')

    ####################################
    # convert text file into dictionary
    # file_name: text file name
    ####################################
    def old_text_to_dict(self, file_name, out_name, KEY, input_value):  # set: input_value=1   reset: input_value=1
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("text_to_dict:Started")
        dictList = OrderedDict()
        dictList[KEY] = OrderedDict()
        file_name_wt_path = currentDir + '/' + file_name
        with open(file_name_wt_path, 'r') as file:
            for line in file:
                key, value = line.split(":")
                # dictList[KEY][key]=int(value)
                dictList[KEY][key] = int(input_value)
        plistlib.writePlist(dictList, out_name)
        logging.info('text_to_dict:Finished')

    ####################################
    # convert features of text file into dictionary
    # file_name: text file name
    ####################################
    def text_to_dict(self, file_name, out_name, systems):  # sys_name:J680, set: input_value=1   reset: input_value=1
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("text_to_dict:Started")
        #
        dictList = OrderedDict()

        # dictList[KEY] = OrderedDict()
        Accel_KEY = ["cail_properties"]
        Cont_KEY = ["aty_config", "aty_properties"]
        flag_accel = 0
        flag_contr = 0
        with open(file_name, 'r') as file_h:
            for line in file_h:
                # for s in systems: for  systems=["J137","J138","J680"], add this line and indent
                if line.find(s) != -1:
                    sys = s
                    # print sys
                    flag_accel = 0
                    flag_contr = 0
                    continue
                elif line.find("Accelerator") != -1:
                    flag_accel = 1
                    flag_contr = 0
                elif line.find("Controller") != -1:
                    Cont_KEY_dict = OrderedDict()
                    flag_accel = 0
                    flag_contr = 1
                else:
                    if flag_accel == 1:
                        flag = 1
                        # search through the keys
                        for k in Accel_KEY:

                            if line.find(k) != -1:
                                KEY = k
                                flag = 0
                                dictList[KEY] = OrderedDict()
                        # read line into dictionary
                        if flag == 1:
                            key, value = line.split(":")
                            # print "KEY key and value are:"+str (KEY)+ str(key)+ "and"+ str(value)
                            dictList[KEY][key] = int(value)


                    #
                    elif flag_contr == 1:
                        flag = 1
                        # search through the keys
                        for k in Cont_KEY:

                            if line.find(k) != -1:
                                KEY = k
                                flag = 0
                                dictList[KEY] = OrderedDict()
                        # read line into dictionary
                        if flag == 1:
                            key, value = line.split(":")
                            dictList[KEY][key] = value

            plistlib.writePlist(dictList, out_name)
        logging.info("text_to_dict:Finished")

    ###############################################
    # change PCIE speed
    ###############################################
    def pcie_gen(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("pcie_gen:Started")
        path_command = currentDir + "/idle_brk/idle\ scripts/pcie_gen1.atirs.txt"
        pcie_run_command = "atirs " + path_command
        os.system(pcie_run_command)
        logging.info('pcie_gen:Finished')

    ###############################################
    # change SCLK_DS_Divdi
    ###############################################
    def sclk_ds_div(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("sclk_ds_div:Started")
        sclk_ds_div_run_command = "atirs SCLK_DEEP_SLEEP_MISC_CNTL__DPM_SS_DIV_ID 3"  # To do: check with Rajeev, command does not work
        os.system(sclk_ds_div_run_command)
        logging.info('sclk_ds_div:Finished')

    ###############################################
    # change yclk
    ###############################################
    def yclk(self):  # To do: make it more dynamic (changing 0 and 1 in the functions)
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("yclk:Started")
        path_command = currentDir + "/idle_brk/idle\ scripts/yclk.atirs.txt"
        run_command = "atirs " + path_command
        os.system(run_command)
        logging.info('yclk:Finished')

    ###############################################
    # clear cache
    ###############################################
    def clear_cache(self, admin):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        os.system("echo " + str(admin) + "| sudo -S kextcache -i /")

    ###############################################
    # reboot
    ###############################################
    def reboot(self, admin):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        os.system("echo " + str(admin) + "| sudo -S reboot")

    ###############################################
    # capture measurement with smcif
    ###############################################
    # run smcifLite and write MSTD according to the status_index(idlelist.txt)
    def smcif(self, tools_path, status_index):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("smcif:Started")
        smcif_path = tools_path + "/smciflite"
        # os.system("echo " + str(admin) +"| sudo ./smcifLite -w MSTD" + str(status_index))  #/Users/atiqa/Desktop/tools/smcifLite -w MSTD

        p = subprocess.check_output("echo \"atiqa\" | sudo -S ./smcifLite -w MSTD " + str(status_index), shell=True)
        m = re.match('^ERROR: Error During Cached Reading of Key REV  operation \(132\)', p)
        if (m == None):
            print(p)
        os.system("sleep 15")

        logging.info('smcif:Finished')

    ###############################################
    # change reg_file(scripts)
    ##input: 0,  1 (by default all regs are zeros and in this function, zeros are checked to be replaced
    # aspm: enable -->input=3
    ###############################################
    def modify_reg_txt(self, reg_file, input_value):
        # logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
        #                    datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("modify_reg_txt:Started")

        reg_file_h = open(currentDir + "/idle scripts/" + reg_file, 'r')
        list = []
        for line in reg_file_h.readlines():
            reg = line.split(" ")[0]
            reg_value = int(input_value)
            str_reg_value = str(reg_value)
            new_line = (reg, str_reg_value)
            line = ' '.join(new_line)
            list.append(line)

        lines = '\n'.join(list)

        reg_file_h.close()
        reg_file_h = open(currentDir + "/idle scripts/" + reg_file, 'w')

        for line in lines:
            reg_file_h.write(line)
        reg_file_h.close()
        logging.info('modify_reg_txt:Finished')

    ###############################################
    # run reg scripts
    ###############################################
    def run_reg_script(self, reg_file):  # To do: make it more dynamic (changing 0 and 1 in the functions)
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("run_reg_script:Started")
        path_command = currentDir + "/idle\ scripts/" + reg_file
        run_command = "atirs " + path_command
        os.system(run_command)
        logging.info('run_reg_script:Finished')

    ###############################################
    # read json file to find the driver (IO controller and accellerator) configuration
    # input: the path of jason file
    ###############################################
    # load json file
    def jason_read(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("json_read:Started")
        json_files = sorted(glob.glob(currentDir + '/*.json'), key=os.path.getmtime)

        if (len(json_files) != 0):

            # config file exists
            json_file = json_files[0]
            json_fh = open(json_file, 'rb')
            for line in json_fh:
                line = line.strip()

                # find the IOFB
                m = re.match('^"IOFB": "(\w+)', line)
                if (m != None):
                    # print m.group(1)
                    if (m.group(1) != "\"-\""):
                        contr_unit_name = m.group(1)
                        contr = "/System/Library/Extensions/" + contr_unit_name + ".kext/Contents/Info.plist"  # to do: redundant --> remove later
                        plist_contr_kext_path = "/System/Library/Extensions/" + contr_unit_name + ".kext/Contents"
                        os.system("ls " + contr)
                    else:
                        os.system("echo error")

                # find the Personality of Driver Controller
                m = re.match('^"Personality": "(\w+)', line)
                if (m != None):
                    # print m.group(1)
                    if (m.group(1) != "\"-\""):
                        personality = m.group(1)
                    else:
                        os.system("echo error")

                # find the IO Accellerator
                m = re.match('^"IOAccel": "(\w+)', line)
                if (m != None):
                    # print m.group(1)
                    m = re.sub(r'HWServices', '', m.group(1))
                    if (m != "\"-\""):
                        accel_unit_name = m
                        accel = "/System/Library/Extensions/" + accel_unit_name + ".kext/Contents/Info.plist"  # to do: redundant --> remove later
                        plist_accel_kext_path = "/System/Library/Extensions/" + accel_unit_name + ".kext/Contents"
                        os.system("ls " + accel)
                    else:
                        os.system("echo error")

        # print accel_unit_name, contr_unit_name, personality, plist_contr_kext_path, plist_accel_kext_path
        return accel_unit_name, contr_unit_name, personality, plist_contr_kext_path, plist_accel_kext_path

        # accel: /System/Library/Extensions/AMDRadeonX4000.kext/Contents/Info.plist
        # contr: /System/Library/Extensions/AMD9500Controller.kext/Contents/Info.plist
        # personality: Palena
        logging.info('json_read:Finished')

    ###############################################
    # copy the plist from the driver to idle_brk folder
    ###############################################
    def cp_plist_from(self, plist_kext_path, idle_brk_path, new_plist_name):

        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("cp_plist_from:Started")
        run_command = "echo " + str(admin) + "| sudo -S cp " + plist_kext_path + "/Info.plist  " + idle_brk_path
        os.system(run_command)
        run_command = "echo " + str(admin) + "| sudo -S mv " + idle_brk_path + "/Info.plist" + " " + new_plist_name
        os.system(run_command)
        return new_plist_name
        logging.info('cp_plist_from:Finished')

    ###############################################
    # save plist into the driver path
    # from : idle_brk_path to /System/Library/Extensions/AMD9500Controller.kext/Contents/Info.plist
    ###############################################
    def save_plist_to(self, currentDir, plist_name, plist_kext_path):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("save_plist_to:Started")
        run_command = "echo " + str(admin) + "| sudo -S mv " + currentDir + "/" + plist_name + " " + "Info.plist"
        os.system(run_command)
        run_command = "echo " + str(admin) + "| sudo -S cp " + currentDir + "/Info.plist " + plist_kext_path
        os.system(run_command)
        run_command = "echo " + str(admin) + "| sudo -S mv " + currentDir + "/Info.plist " + " " + plist_name
        os.system(run_command)
        logging.info('save_plist_to:Finished')

    ###############################################
    # add run.command (run.py) into login item
    ###############################################
    def load_auto_launch(self, launch_command):
        #    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("load_auto_launch:Started")
        logger = logging.getLogger(launch_command)
        logger.info("Adding run.command to login item")
        addLoginItem = 'osascript -e ' + "'tell application " + '"System Events"' + ' to make login item at end with properties {path: "' + currentDir + "/" + launch_command + '"' + ", hidden:true}'"
        os.system(addLoginItem)
        logging.info('load_auto_launch:Finished')

    ###############################################
    # remove run.command (run.py) from login item
    ###############################################
    def rm_auto_launch(self, launch_command):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info(" rm_auto_launch:Started")
        logger = logging.getLogger(launch_command)
        logger.info("Remove run.command to login item")
        addLoginItem = 'osascript -e ' + "'tell application " + '"System Events"' + ' to delete login item "' + launch_command + '"' + "'"
        os.system(addLoginItem)
        logging.info('rm_auto_launch:Finished')

    ###############################################
    # auto launch script
    ###############################################
    def auto_launch(self, launch_file):  # To do: make it more dynamic (changing 0 and 1 in the functions)
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("auto_launch:Started")
        path_command = currentDir + "/" + launch_file
        os.system('sh ' + path_command)
        logging.info('auto_launch:Finished')
        return

    ###############################################
    # print time in to terminal
    ###############################################
    def write_in_terminal(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("write_in_terminal:Started")
        time_now = strftime("%Y-%m-%d %H:%M:%S", localtime())
        # print time_now
        os.system('echo ' + time_now)
        fh = open(currentDir + "/output.txt", 'a')
        fh.write(time_now + "\n")
        logging.info('write_in_terminal:Finished')

    ###############################################
    # log file
    ###############################################
    def log_file(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S', filename="log.log", mode='a')
        logging.info("Started")
        logging.error("Error")
        logging.info('Finished')

    ###############################################
    # sell command
    ###############################################
    def ExecSys(self, cmd):
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        return (proc.communicate()[0])


# create an instance of the class idle_pwr()
out = idle_pwr()
# out.status_reset()
out.read_features()

# out.load_auto_launch("run.command")
# out.rm_auto_launch("run.command")

#
#
# # del the key
# del plistelements[key[0]][key[1]][key[2]]
#
# # read the input dictionary
# dict_file = os.path.expanduser(dict_list)
# item = plistlib.readPlist(dict_file)
#
# # load the input dictionary
# plistelements[key[0]][key[1]][key[2]] = item[key[2]]
#
# # print the modified plist
# plistlib.writePlist(plistelements, plistfile)


# ---------------------------
# Tested:
# ---------------------------
# out.load_plist("Info_contr.plist","contr_dict.plist",key_contr_3_lv,plist_contr_kext_path)
# out.feature_reset()
# out.log_file()
# out.jason_read()
# out.load_plist("Info_accel.plist","feature_dict.plist",key_accel_3_lv,currentDir)
# out.load_plist("Info_contr.plist","feature_dict.plist",key_contr_4_lv,currentDir)


# out.feature_reset()

# out.load_auto_launch('run.command')

# out.feature_set()


# out.read_features(1)
# out.modify_reg_txt("yclk.atirs.txt",3)
