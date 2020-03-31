import os
from globalData import globalDataInst
from TestJig import TestJig


class GlobalSetUpTearDown ():

    def __init__(self):
        self.setup = False

    def globalSetUp(self):

        self.setup = True

        if os.name == "nt":
            import win32api
            win32api.SetConsoleCtrlHandler(TestJig.on_exit, True)  # omogoci izhod tekom testiranja, izklopi vse naprave
        else:
            TestJig.set_exit_handler(TestJig.on_exit)  # omogoci izhod tekom testiranja, izklopi vse naprave

        TestJig.breme(0)  # preventivni izklop bremena
        TestJig.power_set(0.0)  # preventivni izklop pred zacetkom testiranja
        TestJig.izklopi(1, 2, 4)  # preventivni izklop main napajanja
        TestJig.izklopi(1, 2, 5)  # preventivni izklop main reverse polarity napajanja
        TestJig.izklopi(1, 3, 4)  # preventivni izklop service port napajanja
        TestJig.izklopi(1, 3, 5)  # preventivni izklop service port reverse polarity napajanja
        TestJig.connect_battery(0)  # preventivni izklop baterijskega simulatorja

    def globalTearDown(self):

        # ##############################################################################################
        # IZKLOP DUT
        # ##############################################################################################

        TestJig.connect_battery(0)  # izklop baterije
        TestJig.uniblox_ps(0)  # izklop internih napajalnikov
        TestJig.izklopi(1, 2, 4)  # izklop napajanje DUT (2 vrstica, 4 kolona)
        TestJig.power_set(0.0)  # izklop zunanjega napajalnika
        globalDataInst.uniblox.close()  # prekini komunikacijo z uniblox modulom

        # ##############################################################################################
        # PRAZNJENJE KONDENZATORJEV PREKO BREMENA
        # ##############################################################################################

        print("\nSupercap voltage:")
        supercap_voltage = TestJig.napetost(202)


        print("\nVklop bremena: ", TestJig.breme(1.5), "A")
        print("\nPraznjenje kondenzatorjev...\n")

        while supercap_voltage > 1.0:  # dokler je napetost po izklopu vecja, nadaljuj s praznjenjem supercap-ov
            supercap_voltage = TestJig.napetost(202)

        print("\nIzklop bremena: ", TestJig.breme(0), "A")

globalSetupTearDownInst = GlobalSetUpTearDown()