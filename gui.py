# If this doesn't work, remember,you changed makeAnalogIn in PyDAQshortcuts
#
# Bug: If you start multiple timers in multiple instances of doOperation, only the last one will actually be connected
# to the timeout

# This code communicates with and NI USB 6002 DAQ (or equivalent) to send out TTL pulses and read in a voltage. This is
# controlled by a GUI created with Qt Designer that will allow buttons to set TTL values to high or low, send a TTL
# pulse of a specific length, and continuously monitor the voltage reading.

import sys
from PyQt4 import QtCore, QtGui, uic
import PyDAQmx as pydaqmx  # Python library to execute NI-DAQmx code
import numpy as np
from PyDAQshortcuts import TTLSwitch, makeAnalogIn, getAnalogIn
import serial

qtCreatorFile = "tuningRigGUI.ui"  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

###### USER INPUT ######
dev = "Dev2/"  # The location of the device, which can be found in the program NI MAX -> Devices and Interfaces. MAKE SURE TO END STRING IN A "/"
digitalPort = "port1/"  # Which digital port the TTL pulses will come from (P0.x is port0) MAKE SURE TO END STRING IN A "/"
gasLine = 3  # Which line within the above port is leading to the gas valve's circuit
pumpLine = 2
cryoLine = 0
analogPort = "ai3"  # Which analog input grouping the pressure sensor is hooked up to
### END USER INPUT #####



######## Configure analog input from the pressure sensor ##########
# fSamp = 50000  # Sampling frequency (maximum is 50000)
# nSamp = 10  # Therefore, our reading will be the average of 10 samples over 200us
# readPressAvg = pydaqmx.TaskHandle()
# data = np.zeros((int(nSamp),), dtype=np.int16)
#makeAnalogIn(dev + analogPort, readPressAvg, fSamp, nSamp)

###### Configure pressure sensor using RS232 connection #####
ser = serial.Serial('COM3', 9600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)

###### Configure digital switches for valves ######
gasSwitch = TTLSwitch(dev, digitalPort, gasLine)
cryoSwitch = TTLSwitch(dev, digitalPort, cryoLine)
pumpSwitch = TTLSwitch(dev, digitalPort, pumpLine)


###### Configure the options in the Set Valve Operations menu #####
# Dictionary that connects the option chosen on the GUI to a switch in this code. String should match the option on the GUI exactly, the definition should be the swtich it opens
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

        self.opGo.clicked.connect(self.doOperation)

        # Continuously update pressure
        self.showPressure()
        self.myTimer = QtCore.QTimer()  # Use QTimer because time.sleep() pauses ALL functionality while sleeping
        self.myTimer.timeout.connect(self.showPressure)  # Every time myTimer times out, execute showPressure()
        self.myTimer.start(1000)  # Update every second
        self.show()

    def doOperation(self):
        valve = str(self.opValveChoice.currentText())
        openTime = (self.opOpenTime.value())
        choiceDict[valve].high()
        self.opTimer = QtCore.QTimer()  # Use QTimer because time.sleep() pauses ALL functionality while sleeping
        self.opTimer.setSingleShot(True)
        self.opTimer.timeout.connect(lambda: choiceDict[valve].low())
        self.opTimer.start(openTime)

    def showPressure(self):
        # getAnalogIn(readPressAvg, data)
        # dataCal = (data * (20.0 / 2 ** 16) - 0.029) * 1 / 0.946  # This is the empirical calibration
        # val = np.mean(dataCal)  # average over the 10 consecutive values
        # val_std = np.std(dataCal)  # standard deviation of the mean
        # self.pressureWindow.setText("%.4f +/- %.4f" % (val, val_std))  # Write the pressure to the GUI
        pressStr = ser.readline
        self.pressureWindow.setText(pressStr[0:4])  # Write the pressure to the GUI

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())