from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QObject, pyqtSlot
from visaUi import Ui_MainWindow
import sys
import copy
import os
import glob
import time
import datetime
from niti import *

from database import DatabaseConnection
#from TestJig import TestJig
#from globalSetUpTearDown import globalSetupTearDownInst

from globalData import globalDataInst


class MainWindowUIClass(Ui_MainWindow, QtWidgets. QMainWindow):
    def __init__(self):
        '''Initialize the super class'''

        self.globalDict = {}  # tukaj belezimo izbrane posamicne teste
        self.fileName = ""  # pot do mape kjer se nahajajo testi
        self.testResults = []  # tukaj so shranjeni rezultati unit testov
        self.started_at = 0
        self.globalTest = False  # dolocimo ali je test globalen ali posamicen
        self.imenaTestov = [] # shranjena imena prebranih testov
        self.izberiVse = True

        super().__init__()

    def setupUi(self, MW):
        ''' Setup the UI of the super class, and add here code
        that relates to the way we want our UI to operate.
        '''
        QtWidgets.QMainWindow.__init__(self)
        super().setupUi(MW)
        self.selectedTestLabel.setText("<span style=\"color:black; \">Mapa ni izbrana !</span>")
        self.selectedTestLabel.setStyleSheet("background-color:yellow;")
        self.setLabelAnimation(self.globalProgressLabel)
        self.setLabelAnimation(self.singleProgressLabel)

    def setLabelAnimation(self, labelName):
        movie = QMovie("loader1.gif", QByteArray(), self)
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(100)
        labelName.setMovie(movie)
        movie.start()

    def setOkFailLabel(self, tip):

        if tip == 1: # ok
            self.failOkLabel.setText("<span style=\"color:white; \">OK</span>")
            self.frame_2.setStyleSheet("background-color:green;")
            self.badTestsListView.setStyleSheet("background-color:white;")
        else: # fail
            self.failOkLabel.setText("<span style=\"color:white; \">FAIL</span>")
            self.frame_2.setStyleSheet("background-color:red;")
            self.badTestsListView.setStyleSheet("background-color:white;")

    def setItemsCheckable(self, list):

        tmpDict = copy.deepcopy(self.globalDict)

        item = QtWidgets.QListWidgetItem()
        for i in range(list.count()):
            item = list.item(i)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if tmpDict[item.text()] == 0:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)


    def displayMessageBox(self, title, text, type):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(type)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # slot
    def chooseFolderButtonClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName = QFileDialog.getExistingDirectory()
        # fileName = QFileDialog.getOpenFileName()
        if self.fileName:
            self.selectedTestLabel.setText("Izbrana mapa: "+self.fileName)
            self.selectedTestLabel.setStyleSheet("background-color:green;")
    # slot
    def badTestsListViewItemClicked(self, item):
        print("izbran")
        ime_testa = str(item.text()).split(" ")[0]
        #print(ime_testa)
        msg = QMessageBox()
        msg.setWindowTitle("Opis")
        msg.setIcon(QMessageBox.Information)
        for i in range(0, len(self.testResults)):
            #print(self.testResults[i]["path"])
            if self.testResults[i]["path"] == ime_testa:
                msg.setText("Opis napake: \n" + self.testResults[i]["error"])

        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    # thread func
    def getListOfDescoveredTests(self, data):  # dobimo podatke o testih v izbrani mapi
        print(data)
        self.imenaTestov = data
        # print(imenaTestov)
        self.posamicniTestiListWidget.clear()
        self.globalDict.clear()

        for i in range(0, len(self.imenaTestov)):
            self.posamicniTestiListWidget.addItem(self.imenaTestov[i])
            self.globalDict[self.imenaTestov[i]] = 0
            imeClassa = self.imenaTestov[i].split(".")[1]
            if imeClassa not in globalDataInst.dictOfExecutedTests.keys():
                globalDataInst.dictOfExecutedTests[str(imeClassa)] = False

        self.setItemsCheckable(self.posamicniTestiListWidget)
        self.singleProgressLabel.setHidden(True)


    # slot
    def loadTestsButton(self):

        if self.fileName:
            if glob.glob(self.fileName + '/test_*') != []:

                self.imenaTestov.clear()
                self.singleProgressLabel.setHidden(False)

                self.threadsDiscover = []
                runDiscover = DiscovererThread(self.fileName)
                runDiscover.discoverer_data.connect(self.getListOfDescoveredTests)
                self.threadsDiscover.append(runDiscover)
                runDiscover.start()

            else:
                print("V tej mapi ni testnih datotek !!!")
                self.displayMessageBox("Napaka", "V tej mapi ni testnih datotek. \nProsim izberite drugo.", QMessageBox.Warning)
                self.selectedTestLabel.setStyleSheet("background-color:red;")
        else:
            print("Datoteka ni izbrana !!!")
            self.displayMessageBox("Napaka", "Potrebno je izbrati mapo", QMessageBox.Warning)


    def getSelectedItemsFromListView(self):
        # preverimo kateri so obkljukani
        item = QtWidgets.QListWidgetItem()
        for i in range(self.posamicniTestiListWidget.count()):
            item = self.posamicniTestiListWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                # print("checked")
                self.globalDict[item.text()] = 1
            else:
                #  print("un-checked")
                self.globalDict[item.text()] = 0

    def dolociOdvisnostTestnihSklopov(self, izbranSklop, pogojniTest, arrayOfTests):

        for izbran in arrayOfTests:

            izbraniTest = izbran.split(".")[1]

            if izbraniTest == izbranSklop and globalDataInst.dictOfExecutedTests[pogojniTest] == False:

                # najprej izvedemo odstranimo željeni test in nato izvedemo pogojni test

                for value in list(arrayOfTests):
                    if izbraniTest in value:
                        arrayOfTests.remove(value)

                self.displayMessageBox("Info", "Izvajam mankajoče pogojne teste: " + pogojniTest + " \n Po izvajanju lahko ponovno poizkusiti zagnati željene teste",
                                       QMessageBox.Information)
                for value in self.imenaTestov:
                    if pogojniTest in value:
                        arrayOfTests.append(value)

        return arrayOfTests


    # slot
    def singleTestButtonClicked(self):
        print("single")

        if self.fileName:
            if glob.glob(self.fileName + '/test_*') != []:
                self.getSelectedItemsFromListView()
                if all(value == 0 for value in self.globalDict.values()):
                    print("Niste naložili ali izbrali testov za izvajanje")
                    self.displayMessageBox("Napaka", "Niste naložili ali izbrali testov za izvajanje", QMessageBox.Warning)
                    return

                # if self.prviZagon:
                #      self.prviZagon = False
                #      globalSetupTearDownInst.globalSetUp()

                arrayOfTests = []
                if self.badTestsListView.count() > 0:
                    self.badTestsListView.clear()
                for key, value in self.globalDict.items():
                    if self.globalDict[key] == 1:
                        arrayOfTests.append(key)
                # print(arrayOfTests)
                self.testResults.clear()

                self.singleProgressLabel.setHidden(False)
                self.globalTest = False


                # dolocimo odvisnosti od testnih sklopov (test set)
                # pogojniTest = "TestVisaMethods"
                # izbranSklop = "TestseEn"
                # arrayOfTests = self.dolociOdvisnostTestnihSklopov(izbranSklop, pogojniTest, arrayOfTests)

                self.pricetek_at = time.time()

                self.threadsSingle = []
                if arrayOfTests != []:
                    runThread = RunnerThread(self.fileName, arrayOfTests)  # izvede globalni test, če ne podamo argumentov oz lista testov npr. ["test_visaTests.TestVisaMethods.test_isupper","test_visaTests.TestVisaMethods.test_split"]
                    runThread.runner_data.connect(self.getListOfResulst)
                    self.threadsSingle.append(runThread)
                    runThread.start()

            else:
                print("V tej mapi ni testnih datotek !!!")
                self.displayMessageBox("Napaka", "V tej mapi ni testnih datotek. \nProsim izberite drugo.", QMessageBox.Warning)
                self.selectedTestLabel.setStyleSheet("background-color:red;")
        else:
            print("Datoteka ni izbrana !!!")
            self.displayMessageBox("Napaka", "Potrebno je izbrati mapo", QMessageBox.Warning)

    def createPorocilo(self, pretekelCas, tip):

        # Write to file
        tipPorocila = tip.replace("č", "c")
        imeDatoteke = str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")) + "_" + tipPorocila + "_porocilo.html"
        if not os.path.exists("porocila"):
            os.makedirs("porocila")

        f = open("porocila/"+imeDatoteke, "a")
        f.write("<html><head><style>table, th, td {border: 1px solid black;border-collapse: collapse;}</style><meta charset='UTF-8'><title>Poročilo</title></head>")
        f.write("<body>")
        f.write("<p>Datum: " + str(datetime.datetime.now().strftime("%d.%m.%Y | %H:%M:%S")) + "</p>")
        f.write("<h1>" + tip + " poročilo izvajanja (številka plošče), Čas (" + pretekelCas + "s):</h1>")
        f.write("<table style='width:100%'>")
        f.write("<tr>")
        f.write("<th>Ime testa</th>")
        f.write("<th>Čas izvajanja</th>")
        f.write("<th>Status</th>")
        f.write("<th>Opis napake</th>")
        f.write("</tr>")

        for i in range(0, len(self.testResults)):
            f.write("<tr>")
            if self.testResults[i]["status"] is 'F' : #fail
                f.write("<td>" + self.testResults[i]["path"] + "</td>")
                elapsed = self.testResults[i]["end_time"] - self.testResults[i]["start_time"]
                cas = '({}s)'.format(round(elapsed, 2))
                f.write("<td>" + cas + "</td>")
                f.write("<td bgcolor='#f01616'>FAIL</td>")
                f.write("<td>" + self.testResults[i]["error"] + "</td>")
            elif self.testResults[i]["status"] is 'E' : #error
                f.write("<td>" + self.testResults[i]["path"] + "</td>")
                elapsed = self.testResults[i]["end_time"] - self.testResults[i]["start_time"]
                cas = '({}s)'.format(round(elapsed, 2))
                f.write("<td>" + cas + "</td>")
                f.write("<td bgcolor='#f01616'>Execution ERROR</td>")
                f.write("<td>" + self.testResults[i]["error"] + "</td>")
            elif self.testResults[i]["status"] is 'OK': # pass
                f.write("<td>" + self.testResults[i]["path"] + "</td>")
                elapsed = self.testResults[i]["end_time"] - self.testResults[i]["start_time"]
                cas = '({}s)'.format(round(elapsed, 2))
                f.write("<td>" + cas + "</td>")
                f.write("<td bgcolor='#39ae8e'>" + self.testResults[i]["status"] + "</td>")
                f.write("<td>/</td>")
            elif self.testResults[i]["status"] is 's': # skip
                f.write("<td>" + self.testResults[i]["path"] + "</td>")
                elapsed = self.testResults[i]["end_time"] - self.testResults[i]["start_time"]
                cas = '({}s)'.format(round(elapsed, 2))
                f.write("<td>" + cas + "</td>")
                f.write("<td bgcolor='#CCCC00'>SKIP</td>")
                f.write("<td>" + self.testResults[i]["error"] + "</td>")
            else: # drugo
                f.write("<td>" + self.testResults[i]["path"] + "</td>")
                elapsed = self.testResults[i]["end_time"] - self.testResults[i]["start_time"]
                cas = '({}s)'.format(round(elapsed, 2))
                f.write("<td>" + cas + "</td>")
                f.write("<td bgcolor='##FFDAB9'>" + self.testResults[i]["status"] + "</td>")
                f.write("<td>" + self.testResults[i]["error"] + "</td>")
            f.write("</tr>")
        f.write("</table>")
        f.write("</body>")
        f.write("</html>")
        f.close()


    def insertToDatabase(self, tip_testa):

        datum = str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        st_plosce = "ni se"
        koda = time.time()
        database = DatabaseConnection()
        database.insertGlobalRun(st_plosce, datum, tip_testa, str(koda))

        for i in range(0, len(self.testResults)):
            ime_testa = self.testResults[i]["path"]
            elapsed = self.testResults[i]["end_time"] - self.testResults[i]["start_time"]
            cas_izvajanja = '({}s)'.format(round(elapsed, 2))
            status = self.testResults[i]["status"]
            if status != "OK":
                opis_napake = self.testResults[i]["error"]
            else:
                opis_napake = "/"
            database.insertIntoDatabase(ime_testa, cas_izvajanja, status, opis_napake, str(koda))

    # thread func
    def getListOfResulst(self, data):
        print(data)
        self.globalDict.clear()
        self.testResults = data
        failedTests = False
        for i in range(0, len(self.testResults)):
            if self.testResults[i]["status"] is 'F' or self.testResults[i]["status"] is 'E':
                elapsed = self.testResults[i]["end_time"] - self.testResults[i]["start_time"]
                cas = '({}s)'.format(round(elapsed, 2))
                self.badTestsListView.addItem(self.testResults[i]["path"] + " ... " + self.testResults[i]["status"] + " " + cas)
                # self.globalDict[self.testResults[i]["path"]] = 0
                failedTests = True


        if self.globalTest == True:  # global Tests Ui
            pretekel = time.time() - self.started_at
            skupniCas = '{}'.format(round(pretekel, 2))
            if float(skupniCas) >= 60.0:
                minute = float(skupniCas) / 60.0
                sekunde = float(skupniCas) % 60.0
                skupniCas = str(round(minute)) + "min " + str(round(sekunde))
            self.izpisLabel.setText("Izpis (" + str(skupniCas) + "s):")
            self.globalProgressLabel.setHidden(True)
            # Write to file
            self.createPorocilo(skupniCas, "Globalno")
            # Write to database
            #self.insertToDatabase("Globalni test")
        else:  # Single tests Ui
            self.singleProgressLabel.setHidden(False)
            pretekel = time.time() - self.pricetek_at
            skupniCas = '{}'.format(round(pretekel, 2))
            if float(skupniCas) >= 60.0:
                minute = float(skupniCas) / 60.0
                sekunde = float(skupniCas) % 60.0
                skupniCas = str(round(minute)) + "min " + str(round(sekunde))
            self.izpisLabel.setText("Izpis (" + str(skupniCas) + "s):")
            self.singleProgressLabel.setHidden(True)
            # Write to file
            self.createPorocilo(skupniCas, "Posamično")
            # Write to database
            #self.insertToDatabase("Posamični test")

        if failedTests:
            self.setOkFailLabel(0)
        else:
            self.setOkFailLabel(1)

    # slot
    def globalTestButtonClicked(self):

        print("global")
        if self.fileName:
            self.testResults.clear()
            if glob.glob(self.fileName + '/test_*') != []:
                if self.badTestsListView.count() > 0:
                    self.badTestsListView.clear()

                # if self.prviZagon:
                #     self.prviZagon = False
                #     globalSetupTearDownInst.globalSetUp()

                self.globalTest = True
                self.globalProgressLabel.setHidden(False)

                self.started_at = time.time()

                self.threadsGlobal = []
                runThread = RunnerThread(self.fileName)
                runThread.runner_data.connect(self.getListOfResulst)
                self.threadsGlobal.append(runThread)
                runThread.start()

            else:
                print("V tej mapi ni testnih datotek !!!")
                self.displayMessageBox("Napaka", "V tej mapi ni testnih datotek. \nProsim izberite drugo.", QMessageBox.Warning)
                self.selectedTestLabel.setStyleSheet("background-color:red;")
        else:
            print("Datoteka ni izbrana !!!")
            self.displayMessageBox("Napaka", "Potrebno je izbrati mapo", QMessageBox.Warning)


    #  slot
    def searchTextChanged(self):
        #print("spreminjamo tekst")
        iskanoBesedilo = self.searchBox.text()
        matching = [s for s in self.globalDict if iskanoBesedilo.upper() in s.upper()]
        #print(matching)
        self.posamicniTestiListWidget.clear()
        for item in matching:
            self.posamicniTestiListWidget.addItem(item)
        self.setItemsCheckable(self.posamicniTestiListWidget)

    #  slot
    def checkBoxSelected(self):
        # preverimo kateri so obkljukani
        item = QtWidgets.QListWidgetItem()
        for i in range(self.posamicniTestiListWidget.count()):
            item = self.posamicniTestiListWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
               # print("checked")
                self.globalDict[item.text()] = 1
            else:
              #  print("un-checked")
                self.globalDict[item.text()] = 0
       # print(self.globalDict)

    def selectAllCheckBoxes(self):

        item = QtWidgets.QListWidgetItem()
        for i in range(self.posamicniTestiListWidget.count()):
            item = self.posamicniTestiListWidget.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def deSelectAllCheckBoxes(self):

        item = QtWidgets.QListWidgetItem()
        for i in range(self.posamicniTestiListWidget.count()):
            item = self.posamicniTestiListWidget.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

    #slot
    def selectAllCheckboxesButtonClicked(self):
        if self.izberiVse == True:
            self.selectAllCheckBoxes()
            self.izberiVse = False
            self.selectAllCheckBoxesButton.setText("Ne izberi vse")
        else:
            self.deSelectAllCheckBoxes()
            self.izberiVse = True
            self.selectAllCheckBoxesButton.setText("Izberi vse")

'''def appExec():
  app = QApplication(sys.argv)
  app.exec_()
  print("Zapiram app")
  if globalSetupTearDownInst.setup == True:
      globalSetupTearDownInst.globalTearDown()'''


def main():

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindowUIClass()
    ui.setupUi(MainWindow)
    MainWindow.show()
    #sys.exit(appExec())
    sys.exit(app.exec())

main()