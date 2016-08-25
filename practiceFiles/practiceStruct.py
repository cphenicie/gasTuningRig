import sys
from PyQt4 import QtCore, QtGui, uic
import PyDAQmx as pydaqmx  # Python library to execute NI-DAQmx code
import ctypes

###### USER INPUT ######
dev = "Dev1/"  # The location of the device, which can be found in the program NI MAX -> Devices and Interfaces
digitalPort = "port0/"  # Which digital port the TTL pulses will come from (P0.x is port0)
gasLine = 1  # Which line within the above port is leading to the gas valve's circuit
pumpLine = 2
cryoLine = 7
analogPort = "ai3"  # Which analog input grouping the pressure sensor is hooked up to
### END USER INPUT #####


class Task():
    def __init__(self, nameArg, handleArg, lineArg, bitmaskArg):
        self.name = nameArg
        self.handle = handleArg
        self.line = lineArg
        self.bitmask = bitmaskArg

openGas = Task(nameArg='openGasValve',
               handleArg=pydaqmx.TaskHandle(),
               lineArg= dev + digitalPort + "line" + str(gasLine),
               bitmaskArg=2)

closeGas = Task(nameArg='closeGasValve',
               handleArg=pydaqmx.TaskHandle(),
               lineArg=dev + digitalPort + "line" + str(gasLine),
               bitmaskArg=0)

tasks = [openGas, closeGas]  # List containing all the task objects, so we can interate over them to do the rest of the setup.

taskName = ''  # Name of the task (I don't know when this would not be an empty string...)
lineNames = ""  # I don't know, from the help guide: "The name of the created virtual channel(s). If you create multiple virtual channels with one call to this function, you can specify a list of names separated by commas. If you do not specify a name, NI-DAQmx uses the physical channel name as the virtual channel name. If you specify your own names for nameToAssignToLines, you must use the names when you refer to these channels in other NI-DAQmx functions."
lineGrouping = pydaqmx.DAQmx_Val_ChanPerLine  #  I THINK this should allow you to only address 1 line instead of the entire port, but I see no difference between the two. Group digital lines into one (ChanPerLine) or more (ChanForAllLines) lines

for TaskObj in tasks:
    pydaqmx.DAQmxCreateTask( taskName, ctypes.byref( TaskObj.handle ))
    pydaqmx.DAQmxCreateDOChan( TaskObj.handle, TaskObj.line, lineNames, lineGrouping )

nSamps = 1  # Number of steps (or "samples") in the pulse sequence
autoSt = 1  # If 1, do not wait for pydaqmx.DAQmxStartTask()
tOut = pydaqmx.float64(
    10.0)  # Return an error if it takes longer than this many seconds to write the entire step sequence
dataLay = pydaqmx.DAQmx_Val_GroupByChannel  # Specify if the data are interleaved (GroupByChannel) or noninterleaved (GroupByScanNumber)


def doValveCmd(cmd):
    print(cmd)
    exec ("pydaqmx.DAQmxStartTask(%s)" % cmd)  # This line and the StopTask line are actually unnecessary, feel free to commment them out
    sampArr = np.array(bitmaskDict[cmd], dtype=pydaqmx.uInt32)
    exec ("pydaqmx.DAQmxWriteDigitalU32(%s, nSamps, autoSt, tOut, dataLay, sampArr, None, None)" % cmd)
    exec ("pydaqmx.DAQmxStopTask(%s)" % cmd)
