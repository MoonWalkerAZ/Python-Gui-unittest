import visa
from util.remoting import RemoteHelper
from globalData import globalDataInst
from pyvisa.errors import VisaIOError
from visa import constants
from init.psu364x.base import Psu, UnexpectedResponse
from init.canard.hw import visacan
import time
import os
from pathlib import PurePath
import pathlib
import subprocess
import sys

class TestJig:
    def __init__(self):

        globalDataInst.loadFiles(str('0BTngLoader_130_4_B0.raw.hex'), str('7BTngTestHw_1_1_B4.raw.hex'), str('CPLD_LC4064ZE-7TN48C_24h.svf'))

        self.addr_inst1 = RemoteHelper.TestjigVisaUri + 'USB0::0x1AB1::0x0C80::MM3A204100115::INSTR'  # Rigol m300
        self.addr_inst2 = RemoteHelper.TestjigVisaUri + 'USB0::0x0483::0x5710::0672FF54-55558967-67155241::INSTR'  # Array load
        globalDataInst.set_First_Two_Adresses(self.addr_inst1, self.addr_inst2)

        globalDataInst.set_MejeNapetostiNapajalnikov(1.62, 1.98, 2.7, 3.3, 2.97, 3.63, 3.69, 4.51, 4.5, 5.5, 3.5, 4.5, 5.25, 5.5)

    def visa_testConnection(self):
        # ##################################################################################
        # VISA RESOURCE
        # ##################################################################################

        try:
           self.rm = visa.ResourceManager()
           self.remote = RemoteHelper()
           self.ports = self.remote.map_serial_ports(self.rm)
           globalDataInst.set_VisaResource(self.rm, self.remote, self.ports)

           instr = next((p for p in self.ports if (p.name == self.remote.DevArduino)), None)
           if instr is not None:
               self.addr_inst3 = instr.resource

           instr = next((p for p in self.ports if (p.name == self.remote.DevUniblox)), None)
           if instr is not None:
               self.addr_inst4 = instr.resource

           instr = next((p for p in self.ports if (p.name == self.remote.DevArrayPsu)), None)
           if instr is not None:
               self.addr_inst5 = instr.resource

           instr = next((p for p in self.ports if (p.name == self.remote.DevRS485)), None)
           if instr is not None:
               self.addr_inst6 = instr.resource

           instr = next((p for p in self.ports if (p.name == self.remote.DevCanable)), None)
           if instr is not None:
               self.addr_inst7 = instr.resource

           globalDataInst.set_Other_Adresses(self.addr_inst3, self.addr_inst4, self.addr_inst5, self.addr_inst6, self.addr_inst7)
           globalDataInst.set_ADC_DATA(3, 4096)
           globalDataInst.set_PSU_ADDRESS(9600, 1)

           print("Povezava z VISO uspešna")
           return "Povezava z VISO uspešna"

        except:
            print("Ni povezave z VISO")
            return "Ni povezave z VISO"

    #  testiraj povezljivost z RIGOL M300
    def rigolM300_testConnection(self):
        try:
            inst1 = globalDataInst.rm.open_resource(globalDataInst.addr_inst1)
            inst1.close()
            print("Povezava z Rigol M300 uspešna")
            return "Povezava z Rigol M300 uspešna"

        except VisaIOError:
            print("Napaka! Preveri povezavo z Rigol M300")
            return "Napaka! Preveri povezavo z Rigol M300"


    # testiraj povezljivost z Array 3721A ELoad
    def array3721A_ELoad_testConnection(self):
        try:
           inst2 = globalDataInst.rm.open_resource(globalDataInst.addr_inst2)
           inst2.close()
           print("Povezava z Array 3721A ELoad uspešna")
           return "Povezava z Array 3721A ELoad uspešna"

        except VisaIOError:
           print("Napaka! Preveri povezavo z Array 3721A")
           return "Napaka! Preveri povezavo z Array 3721A"

    # testiraj povezljivost z LED Color Detector
    def LED_Color_Detector_testConnection(self):
        try:
           inst3 = globalDataInst.rm.open_resource(globalDataInst.addr_inst3)
           inst3.close()
           print("Povezava z LED Color Detector uspešna")
           return "Povezava z LED Color Detector uspešna"

        except VisaIOError:
            print("Napaka! Preveri povezavo z LED Color Detector")
            return "Napaka! Preveri povezavo z LED Color Detector"

        # povezava z Uniblox-om
    def uniblox_TestConnection(self):
        try:
            globalDataInst.uniblox = globalDataInst.rm.open_resource(globalDataInst.addr_inst4)  # komunikacija z Uniblox testnim FW

            globalDataInst.uniblox.baud_rate = 115200
            globalDataInst.uniblox.data_bits = 8
            globalDataInst.uniblox.stop_bits = constants.StopBits.one
            globalDataInst.uniblox.parity = constants.Parity.none
            globalDataInst.uniblox.timeout = 500  # millis

            globalDataInst.uniblox.read_termination = None
            globalDataInst.uniblox.write_termination = None
            globalDataInst.uniblox.flow_control = constants.VI_ASRL_FLOW_NONE

            globalDataInst.uniblox.set_visa_attribute(visa.constants.VI_ATTR_ASRL_RTS_STATE, 1)
            globalDataInst.uniblox.set_visa_attribute(visa.constants.VI_ATTR_ASRL_DTR_STATE, 0)

            print("Povezava z Uniblox-om uspešna")
            return "Povezava z Uniblox-om uspešna"

        except VisaIOError:
            print("Napaka! Preveri povezavo z Uniblox napravo.")
            return "Napaka! Preveri povezavo z Uniblox napravo."

    # testiraj povezljivost z Array 3646A Power Supply
    def array3646A_PowerSupply_Connection(self):
        try:
            inst5 = Psu(globalDataInst.PORT, globalDataInst.ADDRESS, globalDataInst.SPEED)
            inst5.open()
            inst5.close()

            print("Povezava z Array 3646A Power Supply uspešna")
            return "Povezava z Array 3646A Power Supply uspešna"

        except UnexpectedResponse as e:

            print("Napaka! Preveri povezavo z Array Power Supply".format(str(e)))
            return "Napaka! Preveri povezavo z Array Power Supply".format(str(e))

        # testiraj povezljivost z USB FTDI RS485
    def ftdi_RS485_Connection(self):

        try:
            inst6 = globalDataInst.rm.open_resource(globalDataInst.addr_inst6)
            inst6.close()

            print("Povezava z USB FTDI RS485 uspešna")
            return "Povezava z USB FTDI RS485 uspešna"

        except VisaIOError:
            print("Napaka! Preveri povezavo z USB FTDI RS485")
            return "Napaka! Preveri povezavo z USB FTDI RS485"

        # testiraj povezljivost s CANable
    def CANable_Connection(self):
        try:
            inst7 = visacan.VisaCanDev(globalDataInst.addr_inst7)
            inst7.set_bitrate(250000)  # set CAN bus bitrate to 250 kbit
            inst7.start()  # connect to CAN bus
            inst7.close()

            print("Povezava s CANable uspešna")
            return "Povezava s CANable uspešna"

        except VisaIOError:
            print("Napaka! Preveri povezavo s CANable")
            return "Napaka! Preveri povezavo s CANable"



    def testjig_setup(self):

        # ##############################################################################################
        # PRVI VKLOP DUT
        # ##############################################################################################

        print("\nPrvi vklop, stabilizacija DUT\n")
        self.power_set(12.5)  # set 12.0 V
        self.vklopi(1, 2, 4)  # dut pwr on

        # stabilizacija DUT
        delay = 15
        while delay >= 0:
            print("stabiliziram...", delay)
            delay -= 1
            time.sleep(1.0)

        poraba = self.power_get("current")  # izmeri porabo toka na usmerniku
        print("\nPoraba DUT:", poraba, "A\n")

        # ##############################################################################################
        # NALOZI Lattice CPLD
        # ##############################################################################################

        print('\n+++ Configure LC4064ZE CPLD ... +++\n')

        svfConfig = PurePath('firmware', globalDataInst.cpld_file)

        try:
            error = False
            globalDataInst.remote.program_lattice(config=svfConfig, cleanup=True)
        except ValueError as err:
            print('Failed: ' + str(err), file=sys.stderr)
            error = True

        time.sleep(1)
        print('\n+++ CPLD configuration done +++\n')

        if error:
            exit(-3)

        # ##############################################################################################
        # NALOZI TESTNI FIRMWARE NA CPU STM32F767
        # ##############################################################################################

        print('\n+++ Program STM32F767 ... +++\n')

        loaderImage = PurePath('firmware', globalDataInst.loader_file)
        testFwImage = PurePath('firmware', globalDataInst.test_fw_file)

        try:

            error = False
            globalDataInst.remote.program_stm32(images=[loaderImage, testFwImage], unlock=True, cleanup=True)
        except ValueError as err:
            print('Failed: ' + str(err), file=sys.stderr)
            error = True

        time.sleep(1)
        print('\n+++ STM32 programming done +++\n')

        if error:
            exit(-2)

        # ##############################################################################################
        # PRAZNJENJE KONDENZATORJEV PREKO BREMENA
        # ##############################################################################################

        print("Supercap voltage:")
        supercap_voltage = self.napetost(202)

        print("\nIzklop DUT")
        self.power_set(0.0)  # napetost 0 V
        self.izklopi(1, 2, 4)  # izklop napajanje DUT (2 vrstica, 4 kolona)
        self.connect_battery(0)  # preventivni izklop baterijskega simulatorja

        print("\nVklop bremena: ", self.breme(1.5), "A")
        print("\nPraznjenje kondenzatorjev...\n")

        while supercap_voltage > 1.0:  # dokler je napetost po izklopu vecja, nadaljuj s praznjenjem supercap-ov
            supercap_voltage = self.napetost(202)

        print("\nIzklop bremena: ", self.breme(0), "A")

        # ##############################################################################################
        # DRUGIdigital_io_high_low VKLOP DUT
        # ##############################################################################################

        print("\nDrugi vklop, stabilizacija DUT\n")
        self.power_set(12.5)  # set 12.0 V
        self.vklopi(1, 2, 4)  # dut pwr on

        # stabilizacija DUT
        delay = 15
        while delay >= 0:
            print("stabiliziram...", delay)
            delay -= 1
            time.sleep(1.0)

        poraba = self.power_get("current")  # izmeri porabo toka na usmerniku
        print("\nPoraba DUT:", poraba, "A\n")

        # vklop default baterije
        self.connect_battery(1)
        self.enable_bat_thermo()  # preventivno omogoci uporabo baterije preko termostata 1
        time.sleep(0.1)
        bat_sim = self.get_bat_voltage()

        return "koncano"


    #SOUND
    def sound_start(self):
        if os.name == "nt":
            import winsound
            winsound.Beep(1500, 200)
            winsound.Beep(2500, 200)
            winsound.Beep(3500, 200)
        else:
            os.system('play -n synth %s sin %s' % (0.2, 1500))
            os.system('play -n synth %s sin %s' % (0.2, 2500))
            os.system('play -n synth %s sin %s' % (0.2, 3500))

    def sound_end_pass(self):
        if os.name == "nt":
            for x in range(3):
                import winsound
                winsound.Beep(3500, 200)
                winsound.Beep(2500, 200)
                winsound.Beep(1500, 200)
                time.sleep(0.5)
                x += 1
        else:
            for x in range(3):
                os.system('play -n synth %s sin %s' % (0.2, 3500))
                os.system('play -n synth %s sin %s' % (0.2, 2500))
                os.system('play -n synth %s sin %s' % (0.2, 1500))
                time.sleep(0.5)
                x += 1

    def sound_end_fail(self):
        if os.name == "nt":
            for x in range(6):
                import winsound
                winsound.Beep(2000, 200)
                time.sleep(0.1)
                winsound.Beep(1000, 200)
                time.sleep(0.1)
                x += 1
        else:
            for x in range(6):
                os.system('play -n synth %s sin %s' % (0.2, 2000))
                time.sleep(0.1)
                os.system('play -n synth %s sin %s' % (0.2, 1000))
                time.sleep(0.1)
                x += 1

    def sound_error(self):
        if os.name == "nt":
            import winsound
            for x in range(6):
                winsound.Beep(5000, 200)
                time.sleep(0.2)
                x += 1
        else:
            for x in range(6):
                os.system('play -n synth %s sin %s' % (0.2, 5000))
                time.sleep(0.2)
                x += 1


    def breme(self, load):

        try:
            # vklop elektricnega bremena CCH

            eload = globalDataInst.rm.open_resource(globalDataInst.addr_inst2)
            time.sleep(0.5)

            eload.write("SYST:REM\n")

            if load == 0:
                eload.write("CURR 0\n")  # izkljuci breme
                time.sleep(0.1)
                eload.write("INP OFF\n")  # izkljuci breme
                time.sleep(0.1)
                eload.close()
                time.sleep(0.1)
                return 0

            else:
                if load <= 1.5:
                    str1 = "CURR "
                    str2 = str(load)
                    str3 = "\n"
                    ukaz = str1 + str2 + str3

                    eload.write("MODE CCH\n")  # nastavi constant current mode
                    time.sleep(0.1)
                    eload.write(ukaz)  # set load
                    time.sleep(0.1)
                    eload.write("INP ON\n")  # vkljuci breme
                    time.sleep(0.1)
                    eload.close()
                    time.sleep(0.1)
                    return load

                else:
                    eload.write("INP OFF\n")
                    time.sleep(0.1)
                    print("\nNapaka! Nastavljeno breme je preveliko.\n")
                    eload.close()
                    time.sleep(0.1)
                    return 0

        except VisaIOError:
            print("Napaka pri komunikaciji (Array Load)")
            globalDataInst.fail(1)
            eload.close()
            return -1

    def script_fail(self):

        print("\nError occured...")
        self.sound_error()

    def power_set(self, command):

        try:

            # krmiljenje napajalnika Array 3646A

            psu = Psu(globalDataInst.PORT, globalDataInst.ADDRESS, globalDataInst.SPEED)
            psu.open()

            if command == 0:
                psu.disable_output()
                time.sleep(0.1)
                psu.set_voltage(command)
                time.sleep(0.1)
                # print("\nPower OFF")

                psu.close()

            else:
                psu.disable_output()
                time.sleep(0.1)
                psu.set_max_current(1.5)
                time.sleep(0.1)
                psu.set_voltage(command)
                time.sleep(0.1)
                psu.enable_output()
                time.sleep(0.1)
                # print("\nPower ON,", command, "V")

                psu.close()

            # current = psu.measure_current()
            # voltage = psu.measure_voltage()

        except VisaIOError:
            print("Napaka pri komunikaciji (Array Power Supply)")
            self.script_fail()

    def connect_battery(self, bat_select):

        # vklop/izklop baterijskega napajanja
        #
        # 0 = disconnect battery power
        # 1 = connect to default battery
        # 2 = connect to optional battery
        #
        #####################################

        try:
            if bat_select == 1:
                # print("\nVklop default baterije...")
                self.izklopi(1, 4, 3)
                self.vklopi(1, 4, 2)
                return 1

            elif bat_select == 2:
                # print("\nVklop opcijske baterije...")
                self.izklopi(1, 4, 2)
                self.vklopi(1, 4, 3)
                return 2

            else:
                # print("\nIzklop baterijskega napajanja...")
                self.izklopi(1, 4, 2)
                self.izklopi(1, 4, 3)
                return 0

        except VisaIOError:
            print("Napaka pri vklopu/izklopu baterijskega napajanja!")
            return 0

    def izklopi(self, num, row, col):

        try:

            # funkcija za izklop posameznih relejev multiplekserja ali matrike

            # PRIMER KRMILJENJA RELEJSKIH KARTIC:

            # izklopi (1, 2, 4)  # izklopi rele matrike: 1=kanal; 2=vrstica; 4=kolona
            # izklopi (2, 0, 8)  # izklopi rele multipl: 2=kanal; 0,8=rele 08
            # izklopi (2, 1, 6)  # izklopi rele multipl: 2=kanal; 1,6=rele 16

            rigol = globalDataInst.rm.open_resource(globalDataInst.addr_inst1)

            str1 = "ROUT:OPEN (@"
            str2 = str(num)  # kanal relejske kartice (poglej razporeditev v Rigolu M300)
            str3 = str(row)  # vrstica pri matriki, oznaka releja pri multiplekserju
            str4 = str(col)  # kolona pri matriki, oznaka releja pri multiplekserju
            str5 = ")"

            ukaz = str1 + str2 + str3 + str4 + str5

            rigol.write(ukaz)
            rigol.close()
            return ukaz

        except VisaIOError:
            print("Napaka pri komunikaciji (Rigol M300)")
            self.script_fail()

    def vklopi(self, num, row, col):

        try:
            # funkcija za vklop posameznih relejev multiplekserja ali matrike

            # PRIMER KRMILJENJA RELEJSKIH KARTIC:

            # vklopi (1, 2, 4)  # vklopi rele matrike: 1=kanal; 2=vrstica; 4=kolona
            # vklopi (2, 0, 8)  # vklopi rele multipl: 2=kanal; 0,8=rele 08
            # vklopi (2, 1, 6)  # vklopi rele multipl: 2=kanal; 1,6=rele 16

            rigol = globalDataInst.rm.open_resource(globalDataInst.addr_inst1)

            str1 = "ROUT:CLOS (@"
            str2 = str(num)  # kanal relejske kartice (poglej razporeditev v Rigolu M300)
            str3 = str(row)  # vrstica pri matriki, oznaka releja pri multiplekserju
            str4 = str(col)  # kolona pri matriki, oznaka releja pri multiplekserju
            str5 = ")"

            ukaz = str1 + str2 + str3 + str4 + str5

            rigol.write(ukaz)
            rigol.close()
            return ukaz

        except VisaIOError:
            print("Napaka pri komunikaciji (Rigol M300)")
            self.script_fail()

    def uniblox_ps(self, ukaz):

        try:
            if ukaz == 1:  # vklop internih napajalnikov Uniblox-a

                globalDataInst.uniblox.write("\x02GPIO,WRITE,G,3,1\x03")  # vklop napajalnika 5V4_BOOST_PS
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,B,8,1\x03")  # vklop napajalnika 3V3_COM_CH in VDD_ISO
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,F,3,1\x03")  # vklop napajalnika 3V3_PRPHRL
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,E,14,1\x03")  # vklop napajalnika 3V3_GPS_PWR
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,B,11,1\x03")  # vklop napajalnika 3V3_GPS_BAT
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,D,15,1\x03")  # vklop napajalnika 5V0_PWR
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,B,9,1\x03")  # vklop napajalnika 5V0_SAT
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,D,11,1\x03")  # vklop napajalnika 4V1_PWR
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,E,13,1\x03")  # vklop napajalnika 4V1_GSM
                time.sleep(0.1)

            elif ukaz == 0:  # izklop

                globalDataInst.uniblox.write("\x02GPIO,WRITE,G,3,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,B,8,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,F,3,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,E,14,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,B,11,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,D,15,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,B,9,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,D,11,0\x03")
                time.sleep(0.1)
                globalDataInst.uniblox.write("\x02GPIO,WRITE,E,13,0\x03")
                time.sleep(0.1)

        except VisaIOError:
            print("Napaka pri komunikaciji (Uniblox)")
            self.script_fail()


    def on_exit(self, sig, func=None):

        print("\nScript interrupted, closing...\n")
        self.breme(0)  # izklop bremena
        self.power_set(0.0)  # izklop zunanjega napajalnika
        self.connect_battery(0)  # izklop baterije
        self.izklopi(1, 2, 4)  # preventivni izklop main napajanja
        self.izklopi(1, 2, 5)  # preventivni izklop main reverse polarity napajanja
        self.izklopi(1, 3, 4)  # preventivni izklop service port napajanja
        self.izklopi(1, 3, 5)  # preventivni izklop service port reverse polarity napajanja
        self.uniblox_ps(0)  # izklop internih napajalnikov
        globalDataInst.uniblox.close()  # prekini komunikacijo z uniblox modulom

    def burn_hw_test(self):

        # burn test firmware
        try:
            cd = pathlib.Path(__file__).parent
            cmd_file = PurePath(cd, 'firmware', 'burn_loader.cmd')
            subprocess.call([str(cmd_file)])
            print("\nLoader Burned!\n")

            cmd_file = PurePath(cd, 'firmware', 'burn_hw_test.cmd')
            subprocess.call([str(cmd_file)])
            print("\nHW Test Burned!\n")

        except UnexpectedResponse:
            self.script_fail()

    def ledcolor(self):

        # detekcija barve led diod

        # predpogoj za delovanje je prikljucen LED detektor (YL-64 + Arduino)

        try:
            detector = globalDataInst.rm.open_resource(globalDataInst.addr_inst3)
            detector.timeout = 3000  # 3 sek

            response = detector.query("RAW\n")
            # print(response)  # kalibracija

            time.sleep(0.5)

            r, g, b = response.split(':')  # razdeli odziv led detektorja na posamezne barve (R, G, B)

            if int(r) > 240:
                if int(b) > 635:
                    # print("ZELENA")
                    detector.close()
                    time.sleep(0.1)
                    return 1
                else:
                    # print("MODRA")
                    detector.close()
                    time.sleep(0.1)
                    return 2

            else:
                if int(b) > 225:
                    # print("RUMENA")
                    detector.close()
                    time.sleep(0.1)
                    return 3
                else:
                    # print("RDECA")
                    detector.close()
                    time.sleep(0.1)
                    return 4

        except VisaIOError:
            print("\nLED color read not responding, second try...\n")
            return -1

    def stat(self):

        try:

            # izpis stanja vseh relejev (0=open, 1=close)

            rigol = globalDataInst.rm.open_resource(globalDataInst.addr_inst1)

            print("\n")
            print("Matrika: ", rigol.query("ROUT:CLOS? (@111:148)"))
            print("MC3120 : ", rigol.query("ROUT:CLOS? (@201:220)"))
            print("MC3132 : ", rigol.query("ROUT:CLOS? (@301:332)"))

            rigol.close()

        except VisaIOError:
            print("Napaka pri komunikaciji (Rigol M300)")
            self.script_fail()

    def napetost(self, kanal):

        try:

            # meritev napetosti na izbranem kanalu

            rigol = globalDataInst.rm.open_resource(globalDataInst.addr_inst1)

            str1 = "MEAS:VOLT:DC? AUTO,DEF,(@"
            str2 = str(kanal)
            str3 = ")"
            ukaz = str1 + str2 + str3

            voltage = rigol.query(ukaz)
            voltage = float(voltage)
            voltage = round(voltage, globalDataInst.decimalke)
            print(voltage)

            rigol.close()

            return voltage

        except VisaIOError:
            print("Napaka pri komunikaciji (Rigol M300)")
            self.script_fail()

    def power_get(self, parameter):

        try:

            # preberi vrednosti napajalnika Array 3646A

            psu = Psu(globalDataInst.PORT, globalDataInst.ADDRESS, globalDataInst.SPEED)
            psu.open()

            if parameter == "voltage":
                voltage = psu.measure_voltage()
                psu.close()
                return voltage

            elif parameter == "current":
                current = psu.measure_current()
                # print(current)
                psu.close()
                return current

            else:
                print("Powe Supply: Ukaz ni veljaven!")
                psu.close()
                return -1

        except VisaIOError:
            print("Napaka pri komunikaciji (Array Power Supply)")
            self.script_fail()

    def digital_io_test(self, portset, portnum):

        try:

            # test Digital_IO

            # izklop DIGITAL_IO
            self.izklopi(3, 1, 3)
            self.izklopi(3, 1, 4)
            self.izklopi(3, 1, 5)

            if portset == 0:  # simulacija 7,5 V DIGITAL_IO, portset = low

                self.vklopi(3, 1, 3)
                self.vklopi(3, 1, 4)

            else:  # simulacija 5,0 V DIGITAL_IO, portset = high

                self.vklopi(3, 1, 3)
                self.vklopi(3, 1, 5)

            # izprazni Uniblox serial buffer
            globalDataInst.uniblox.clear()

            time.sleep(0.2)

            cmd1 = "\x02GPIO,READ,A,"
            cmd2 = str(portnum)
            cmd3 = "\x03"

            command = cmd1 + cmd2 + cmd3

            globalDataInst.uniblox.write(command)

            time.sleep(0.1)

            response = globalDataInst.uniblox.read()  # 1. vrstica je prazna
            response = globalDataInst.uniblox.read()  # 2. vrstica je stanje

            if "low" in response:
                return 0
            elif "high" in response:
                return 1
            else:
                return -1

        except VisaIOError:
            #logger.info("06x : ERROR")
            globalDataInst.fail(1)
            print("Napaka pri komunikaciji z DUT (Uniblox) 06x : ERROR")

        finally:
            # izklop DIGITAL_IO
            self.izklopi(3, 1, 3)
            self.izklopi(3, 1, 4)
            self.izklopi(3, 1, 5)

    def digital_io_read(self, portnum):

        try:

            # Preberi stanje "Digital IO" vhodov

            # izprazni Uniblox serial buffer
            globalDataInst.uniblox.clear()

            time.sleep(0.2)

            cmd1 = "\x02GPIO,READ,A,"
            cmd2 = str(portnum)
            cmd3 = "\x03"

            command = cmd1 + cmd2 + cmd3

            globalDataInst.uniblox.write(command)

            time.sleep(0.1)

            response = globalDataInst.uniblox.read()  # 1. vrstica je prazna
            response = globalDataInst.uniblox.read()  # 2. vrstica je stanje

            if "high" in response:
                return 1
            elif "low" in response:
                return 0
            else:
                return -1

        except VisaIOError:
            print("Napaka pri komunikaciji z DUT (Uniblox)")
            return -1

    def adc_read(self, port, channel):

        try:

            # preberi Alert ADC

            # predpogoj za delovanje je vklopljen DUT

            globalDataInst.uniblox.clear()
            time.sleep(0.1)

            cmd1 = "\x02ADC,READ,"
            cmd2 = str(port)
            cmd3 = ","
            cmd4 = str(channel)
            cmd5 = "\x03"

            command = cmd1 + cmd2 + cmd3 + cmd4 + cmd5

            globalDataInst.uniblox.write(command)

            try:
                response = globalDataInst.uniblox.read()  # 1. vrstica je prazna
                response = globalDataInst.uniblox.read()  # 2. vrstica je stanje
                # print(response)  # ADC value

                str1, adc, str3 = response.split(' ')  # razdeli rezultat na 3 besede (delimiter = presledek)

                result = ((globalDataInst.VOLTAGE_REF / (100 / (910 + 100))) / globalDataInst.ADC_SCALE)  # 100k in 910k sta upora ALERT vezja
                result = float(result) * float(adc)

                return result

            except VisaIOError:
                print("Uniblox Response Error")
                globalDataInst.fail(1)
                return -1

        except VisaIOError:
            print("Napaka pri komunikaciji z DUT (Uniblox)")

    def gpio_read(self, port, channel):

        try:

            globalDataInst.uniblox.clear()
            time.sleep(0.1)

            cmd1 = "\x02GPIO,READ,"
            cmd2 = str(port)
            cmd3 = ","
            cmd4 = str(channel)
            cmd5 = "\x03"

            command = cmd1 + cmd2 + cmd3 + cmd4 + cmd5

            globalDataInst.uniblox.write(command)

            try:
                response = globalDataInst.uniblox.read()  # 1. vrstica je prazna
                response = globalDataInst.uniblox.read()  # 2. vrstica je stanje

                if "high" in response:
                    return 1
                elif "low" in response:
                    return 0

            except VisaIOError:
                print("Uniblox Response Error")
                return -1

        except VisaIOError:
            print("Napaka pri komunikaciji z DUT (Uniblox)")

    def gpio_write(self, port, channel, level):

        try:

            cmd1 = "\x02GPIO,WRITE,"
            cmd2 = str(port)
            cmd3 = ","
            cmd4 = str(channel)
            cmd5 = ","
            cmd6 = str(level)
            cmd7 = "\x03"

            command = cmd1 + cmd2 + cmd3 + cmd4 + cmd5 + cmd6 + cmd7

            globalDataInst.uniblox.write(command)

        except VisaIOError:
            print("Napaka pri komunikaciji z DUT (Uniblox)")

    def get_alert_irq(self):

        try:

            # preberi "alert irq" stanje

            # predpogoj za delovanje je vklopljen DUT

            globalDataInst.uniblox.clear()
            time.sleep(0.1)

            # GET IRQ
            globalDataInst.uniblox.write("\x02GPIO,READ,D,2\x03")  # read ALERT_IRQ

            response = globalDataInst.uniblox.read()
            response = globalDataInst.uniblox.read()

            if "high" in str(response):
                print("Alert IRQ Read : HIGH")
                # logger.info("Alert IRQ Read : HIGH")
            else:
                print("Alert IRQ Read : LOW")
                # logger.info("Alert IRQ Read : LOW")

        except VisaIOError:
            print("Napaka pri komunikaciji z DUT (Uniblox)")

    def get_pwr_fail(self):

        try:

            globalDataInst.uniblox.clear()
            time.sleep(0.1)

            # GET PWR_VIN_FAIL
            globalDataInst.uniblox.write("\x02GPIO,READ,E,15\x03")  # read PWR_VIN_FAIL
            time.sleep(0.1)

            response = globalDataInst.uniblox.read()
            response = globalDataInst.uniblox.read()

            if "low" in str(response):
                return 0  # pwr ok
            else:
                return 1  # pwr fail

        except VisaIOError:
            print("Napaka pri komunikaciji z DUT (Uniblox)")

    def uart_test(self, uart_num):

        # uart test send-read

        try:

            # poslji prvi paket
            pack1 = "\x02"
            pack2 = "UART,OPEN,"
            pack3 = str(uart_num)
            pack4 = "\x03"

            send1 = pack1 + pack2 + pack3 + pack4

            globalDataInst.uniblox.clear()  # pocisti serial buffer
            time.sleep(0.1)

            globalDataInst.uniblox.write(send1)
            time.sleep(0.1)

            # poslji drugi paket
            pack1 = "\x02"
            pack2 = "UART,WRITE,"
            pack3 = str(uart_num)
            pack4 = ",test\n\r\x03"

            send2 = pack1 + pack2 + pack3 + pack4

            globalDataInst.uniblox.write(send2)
            time.sleep(0.1)

            response = globalDataInst.uniblox.read()

            if "test" in response:
                return 1  # pass
            else:
                return 0  # fail

        except VisaIOError:
            print("Napaka pri izvajanju UART testa")
            # logger.info("10x : ERROR")
            globalDataInst.fail(1)

        finally:
            # zapri uart port
            globalDataInst.uniblox.write("\x02UART,CLOSE\x03")
            time.sleep(0.1)

    def rs485_send(self):

        # rs485 send test
        try:

            rs485 = globalDataInst.rm.open_resource(globalDataInst.addr_inst6)
            rs485.baud_rate = 115200
            rs485.timeout = 1000

            time.sleep(0.2)

            rs485.write("TEST")
            time.sleep(0.2)

            rs485.close()
            time.sleep(0.1)

        except VisaIOError:
            print("\nNapaka! Preveri povezavo z USB FTDI RS485\n")

    def get_bat_consumption(self):

        # meritev porabe toka baterije

        try:
            volt_pre = self.napetost(304)
            volt_pos = self.napetost(305)

            volt_pre = float(volt_pre)
            volt_pos = float(volt_pos)

            # izracun toka I=(U1-U2)/R

            volt_dif = volt_pre - volt_pos
            shunt_res = 0.1

            bat_consumption = volt_dif / shunt_res

            # print("Tok baterije:", bat_consumption, "A")

            return bat_consumption

        except VisaIOError:
            print("\nNapaka pri merjenju toka baterije!")
            return 0

    def get_bat_voltage(self):

        # meritev napetosti baterije

        try:
            bat_voltage = self.napetost(305)
            bat_voltage = float(bat_voltage)

            # print("\nNapetost baterije:", bat_voltage, "V")

            return bat_voltage

        except VisaIOError:
            print("\nNapaka pri merjenju napetosti baterije!")
            return 0

    def enable_bat_thermo(self):

        try:
            globalDataInst.thermostat.setDefaultTempTrigger(globalDataInst.uniblox, 1)
            globalDataInst.thermostat.setDefaultTempTrigger(globalDataInst.uniblox, 2)
            globalDataInst.bat.bat_def_chrg_on(globalDataInst.uniblox)  # omogoči polnjenje baterij
            globalDataInst.bat.bat_opt_chrg_on(globalDataInst.uniblox)

        except VisaIOError:
            print("Napaka pri komunikaciji z Uniblox modulom!")

    def disable_bat_thermo(self):

        try:
            globalDataInst.thermostat.changeThermostatPolarity(globalDataInst.uniblox, 1, 0)  # onemogoci uporabo baterije
            globalDataInst.thermostat.changeThermostatPolarity(globalDataInst.uniblox, 2, 0)  # onemogoci uporabo baterije
            globalDataInst.bat.bat_def_chrg_off(globalDataInst.uniblox)  # onemogoci polnjenje baterij
            globalDataInst.bat.bat_opt_chrg_off(globalDataInst.uniblox)

        except VisaIOError:
            print("Napaka pri komunikaciji z Uniblox modulom!")

    def ext_int_read(self):

        # external interrupt read

        globalDataInst.uniblox.clear()
        time.sleep(0.5)

        globalDataInst.uniblox.write("\x02EXTINT,ENABLE\x03")  # enable EXT_INT
        time.sleep(0.2)
        globalDataInst.uniblox.write("\x02GPIO,WRITE,D,3,1\x03")  # set ALERT_EN high
        time.sleep(0.2)
        globalDataInst.uniblox.write("\x02GPIO,WRITE,D,5,1\x03")  # set ALERT_PULSE high
        time.sleep(0.2)

        globalDataInst.uniblox.clear()
        time.sleep(0.5)

        globalDataInst.uniblox.write("\x02GPIO,WRITE,D,5,0\x03")  # set ALERT_PULSE low
        time.sleep(3.0)

        try:
            response = globalDataInst.uniblox.read()  # 1. vrstica je prazna
            response = globalDataInst.uniblox.read()  # 2. vrstica je stanje
            response = globalDataInst.uniblox.read()  # 3. vrstica je stanje

            if "ExtInt" in response:
                return 1  # detekcija ext interrupta
            else:
                return 0

        except VisaIOError:
            print("Napaka pri izvajanju Ext Interrupt testa!")
            return -1

    def simulate_alert(self, button):

        # simulator alert tipke (push, release, short, open)

        try:
            if str(button) == "push":
                self.izklopi(1, 1, 6)
                time.sleep(0.1)
                self.izklopi(1, 1, 7)
                time.sleep(0.1)
                self.izklopi(1, 1, 8)
                time.sleep(0.1)

                self.vklopi(1, 1, 6)  # tipka je pritisnjena
                time.sleep(0.1)
                print("\nALERT: Tipka je pritisnjena")
                return 1

            elif str(button) == "release":
                self.izklopi(1, 1, 6)
                time.sleep(0.1)
                self.izklopi(1, 1, 7)
                time.sleep(0.1)
                self.izklopi(1, 1, 8)
                time.sleep(0.1)

                self.vklopi(1, 1, 8)  # tipka je sproscena
                time.sleep(0.1)
                print("\nALERT: Tipka je sproscena")
                return 2

            elif str(button) == "short":
                self.izklopi(1, 1, 6)
                time.sleep(0.1)
                self.izklopi(1, 1, 7)
                time.sleep(0.1)
                self.izklopi(1, 1, 8)
                time.sleep(0.1)

                self.vklopi(1, 1, 7)  # kratek stik
                time.sleep(0.1)
                print("\nALERT: Kratek stik")
                return 3

            elif str(button) == "open":
                self.izklopi(1, 1, 6)
                time.sleep(0.1)
                self.izklopi(1, 1, 7)
                time.sleep(0.1)
                self.izklopi(1, 1, 8)
                time.sleep(0.1)
                print("\nALERT: Odprte sponke")
                return 4

            else:
                print("\nERROR! Izbrana simulacija alert tipke ni veljavna")
                return 0

        except VisaIOError:
            print("\nNapaka pri simulaciji alert tipke (Rigol M300)\n")
            return -1

    def rtc_wdi(self):

        # RTC WDI funkcionalnost
        try:
            value = globalDataInst.extRTC.testWDT(globalDataInst.uniblox)
            time.sleep(0.5)

            if value == 0:  # če je return 0, je detektiran reset Uniblox-a = PASS
                return 0
            elif value == 1:  # če je return 1, extRTC ni kicknil Unibloxa na WDI liniji = FAIL
                return 1
            elif value == 2:  # če je return 2, ni uspel prebrati texta, ki ga Uniblox pošlje ob resetu = FAIL
                return 2
            else:
                return 3  # FAIL

        except VisaIOError:
            return -1

    def set_exit_handler(self, func):
        if os.name == "nt":
            try:
                import win32api
                win32api.SetConsoleCtrlHandler(func, True)
            except ImportError:
                version = ".".join(map(str, sys.version_info[:2]))
                raise Exception("pywin32 not installed for Python " + version)
        else:
            import signal
            signal.signal(signal.SIGTERM, func)
            signal.signal(signal.SIGINT, func)