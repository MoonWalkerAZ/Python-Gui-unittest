
class GlobalData:
    def __init__(self, decimalke, failCounter):
        self.decimalke = decimalke # 2 stevilo zaokrozevanja decimalk
        self.failCounter = failCounter
        self.loader_file = ''
        self.test_fw_file = ''
        self.cpld_file = ''
        self.addr_inst1 = ''
        self.addr_inst2 = ''
        self.addr_inst3 = ''
        self.addr_inst4 = ''
        self.addr_inst5 = ''
        self.addr_inst6 = ''
        self.addr_inst7 = ''

        self.min_1v8 = 0.0
        self.max_1v8 = 0.0
        self.min_3v0 = 0.0
        self.max_3v0 = 0.0
        self.min_3v3 = 0.0
        self.max_3v3 = 0.0
        self.min_4v1 = 0.0
        self.max_4v1 = 0.0
        self.min_5v0 = 0.0
        self.max_5v0 = 0.0
        self.min_thm = 0.0
        self.max_thm = 0.0
        self.min_Uext = 0.0
        self.max_Uext = 0.0

        self.rm = None
        self.remote = None
        self.ports = None

        self.VOLTAGE_REF = 0
        self.ADC_SCALE = 0

        self.PORT = 0
        self.SPEED = 0
        self.ADDRESS = 0

        self.uniblox = None

        self.dictOfExecutedTests = {}

    def loadFiles(self, loader_file, test_fw_file, cpld_file):
        self.loader_file = loader_file
        self.test_fw_file = test_fw_file
        self.cpld_file = cpld_file

        # RAZPOREDITEV MODULOV @ Rigol M300
        #
        # Kanal 1: MATRIKA MC3648 (111-148)
        # Kanal 2: MULTIPL MC3120 (201-220)
        # Kanal 3: MULTIPL MC3132 (301-332)
        # Kanal 4: empty
        # Kanal 5: DMM

    def set_First_Two_Adresses(self, addr_inst1, addr_inst2):
        # ############################## NASLOVI INSTRUMENTOV ##############################
        self.addr_inst1 = addr_inst1 #RemoteHelper.TestjigVisaUri + 'USB0::0x1AB1::0x0C80::MM3A204100115::INSTR'  # Rigol m300
        self.addr_inst2 = addr_inst2 #RemoteHelper.TestjigVisaUri + 'USB0::0x0483::0x5710::0672FF54-55558967-67155241::INSTR'  # Array load

    def set_Other_Adresses(self, addr_inst3, addr_inst4, addr_inst5, addr_inst6, addr_inst7):
        self.addr_inst3 = addr_inst3  # ''  # 'ASRL16::INSTR'  # LED color detector
        self.addr_inst4 = addr_inst4  # ''  # 'ASRL5::INSTR'   # Uniblox
        self.addr_inst5 = addr_inst5  # ''  # 'ASRL15::INSTR'  # Array power supply
        self.addr_inst6 = addr_inst6  # ''  # 'ASRL31::INSTR'  # FTDI RS-485
        self.addr_inst7 = addr_inst7  # ''  # 'ASRL29::INSTR'  # CANable

    def set_MejeNapetostiNapajalnikov(self, min_1v8, max_1v8, min_3v0, max_3v0, min_3v3, max_3v3, min_4v1, max_4v1, min_5v0, max_5v0, min_thm, max_thm, min_Uext, max_Uext):
        # #################### PASS/FAIL MEJE ZA NAPETOSTI NAPAJALNIKOV ####################

        # zapisana vrednost je še min/max sprejemljiva vrednost (>=/<=)
        # trenutne meje zajemajo 10% nominalne vrednosti

        # vse meje so postavljene empirično!
        self.min_1v8 = min_1v8 #1.62
        self.max_1v8 = max_1v8 #1.98

        self.min_3v0 = min_3v0  #2.7
        self.max_3v0 = max_3v0  #3.3

        self.min_3v3 = min_3v3  #2.97
        self.max_3v3 = max_3v3  #3.63

        self.min_4v1 = min_4v1  #3.69
        self.max_4v1 = max_4v1  #4.51

        self.min_5v0 = min_5v0  #4.5
        self.max_5v0 = max_5v0  #5.5

        self.min_thm = min_thm  #3.5  # meja za THERMO_PWR
        self.max_thm = max_thm  #4.5

        # potrebno je določiti meje (določil Vojvodić)
        self.min_Uext = min_Uext #5.25
        self.max_Uext = max_Uext #5.5

    def set_VisaResource(self, rm, remote, ports):

        self.rm = rm
        self.remote = remote
        self.ports = ports

    def set_ADC_DATA(self, VOLTAGE_REF, ADC_SCALE):
        # ADC DATA
        self.VOLTAGE_REF = VOLTAGE_REF #3
        self.ADC_SCALE = ADC_SCALE # 4096

    def set_PSU_ADDRESS(self, SPEED, ADDRESS):
        # PSU ADDRESS
        self.PORT = self.addr_inst5
        self.SPEED = SPEED #9600
        self.ADDRESS = ADDRESS #1

    def fail(self, counter):
        # stevec napak

        self.failCounter += counter

        return self.failCounter


globalDataInst = GlobalData(2, 0)

