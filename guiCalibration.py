# Bug: If you start multiple timers in multiple instances of doOperation, only the last one will actually be connected
# to the timeout

# This code communicates with and NI USB 6002 DAQ (or equivalent) to send out TTL pulses and read in a voltage. This is
# controlled by a GUI created with Qt Designer that will allow buttons to set TTL values to high or low, send a TTL
# pulse of a specific length, and continuously monitor the voltage reading.

import sys
from PyQt4 import QtCore, QtGui, uic
import PyDAQmx as pydaqmx  # Python library to execute NI-DAQmx code
import numpy as np
from PyDAQshortcuts import TTLSwitch, makeAnalogIn, getAnalogIn  # Module that sets a bunch of defaults for the DAQ operations we will be doing
from pyqtShortcuts import MatplotlibWidget  # Module that has custom widgets for Qt
import dataShortcuts  # Module that has functions like saving data to a .csv format easily
import time
import os

qtCreatorFile = "tuningRigCalibrationGUI.ui"  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

###### USER INPUT ######
dev = "Dev2/"  # The location of the device, which can be found in the program NI MAX -> Devices and Interfaces. MAKE SURE TO END STRING IN A "/"
digitalPort = "port1/"  # Which digital port the TTL pulses will come from (P0.x is port0) MAKE SURE TO END STRING IN A "/"
gasLine = 3  # Which line within the above port is leading to the gas valve's circuit
pumpLine = 2
cryoLine = 0
analogPort = "ai3"  # Which analog input grouping the pressure sensor is hooked up to
dataUpdateTime = 100  # Time between consecutive calls of the readData function in ms. (In reality you will never get better than 50ms between data points)
dataLabel = "Pressure(V)"
### END USER INPUT #####




######## Configure analog input from the pressure sensor ##########
fSamp = 50000  # Sampling frequency (maximum is 50000)
nSamp = 10  # Therefore, our reading will be the average of 10 samples over 200us
readPressAvg = pydaqmx.TaskHandle()
data = np.zeros((int(nSamp),), dtype=np.int16)
makeAnalogIn(dev, analogPort, readPressAvg, fSamp, nSamp)

###### Configure digital switches for valves ######
gasSwitch = TTLSwitch(dev, digitalPort, gasLine)
cryoSwitch = TTLSwitch(dev, digitalPort, cryoLine)
pumpSwitch = TTLSwitch(dev, digitalPort, pumpLine)


###### Configure the options in the Set Valve Operations menu #####
# Dictionary that connects the Set Valve Operation options from GUI to a switch in this code.
# The string should match the option on the GUI exactly, the definition should be the switch it opens
choiceDict = {'Gas Valve': gasSwitch,
              'Cryo Valve': cryoSwitch,
              'Pump Valve': pumpSwitch}


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.openGasButton.clicked.connect(lambda: gasSwitch.high())
        self.closeGasButton.clicked.connect(lambda: gasSwitch.low())
        self.openCryoButton.clicked.connect(lambda: cryoSwitch.high())
        self.closeCryoButton.clicked.connect(lambda: cryoSwitch.low())
        self.openPumpButton.clicked.connect(lambda: pumpSwitch.high())
        self.closePumpButton.clicked.connect(lambda: pumpSwitch.low())
        self.resetButton.clicked.connect(self.clearPlot)
        self.saveButton.clicked.connect(self.saveData)

        self.opGo.clicked.connect(self.doOperation)

        # Set up the graph
        self.matplotlibWidget = MatplotlibWidget(self)
        self.matplotlibWidget.setGeometry(self.graphHolder.geometry())  # If this starts breaking you could also try using .frameGeometry()
        self.matplotlibWidget.axis.set_xlabel('Time (sec)')
        self.matplotlibWidget.axis.set_ylabel(dataLabel)
        # Set the graph to update after the specified interval
        self.graphTimer = QtCore.QTimer()  # Use QTimer because time.sleep() pauses ALL functionality while sleeping
        self.graphTimer.timeout.connect(self.readData)  # Every time myTimer times out, execute showPressure()
        self.graphTimer.start(dataUpdateTime)  # Update every second
        # Initialize some variables
        self.dataArr = list()
        self.timeArr = list()
        self.initialTime = time.time()

        # Continuously update pressure
        self.showPressure()
        self.myTimer = QtCore.QTimer()  # Use QTimer because time.sleep() pauses ALL functionality while sleeping
        self.myTimer.timeout.connect(self.showPressure)  # Every time myTimer times out, execute showPressure()
        self.myTimer.start(1000)  # Update every second


    def doOperation(self):
        if self.autoReset.isChecked():
            self.clearPlot()
        valve = str(self.opValveChoice.currentText())
        openTime = (self.opOpenTime.value())
        choiceDict[valve].high()
        self.opTimer = QtCore.QTimer()  # Use QTimer because time.sleep() pauses ALL functionality while sleeping
        self.opTimer.setSingleShot(True)
        self.opTimer.timeout.connect(lambda: choiceDict[valve].low())
        self.opTimer.start(openTime)

    def showPressure(self):
        getAnalogIn(readPressAvg, data)
        dataCal = (data * (20.0 / 2 ** 16) - 0.029) * 1 / 0.946  # The empirical calibration from DAQ units to Volts
        val = np.mean(dataCal)  # average over the 10 consecutive values
        val_std = np.std(dataCal)  # standard deviation of the mean
        self.pressureWindow.setText("%.4f +/- %.4f" % (val, val_std))  # Write the pressure to the GUI

    def clearPlot(self):
        self.dataArr = list()
        self.timeArr = list()
        self.initialTime = time.time()
        self.matplotlibWidget.axis.cla()
        self.matplotlibWidget.axis.set_xlabel('Time (sec)')
        self.matplotlibWidget.axis.set_ylabel(dataLabel)

    def readData(self):
        # For now, we will repeat the structure of showPressure() because in the future we will want different data here, it is easiest to keep this as a completely separate function
        getAnalogIn(readPressAvg, data)
        dataCal = (data * (20.0 / 2 ** 16) - 0.029) * 1 / 0.946  # The empirical calibration from DAQ units to Volts
        val = np.mean(dataCal)  # average over the 10 consecutive values

        newData = val
        self.dataArr.append(newData)
        self.timeArr.append(time.time() - self.initialTime)  # Time in seconds
        self.matplotlibWidget.axis.plot(self.timeArr, self.dataArr, 'k')
        self.matplotlibWidget.canvas.draw()

    def saveData(self):
        # Get current save directory and metadata
        self.saveDir = str(self.saveDirText.text())
        self.metadata = str(self.metadataText.toPlainText())

        # Check if save directory exists. If it does, append a number at the end to make sure we don't overwrite anything
        if os.path.exists(self.saveDir):
            i = 1
            origDir = self.saveDir
            while os.path.exists(self.saveDir):
                self.saveDir = origDir + str(i)
                i = i + 1

        # Make the directory
        os.makedirs(self.saveDir)
        # Save the files
        self.writeDataFile(self.saveDir + "\data.csv")  # Save the data as .csv
        self.matplotlibWidget.figure.savefig(self.saveDir + "\graph.png")  # Save the graph as .png
        self.writeMetadata(self.saveDir + "\metadata.txt")  # Save the metadat as .txt
        print("Saved the files in " + self.saveDir)


    def writeDataFile(self, dataFileName):
        dataShortcuts.writeCSV(dataFileName, [self.timeArr, self.dataArr], ["Time(sec)", dataLabel])

    def writeMetadata(self, metadataFileName):
        textFile = open(metadataFileName, 'w')
        textFile.write(self.metadata)
        textFile.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())