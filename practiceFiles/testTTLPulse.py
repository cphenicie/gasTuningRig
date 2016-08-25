# For more help on functions within pydaqmx, check the NI-DAQmx C Reference Help, and make sure to use the entire
# function name in the search

import PyDAQmx as pydaqmx  # Python library to execute NI-DAQmx code
import numpy as np
import ctypes  # Lets us use data types compatible with C code
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#
# ## Specify the device and port(s) we will be using
# #### NOTE: If you address an entire port you might see random pulses whenever you right lines. For instance, you might
# #### have line 7 off and write "1" (which should turn on line 1 and turn off the rest of the lines) and see line 7 pulse
# #### to on for 1 ms. If you address lines individually you do not have this problem.
# dev = "Dev1"
# port = "Dev1/port0/line1"
#
# ## Create a task handle
# setStates = pydaqmx.TaskHandle()
#
# ## Create a task out of an existing handle
# #int32 DAQmxCreateTask (const char taskName[], TaskHandle *taskHandle);
# taskName = ''  # Name of the task (I don't know when this would not be an empty string...)
# thPointer = ctypes.byref(setStates)  # Equivalent to &setStates in C, the pointer to the task handle
# pydaqmx.DAQmxCreateTask(taskName, thPointer)
#
# ## Create a digital output channel
# # int32 DAQmxCreateDOChan (TaskHandle taskHandle, const char lines[], const char nameToAssignToLines[], int32 lineGrouping);
# lineNames = ""  # I don't know, from the help guide: "The name of the created virtual channel(s). If you create multiple virtual channels with one call to this function, you can specify a list of names separated by commas. If you do not specify a name, NI-DAQmx uses the physical channel name as the virtual channel name. If you specify your own names for nameToAssignToLines, you must use the names when you refer to these channels in other NI-DAQmx functions."
# lineGrouping = pydaqmx.DAQmx_Val_ChanForAllLines  #  I THINK this should allow you to only address 1 line instead of the entire port, but I see no difference between the two. Group digital lines into one (ChanPerLine) or more (ChanForAllLines) lines
# pydaqmx.DAQmxCreateDOChan(setStates, port, lineNames, lineGrouping)
#
# ## Write the TTL pulse
# #while 1:  # If you run it through this loop, you can see the default is a 1ms pulse with a period of 33 ms
# # int32 DAQmxWriteDigitalU32 (TaskHandle taskHandle, int32 numSampsPerChan, bool32 autoStart, float64 timeout, bool32 dataLayout, uInt32 writeArray[], int32 *sampsPerChanWritten, bool32 *reserved);
# nSamps = 1  # Number of steps (or "samples") in the pulse sequence
# autoSt = 1  # If 1, do not wait for pydaqmx.DAQmxStartTask()
# tOut = pydaqmx.float64(10.0)  #  Return an error if it takes longer than this many seconds to write the entire step sequence
# dataLay = pydaqmx.DAQmx_Val_GroupByChannel  # Specify if the data are interleaved (GroupByChannel) or noninterleaved (GroupByScanNumber)
# sampArr = np.array(0, dtype=pydaqmx.uInt32)  # Array containing the bit values for each "sample" (step in the sequence). The value is a decimal value corresponding to a "binary" string representing which outputs are on. For instance, to turn outputs P0.0 and P0.3 on and the rest off, in "binary" this is 00000000000000000000000000001001 = 9 (in decimal). To turn all the outputs on (since we only have 8 outputs) this is 00000000000000000000000011111111 = 255
# pydaqmx.DAQmxWriteDigitalU32(setStates, nSamps, autoSt, tOut, dataLay,sampArr , None, None)

# #
# # ## Configure the internal clock in case we want really precise timing
# ##### For now, uncommenting this block breaks the code
# # # int32 DAQmxCfgSampClkTiming (TaskHandle taskHandle, const char source[], float64 rate, int32 activeEdge, int32 sampleMode, uInt64 sampsPerChanToAcquire);
# # clock = None  # Source terminal of the sample clock. In
# # rate = pydaqmx.float64(1000) # Sampling rate, which apparently can be set to any value less than I THINK 50000 (manual says analog sample rate is 50kS/s, but meanual also shows 80MHz Clock on pg 7...)
# # edge = pydaqmx.DAQmx_Val_Rising  # Acquire or generate on Rising or Falling edge
# # sampMode = pydaqmx.DAQmx_Val_FiniteSamps
# # nPts = pydaqmx.uInt64(1000)  # Number of samples you will actually collect during the task (so we can make the correct sized buffer)
# # pydaqmx.DAQmxCfgSampClkTiming(setStates, clock, rate, edge, sampMode, nPts)
# #
# #
# ## Write the TTL pulse
# #while 1:  # If you run it through this loop, you can see the default is a 1ms pulse with a period of 33 ms
# # int32 DAQmxWriteDigitalU32 (TaskHandle taskHandle, int32 numSampsPerChan, bool32 autoStart, float64 timeout, bool32 dataLayout, uInt32 writeArray[], int32 *sampsPerChanWritten, bool32 *reserved);
# nSamps = 1  # Number of steps (or "samples") in the pulse sequence
# autoSt = 1  # If 1, do not wait for pydaqmx.DAQmxStartTask()
# tOut = pydaqmx.float64(10.0)  #  Return an error if it takes longer than this many seconds to write the entire step sequence
# dataLay = pydaqmx.DAQmx_Val_GroupByChannel  # Specify if the data are interleaved (GroupByChannel) or noninterleaved (GroupByScanNumber)
# sampArr = np.array(0, dtype=pydaqmx.uInt32)  # Array containing the bit values for each "sample" (step in the sequence). The value is a decimal value corresponding to a "binary" string representing which outputs are on. For instance, to turn outputs P0.0 and P0.3 on and the rest off, in "binary" this is 00000000000000000000000000001001 = 9 (in decimal). To turn all the outputs on (since we only have 8 outputs) this is 00000000000000000000000011111111 = 255
# pydaqmx.DAQmxWriteDigitalU32(setStates, nSamps, autoSt, tOut, dataLay ,sampArr , None, None)










# Configure variables for measurement
fSamp = 1000  # Sampling frequency (maximum is 50000)
nSamp = 50
tSamp = nSamp / float(fSamp)

#  samp_prog = tSamp / 0.01
#  sys.setrecursionlimit(int(samp_prog))  # I'm not sure if this is necessary...

## Create a task handle
input1 = pydaqmx.TaskHandle()

## Create a task out of an existing handle
#int32 DAQmxCreateTask (const char taskName[], TaskHandle *taskHandle);
taskName = ''  # Name of the task (I don't know when this would not be an empty string...)
input1Pointer = ctypes.byref(input1)  # Equivalent to &setStates in C, the pointer to the task handle
pydaqmx.DAQmxCreateTask(taskName, input1Pointer)
#  input1 = pydaqmx.Task()
read = pydaqmx.int32()
data = np.zeros((int(nSamp),), dtype = np.int16)

## Create Analog In voltage channel
# int32 DAQmxCreateAIVoltageChan (TaskHandle taskHandle, const char physicalChannel[], const char nameToAssignToChannel[], int32 terminalConfig, float64 minVal, float64 maxVal, int32 units, const char customScaleName[]);
chan = "Dev1/ai3"  # Location of the channel (this should be a physical channel, but it will be used as a virtual channel?)
chanName = ""  # Name(s) to assign to the created virtual channel(s). "" means physical channel name will be used
termConfig = pydaqmx.DAQmx_Val_Diff  # Is this singled/double referenced, differential, etc.\
vMin = -10  # Minimum voltage you expect to measure (in units described by variable "units" below)
vMax = 10  # Maximum voltage you expect to measure
units = pydaqmx.DAQmx_Val_Volts  # Units used in vMax/vMin.
custUnits = None  # If units where DAQmx_Val_FromCustomScale, specify scale. Otherwise, it should be None
pydaqmx.DAQmxCreateAIVoltageChan(input1, chan, chanName, termConfig, vMin, vMax, units, custUnits)

## Configure the clock
# int32 DAQmxCfgSampClkTiming (TaskHandle taskHandle, const char source[], float64 rate, int32 activeEdge, int32 sampleMode, uInt64 sampsPerChanToAcquire);
source = None   # If you use an external clock, specify here, otherwise it should be None
#rate = c_double(fSamp).value  # Sampling rate in samples/second/channel
rate = pydaqmx.float64(fSamp)
edge = pydaqmx.DAQmx_Val_Rising  # Which edge of the clock (Rising/Falling) to acquire data
sampMode = pydaqmx.DAQmx_Val_FiniteSamps  # Acquire samples continuously or just a finite number of samples
#sampPerChan = c_ulonglong(int(nSamp)).value  # The number of samples to acquire or generate for each channel in the task if sampleMode is DAQmx_Val_FiniteSamps. If sampleMode is DAQmx_Val_ContSamps, NI-DAQmx uses this value to determine the buffer size.
sampPerChan = pydaqmx.uInt64(nSamp)
pydaqmx.DAQmxCfgSampClkTiming(input1, source, rate, edge, sampMode, sampPerChan)


## Create constantly updating plot
fig = plt.figure()
def animate(i):
    plt.clf()
    pydaqmx.DAQmxStartTask(input1)

    ## Read from the specified line(s)
    # int32 DAQmxReadBinaryI16 (TaskHandle taskHandle, int32 numSampsPerChan, float64 timeout, bool32 fillMode, int16 readArray[], uInt32 arraySizeInSamps, int32 *sampsPerChanRead, bool32 *reserved);
    nSampsPerChan = -1  # -1 in finite mode means wait until all samples are collected and read them
    timeout = -1  # -1 means wait indefinitely to read the samples
    fillMode = pydaqmx.DAQmx_Val_GroupByChannel  # Controls organization of output. Specifies if you want to prioritize by lowest channel or lowest sample (if you have mutiple channels each getting multiple samples)
    readArr = data  # The array to read the samples into
    #arrSize = c_uint32(int(nSamp)).value  # size of the read array
    arrSize = pydaqmx.uInt32(nSamp)
    sampsPerChanRead = ctypes.byref(read)
    pydaqmx.DAQmxReadBinaryI16(input1, nSampsPerChan, timeout, fillMode, readArr, arrSize, sampsPerChanRead, None)


    pydaqmx.DAQmxStopTask(input1)
    # filename = "test.csv"
    # np.savetxt(filename, data, delimiter=",")
    tMS = (np.arange(0,nSamp)/float(fSamp))*1e3
    dataCal = data*(20.0/2**16)
    plt.plot(tMS,dataCal)
    #plt.plot(data)
    plt.xlabel('Time (ms)')
    plt.ylabel('Signal (V)')

ani = animation.FuncAnimation(fig, animate, interval=500)
plt.show()




# If you'd rather save data to a file
pydaqmx.DAQmxStartTask(input1)

## Read from the specified line(s)
# int32 DAQmxReadBinaryI16 (TaskHandle taskHandle, int32 numSampsPerChan, float64 timeout, bool32 fillMode, int16 readArray[], uInt32 arraySizeInSamps, int32 *sampsPerChanRead, bool32 *reserved);
nSampsPerChan = -1  # -1 in finite mode means wait until all samples are collected and read them
timeout = -1  # -1 means wait indefinitely to read the samples
fillMode = pydaqmx.DAQmx_Val_GroupByChannel  # Controls organization of output. Specifies if you want to prioritize by lowest channel or lowest sample (if you have mutiple channels each getting multiple samples)
readArr = data  # The array to read the samples into
#arrSize = c_uint32(int(nSamp)).value  # size of the read array
arrSize = pydaqmx.uInt32(nSamp)
sampsPerChanRead = ctypes.byref(read)
pydaqmx.DAQmxReadBinaryI16(input1, nSampsPerChan, timeout, fillMode, readArr, arrSize, sampsPerChanRead, None)

#
# pydaqmx.DAQmxStopTask(input1)
# filename = "test.csv"
# np.savetxt(filename, data, delimiter=",")







##### Here's an example importing PyDAQmx *, giving more concise code

# from PyDAQmx import *
# import numpy as np
# import ctypes
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
#
#
# ## Configure variables for measurement
# fSamp = 20000.0  # Sampling frequency (maximum is 50000)
# nSamp = 50.0
# tSamp = nSamp / fSamp
#
# #  samp_prog = tSamp / 0.01
# #  sys.setrecursionlimit(int(samp_prog))  # I'm not sure if this is necessary...
#
#
# ## Create Task object and data object to store the information
# input1 = Task()
# read = int32()
# data = np.zeros((int(nSamp),), dtype = np.int16)
#
# ## Create Analog In voltage channel
# # int32 DAQmxCreateAIVoltageChan (TaskHandle taskHandle, const char physicalChannel[], const char nameToAssignToChannel[], int32 terminalConfig, float64 minVal, float64 maxVal, int32 units, const char customScaleName[]);
# chan = "Dev1/ai3"  # Location of the channel (this should be a physical channel, but it will be used as a virtual channel?)
# chanName = ""  # Name(s) to assign to the created virtual channel(s). "" means physical channel name will be used
# termConfig = DAQmx_Val_Diff  # Is this singled/double referenced, differential, etc.\
# vMin = -10  # Minimum voltage you expect to measure (in units described by variable "units" below)
# vMax = 10  # Maximum voltage you expect to measure
# units = DAQmx_Val_Volts  # Units used in vMax/vMin.
# custUnits = None  # If units where DAQmx_Val_FromCustomScale, specify scale. Otherwise, it should be None
# input1.CreateAIVoltageChan(chan, chanName, termConfig, vMin, vMax, units, custUnits)
#
# ## Configure the clock
# # int32 DAQmxCfgSampClkTiming (TaskHandle taskHandle, const char source[], float64 rate, int32 activeEdge, int32 sampleMode, uInt64 sampsPerChanToAcquire);
# source = None   # If you use an external clock, specify here, otherwise it should be None
# rate = c_double(fSamp).value  # Sampling rate in samples/second/channel
# #rate = ctypes.float64(fSamp)
# edge = DAQmx_Val_Rising  # Which edge of the clock (Rising/Falling) to acquire data
# sampMode = DAQmx_Val_FiniteSamps  # Acquire samples continuously or just a finite number of samples
# sampPerChan = c_ulonglong(int(nSamp)).value  # The number of samples to acquire or generate for each channel in the task if sampleMode is DAQmx_Val_FiniteSamps. If sampleMode is DAQmx_Val_ContSamps, NI-DAQmx uses this value to determine the buffer size.
# #sampsperChan = ctypes.uInt64(nSamp)
# input1.CfgSampClkTiming(source, rate, edge, sampMode, sampPerChan)
#
#
# ## Create constantly updating plot
# fig = plt.figure()
# def animate(i):
#     plt.clf()
#     input1.StartTask()
#
#     ## Read from the specified line(s)
#     # int32 DAQmxReadBinaryI16 (TaskHandle taskHandle, int32 numSampsPerChan, float64 timeout, bool32 fillMode, int16 readArray[], uInt32 arraySizeInSamps, int32 *sampsPerChanRead, bool32 *reserved);
#     nSampsPerChan = -1  # -1 in finite mode means wait until all samples are collected and read them
#     timeout = -1  # -1 means wait indefinitely to read the samples
#     fillMode = DAQmx_Val_GroupByChannel  # Controls organization of output. Specifies if you want to prioritize by lowest channel or lowest sample (if you have mutiple channels each getting multiple samples)
#     readArr = data  # The array to read the samples into
#     arrSize = c_uint32(int(nSamp)).value  # size of the read array
#     #arrSize = ctypes.uInt32(nSamp)
#     sampsPerChanRead = ctypes.byref(read)
#     input1.ReadBinaryI16(nSampsPerChan, timeout, fillMode, readArr, arrSize, sampsPerChanRead, None)
#
#
#     input1.StopTask()
#     # filename = "test.csv"
#     # np.savetxt(filename, data, delimiter=",")
#     tMS = (np.arange(0,nSamp)/fSamp)*1e3
#     dataCal = data*(20.0/2**16)
#     plt.plot(tMS,dataCal)
#     plt.ylabel('Time (ms)')
#     plt.xlabel('Signal (V)')
#
# ani = animation.FuncAnimation(fig, animate, interval=500)
# plt.show()
