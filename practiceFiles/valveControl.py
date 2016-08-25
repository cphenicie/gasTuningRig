import PyDAQmx as pydaqmx  # Python library to execute NI-DAQmx code
import numpy as np
import ctypes  # Lets us use data types compatible with C code
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time


gasLine = 1
vacLine = 2
cryLine = 7

portGasValve = "Dev1/port0/line"+str(gasLine)
portVacValve = "Dev1/port0/line"+str(vacLine)
portCryValve = "Dev1/port0/line"+str(cryLine)

## Create tasks
tasks = ["openGasValve", "closeGasValve", "openVacValve", "closeVacValve", "openCryValve", "closeCryValve"]
portDict = {'openGasValve' : portGasValve,
            'closeGasValve' : portGasValve,
            'openVacValve': portVacValve,
            'closeVacValve': portVacValve,
            'openCryValve' : portCryValve,
            'closeCryValve' : portCryValve
            }

## Value should be 2 ** (line number)
bitmaskDict = {'openGasValve' : 2**gasLine,
            'closeGasValve' : 0,
            'openVacValve': 2**vacLine,
            'closeVacValve': 0,
            'openCryValve' : 2**cryLine,
            'closeCryValve' : 0
            }

taskName = ''  # Name of the task (I don't know when this would not be an empty string...)
lineNames = ""  # I don't know, from the help guide: "The name of the created virtual channel(s). If you create multiple virtual channels with one call to this function, you can specify a list of names separated by commas. If you do not specify a name, NI-DAQmx uses the physical channel name as the virtual channel name. If you specify your own names for nameToAssignToLines, you must use the names when you refer to these channels in other NI-DAQmx functions."
lineGrouping = pydaqmx.DAQmx_Val_ChanPerLine  #  I THINK this should allow you to only address 1 line instead of the entire port, but I see no difference between the two. Group digital lines into one (ChanPerLine) or more (ChanForAllLines) lines


## Initialize the tasks
for taskVar in tasks:
    exec("%s = pydaqmx.TaskHandle()" % taskVar)
    exec("pydaqmx.DAQmxCreateTask( taskName, ctypes.byref( %s ))" % taskVar)
    exec("pydaqmx.DAQmxCreateDOChan(%s, %s, %s, %s)" % (taskVar, "portDict[taskVar]", "lineNames", "lineGrouping") )
    # print("%s = pydaqmx.TaskHandle()" % taskVar)
    # print("pydaqmx.DAQmxCreateTask( taskName, ctypes.byref( %s ))" % taskVar)
    # print("pydaqmx.DAQmxCreateDOChan(%s, %s, %s, %s)" % (taskVar, "portDict[taskVar]", "lineNames", "lineGrouping"))


## Set the necessary variables
nSamps = 1  # Number of steps (or "samples") in the pulse sequence
autoSt = 1  # If 1, do not wait for pydaqmx.DAQmxStartTask()
tOut = pydaqmx.float64(10.0)  #  Return an error if it takes longer than this many seconds to write the entire step sequence
dataLay = pydaqmx.DAQmx_Val_GroupByChannel  # Specify if the data are interleaved (GroupByChannel) or noninterleaved (GroupByScanNumber)

# ## for GasValve
# sampArr = np.array(bitmaskDict['closeGasValve'], dtype=pydaqmx.uInt32)  # Array containing the bit values for each "sample" (step in the sequence). The value is a decimal value corresponding to a "binary" string representing which outputs are on. For instance, to turn outputs P0.0 and P0.3 on and the rest off, in "binary" this is 00000000000000000000000000001001 = 9 (in decimal). To turn all the outputs on (since we only have 8 outputs) this is 00000000000000000000000011111111 = 255
# pydaqmx.DAQmxWriteDigitalU32(closeGasValve, nSamps, autoSt, tOut, dataLay, sampArr, None, None)

def doValveCmd(cmd):
    exec ("pydaqmx.DAQmxStartTask(%s)" %cmd)  # This line and the StopTask line are actually unnecessary, feel free to commment them out
    sampArr = np.array(bitmaskDict[cmd], dtype=pydaqmx.uInt32)
    exec("pydaqmx.DAQmxWriteDigitalU32(%s, nSamps, autoSt, tOut, dataLay, sampArr, None, None)" % cmd)
    exec ("pydaqmx.DAQmxStopTask(%s)" % cmd)


## Notice, pulses end up being between 1 and 2 ms too long (somewhat inconsistently)
# while 1:
#     time.sleep(5)
#     doValveCmd("openGasValve")
#     time.sleep(5)
    #doValveCmd("closeGasValve")
doValveCmd("openGasValve")