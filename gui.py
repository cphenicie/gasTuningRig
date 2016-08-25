# This code communicates with and NI USB 6002 DAQ (or equivalent) to send out TTL pulses and read in a voltage. This is
# controlled by a GUI created with Qt Designer that will allow buttons to set TTL values to high or low, send a TTL
# pulse of a specific length, and continuously monitor the voltage reading.

import sys
from PyQt4 import QtCore, QtGui, uic
import PyDAQmx as pydaqmx  # Python library to execute NI-DAQmx code
import numpy as np
import ctypes  # Lets us use data types compatible with C code

qtCreatorFile = "tuningRigGUI.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

###### USER INPUT ######
dev = "Dev1/"  # The location of the device, which can be found in the program NI MAX -> Devices and Interfaces
digitalPort = "port0/"  # Which digital port the TTL pulses will come from (P0.x is port0)
gasLine = 1  # Which line within the above port is leading to the gas valve's circuit
pumpLine = 2
cryoLine = 7
analogPort = "ai3"  # Which analog input grouping the pressure sensor is hooked up to
### END USER INPUT #####


## First, configure some global variables. The real meat of the code starts at the line "class MyApp(QtGui.QMainWindow, Ui_MainWindow):"

######## Variables to read the analog input from the pressure sensor ##########
fSamp = 50000  # Sampling frequency (maximum is 50000)
nSamp = 10  # Therefore, our reading will be the average of 10 samples over 20us
tSamp = nSamp / float(fSamp)

## Create a task handle
readPressAvg = pydaqmx.TaskHandle()

## Create a task out of an existing handle
# int32 DAQmxCreateTask (const char taskName[], TaskHandle *taskHandle);
taskName = ''  # Name of the task (I don't know when this would not be an empty string...)
input1Pointer = ctypes.byref(readPressAvg)  # Equivalent to &setStates in C, the pointer to the task handle
pydaqmx.DAQmxCreateTask(taskName, input1Pointer)
read = pydaqmx.int32()
data = np.zeros((int(nSamp),), dtype=np.int16)

## Create Analog In voltage channel
# int32 DAQmxCreateAIVoltageChan (TaskHandle taskHandle, const char physicalChannel[], const char nameToAssignToChannel[], int32 terminalConfig, float64 minVal, float64 maxVal, int32 units, const char customScaleName[]);
chan = dev+analogPort  # Location of the channel (this should be a physical channel, but it will be used as a virtual channel?)
chanName = ""  # Name(s) to assign to the created virtual channel(s). "" means physical channel name will be used
termConfig = pydaqmx.DAQmx_Val_Diff  # Is this singled/double referenced, differential, etc.\
vMin = -10  # Minimum voltage you expect to measure (in units described by variable "units" below)
vMax = 10  # Maximum voltage you expect to measure
units = pydaqmx.DAQmx_Val_Volts # Units used in vMax/vMin.
custUnits = None  # If units where DAQmx_Val_FromCustomScale, specify scale. Otherwise, it should be None
pydaqmx.DAQmxCreateAIVoltageChan(readPressAvg, chan, chanName, termConfig, vMin, vMax, units, custUnits)

## Configure the clock
# int32 DAQmxCfgSampClkTiming (TaskHandle taskHandle, const char source[], float64 rate, int32 activeEdge, int32 sampleMode, uInt64 sampsPerChanToAcquire);
source = None  # If you use an external clock, specify here, otherwise it should be None
rate = pydaqmx.float64(fSamp)
edge = pydaqmx.DAQmx_Val_Rising  # Which edge of the clock (Rising/Falling) to acquire data
sampMode = pydaqmx.DAQmx_Val_FiniteSamps  # Acquire samples continuously or just a finite number of samples
sampPerChan = pydaqmx.uInt64(nSamp)
pydaqmx.DAQmxCfgSampClkTiming(readPressAvg, source, rate, edge, sampMode, sampPerChan)

## Other variables we need for
# int32 DAQmxReadBinaryI16 (TaskHandle taskHandle, int32 numSampsPerChan, float64 timeout, bool32 fillMode, int16 readArray[], uInt32 arraySizeInSamps, int32 *sampsPerChanRead, bool32 *reserved);
nSampsPerChan = -1  # -1 in finite mode means wait until all samples are collected and read them
timeout = -1  # -1 means wait indefinitely to read the samples
fillMode = pydaqmx.DAQmx_Val_GroupByChannel  # Controls organization of output. Specifies if you want to prioritize by lowest channel or lowest sample (if you have mutiple channels each getting multiple samples)
readArr = data  # The array to read the samples into
arrSize = pydaqmx.uInt32(nSamp)
sampsPerChanRead = ctypes.byref(read)


###############   Configure digital output channels to make TTL Pulses #####################
## Note the characters following "open" and "close" need to match the options in the GUI's Set Valve Operation drop down menu exactly
tasks = ["openGasValve", "closeGasValve", "openPumpValve", "closePumpValve", "openCryoValve", "closeCryoValve"]
portDict = {'openGasValve' : dev + digitalPort + "line" + str(gasLine),
            'closeGasValve' : dev + digitalPort + "line" + str(gasLine),
            'openPumpValve': dev + digitalPort + "line" + str(pumpLine),
            'closePumpValve': dev + digitalPort + "line" + str(pumpLine),
            'openCryoValve' : dev + digitalPort + "line" + str(cryoLine),
            'closeCryoValve' : dev + digitalPort + "line" + str(cryoLine)
            }

## Value should be 2 ** (line number)
bitmaskDict = {'openGasValve' : 2**gasLine,
            'closeGasValve' : 0,
            'openPumpValve': 2**pumpLine,
            'closePumpValve': 0,
            'openCryoValve' : 2**cryoLine,
            'closeCryoValve' : 0
            }

taskName = ''  # Name of the task (I don't know when this would not be an empty string...)
lineNames = ""  # I don't know, from the help guide: "The name of the created virtual channel(s). If you create multiple virtual channels with one call to this function, you can specify a list of names separated by commas. If you do not specify a name, NI-DAQmx uses the physical channel name as the virtual channel name. If you specify your own names for nameToAssignToLines, you must use the names when you refer to these channels in other NI-DAQmx functions."
lineGrouping = pydaqmx.DAQmx_Val_ChanPerLine  #  I THINK this should allow you to only address 1 line instead of the entire port, but I see no difference between the two. Group digital lines into one (ChanPerLine) or more (ChanForAllLines) lines

## Initialize the tasks
for taskVar in tasks:
    exec("%s = pydaqmx.TaskHandle()" % taskVar)
    exec("pydaqmx.DAQmxCreateTask( taskName, ctypes.byref( %s ))" % taskVar)
    exec("pydaqmx.DAQmxCreateDOChan(%s, %s, %s, %s)" % (taskVar, "portDict[taskVar]", "lineNames", "lineGrouping") )


## Set the necessary variables
nSamps = 1  # Number of steps (or "samples") in the pulse sequence
autoSt = 1  # If 1, do not wait for pydaqmx.DAQmxStartTask()
tOut = pydaqmx.float64(10.0)  #  Return an error if it takes longer than this many seconds to write the entire step sequence
dataLay = pydaqmx.DAQmx_Val_GroupByChannel  # Specify if the data are interleaved (GroupByChannel) or noninterleaved (GroupByScanNumber)


def doValveCmd(cmd):
    print(cmd)
    exec ("pydaqmx.DAQmxStartTask(%s)" % cmd)  # This line and the StopTask line are actually unnecessary, feel free to commment them out
    sampArr = np.array(bitmaskDict[cmd], dtype=pydaqmx.uInt32)
    exec ("pydaqmx.DAQmxWriteDigitalU32(%s, nSamps, autoSt, tOut, dataLay, sampArr, None, None)" % cmd)
    exec ("pydaqmx.DAQmxStopTask(%s)" % cmd)




class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.openGasButton.clicked.connect(lambda: doValveCmd('openGasValve'))
        self.closeGasButton.clicked.connect(lambda: doValveCmd('closeGasValve'))
        self.openCryoButton.clicked.connect(lambda: doValveCmd('openCryoValve'))
        self.closeCryoButton.clicked.connect(lambda: doValveCmd('closeCryoValve'))
        self.openPumpButton.clicked.connect(lambda: doValveCmd('openPumpValve'))
        self.closePumpButton.clicked.connect(lambda: doValveCmd('closePumpValve'))

        self.opGo.clicked.connect(self.doOperation)

        self.showPressure()
        #  Use QTimer instead of time.sleep() because time.sleep() pauses ALL functionality while sleeping
        self.myTimer = QtCore.QTimer()
        self.myTimer.timeout.connect(self.showPressure)
        self.myTimer.start(1000)  # Update every second
        self.show()


    def doOperation(self):
        valve = str(self.opValveChoice.currentText())
        openTime = (self.opOpenTime.value())
        doValveCmd('open'+valve)
        #  Use QTimer instead of time.sleep() because time.sleep() pauses ALL functionality while sleeping
        self.opTimer = QtCore.QTimer()
        self.opTimer.setSingleShot(True)
        self.opTimer.timeout.connect(lambda: doValveCmd('close'+valve))
        self.opTimer.start(openTime)  # Update every second

    def showPressure(self):
        pydaqmx.DAQmxStartTask(readPressAvg)
        pydaqmx.DAQmxReadBinaryI16(readPressAvg, nSampsPerChan, timeout, fillMode, readArr, arrSize, sampsPerChanRead, None)  # This is the line when you actually read the voltage
        # dataCal = data*(20.0/2**16)  # I Think this is the calibration from DAQ arbitrary units to volts
        dataCal = (data * (20.0 / 2 ** 16) - 0.029) * 1 / 0.946  # This is the empirical calibration
        val = np.mean(dataCal)  # average over the 10 consecutive values
        val_std = np.std(dataCal)  # standard deviation of the mean
        self.pressureWindow.setText("%.4f +/- %.4f" %(val, val_std))  # Write the pressure to the GUI
        pydaqmx.DAQmxStopTask(readPressAvg)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())