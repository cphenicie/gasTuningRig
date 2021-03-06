import numpy as np
import ctypes  # Lets us use data types compatible with C code
import PyDAQmx as pydaqmx  # Python library to execute NI-DAQmx code
import time


# Configure variables for measurement
fSamp = 50000  # Sampling frequency (maximum is 50000)
nSamp = 10  #  Therefore, our reading will be the average of 10 samples over 20us
tSamp = nSamp / float(fSamp)




#  samp_prog = tSamp / 0.01
#  sys.setrecursionlimit(int(samp_prog))  # I'm not sure if this is necessary...

## Create a task handle
readPressAvg = pydaqmx.TaskHandle()

## Create a task out of an existing handle
#int32 DAQmxCreateTask (const char taskName[], TaskHandle *taskHandle);
taskName = ''  # Name of the task (I don't know when this would not be an empty string...)
input1Pointer = ctypes.byref(readPressAvg)  # Equivalent to &setStates in C, the pointer to the task handle
pydaqmx.DAQmxCreateTask(taskName, input1Pointer)
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
pydaqmx.DAQmxCreateAIVoltageChan(readPressAvg, chan, chanName, termConfig, vMin, vMax, units, custUnits)

## Configure the clock
# int32 DAQmxCfgSampClkTiming (TaskHandle taskHandle, const char source[], float64 rate, int32 activeEdge, int32 sampleMode, uInt64 sampsPerChanToAcquire);
source = None   # If you use an external clock, specify here, otherwise it should be None
rate = pydaqmx.float64(fSamp)
edge = pydaqmx.DAQmx_Val_Rising  # Which edge of the clock (Rising/Falling) to acquire data
sampMode = pydaqmx.DAQmx_Val_FiniteSamps  # Acquire samples continuously or just a finite number of samples
sampPerChan = pydaqmx.uInt64(nSamp)
pydaqmx.DAQmxCfgSampClkTiming(readPressAvg, source, rate, edge, sampMode, sampPerChan)

## Read from the specified line(s)
# int32 DAQmxReadBinaryI16 (TaskHandle taskHandle, int32 numSampsPerChan, float64 timeout, bool32 fillMode, int16 readArray[], uInt32 arraySizeInSamps, int32 *sampsPerChanRead, bool32 *reserved);
nSampsPerChan = -1  # -1 in finite mode means wait until all samples are collected and read them
timeout = -1  # -1 means wait indefinitely to read the samples
fillMode = pydaqmx.DAQmx_Val_GroupByChannel  # Controls organization of output. Specifies if you want to prioritize by lowest channel or lowest sample (if you have mutiple channels each getting multiple samples)
readArr = data  # The array to read the samples into
arrSize = pydaqmx.uInt32(nSamp)
sampsPerChanRead = ctypes.byref(read)



def readPress():
    pydaqmx.DAQmxStartTask(readPressAvg)
    pydaqmx.DAQmxReadBinaryI16(readPressAvg, nSampsPerChan, timeout, fillMode, readArr, arrSize, sampsPerChanRead, None)
    #dataCal = data*(20.0/2**16)  # I Think this is the calibration
    dataCal = ( data * (20.0 / 2 ** 16) - 0.029 ) * 1/0.946  # This is the empirical calibration
    val = np.mean(dataCal)
    val_std = np.std(dataCal)
    print("%.4f +/- %.4f" %(val, val_std) )
    pydaqmx.DAQmxStopTask(readPressAvg)

readPress()
time.sleep(1)
readPress()
time.sleep(1)
readPress()