# TODO:
# Put userBand in CSV filename (will need to export userBand from Python to bash)
# Clean up User Settings string that prints to terminal


#======================================================================================
# Modified example code. Original file RFE_Example_USB_2.py
#======================================================================================

import time
import RFExplorer
from RFExplorer import RFE_Common 
import math
import bandLookup

#---------------------------------------------------------
# Helper functions
#---------------------------------------------------------

def PrintScan(objAnalyzer, scanCount): # This one I actually wrote
    nIndex = objAnalyzer.SweepData.Count-1
    objSweepTemp = objAnalyzer.SweepData.GetData(nIndex)
    objSweepTemp.SaveFileCSV("scan-temp-" + str(scanCount) + '.csv', ';', 0)

    #Print Progress
    print("Scanning " + str("{0:.3f}".format(StartFreq)) + " - " + str("{0:.3f}".format(StopFreq)) + " (" + str(scanCount) + " of " + str(nScans) + ")")

def cls(): #lazy clear screen
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

def ControlSettings(objAnalazyer):
    """This functions check user settings 
    """
    SpanSizeTemp = None
    StartFreqTemp = None
    StopFreqTemp =  None

    #print user settings
    print("User settings:" + "Span: " + str(SPAN_SIZE_MHZ) +"MHz"+  " - " + "Start freq: " + str(START_SCAN_MHZ) +"MHz"+" - " + "Stop freq: " + str(STOP_SCAN_MHZ) + "MHz")

    #Control maximum Span size
    if(objAnalazyer.MaxSpanMHZ <= SPAN_SIZE_MHZ):
        print("Max Span size: " + str(objAnalazyer.MaxSpanMHZ)+"MHz")
    else:
        objAnalazyer.SpanMHZ = SPAN_SIZE_MHZ
        SpanSizeTemp = objAnalazyer.SpanMHZ
    if(SpanSizeTemp):
        #Control minimum start frequency
        if(objAnalazyer.MinFreqMHZ > START_SCAN_MHZ):
            print("Min Start freq: " + str(objAnalazyer.MinFreqMHZ)+"MHz")
        else:
            objAnalazyer.StartFrequencyMHZ = START_SCAN_MHZ
            StartFreqTemp = objAnalazyer.StartFrequencyMHZ    
        if(StartFreqTemp):
            #Control maximum stop frequency
            if(objAnalazyer.MaxFreqMHZ < STOP_SCAN_MHZ):
                print("Max Start freq: " + str(objAnalazyer.MaxFreqMHZ)+"MHz")
            else:
                if((StartFreqTemp + SpanSizeTemp) > STOP_SCAN_MHZ):
                    print("Max Stop freq (START_SCAN_MHZ + SPAN_SIZE_MHZ): " + str(STOP_SCAN_MHZ) +"MHz")
                else:
                    StopFreqTemp = (StartFreqTemp + SpanSizeTemp)
    
    return SpanSizeTemp, StartFreqTemp, StopFreqTemp

#---------------------------------------------------------
# global variables and initialization
#---------------------------------------------------------

SERIALPORT = '/dev/ttyUSB0'   #serial port identifier, use None to autodetect
BAUDRATE = 500000

objRFE = RFExplorer.RFECommunicator()     #Initialize object and thread
objRFE.AutoConfigure = False

#These values can be limited by specific RF Explorer Spectrum Analyzer model. 
#Check RFE SA Comparation chart from www.rf-explorer.com\models to know what
#frequency setting are available for your model
#These freq settings will be updated later in SA condition.
SPAN_SIZE_MHZ = 13.875           #Initialize settings
START_SCAN_MHZ = 240
STOP_SCAN_MHZ = 960

#---------------------------------------------------------
# Main processing loop
#---------------------------------------------------------

try:
    #Find and show valid serial ports
    objRFE.GetConnectedPorts()

    #Connect to available port
    if (objRFE.ConnectPort(SERIALPORT, BAUDRATE)): 
        #If unit is resetting, wait
        while(objRFE.IsResetEvent):
            pass

        #Request RF Explorer configuration
        objRFE.SendCommand_RequestConfigData()

        #Wait to receive configuration and model details
        while(objRFE.ActiveModel == RFExplorer.RFE_Common.eModel.MODEL_NONE):
            objRFE.ProcessReceivedString(True)    #Process the received configuration

        #If object is an analyzer, we can scan for received sweeps
        if(objRFE.IsAnalyzer()):
            cls()
            print("---- RFE High-Resolution Scan to CSV for WWB ----")
            START_SCAN_MHZ = objRFE.MinFreqMHZ
            STOP_SCAN_MHZ = objRFE.MaxFreqMHZ
            SPAN_SIZE_MHZ = 13.875 # 111 points per window * 0.125 MHz resolution = 13.875 span size

            print("Enter band to scan (leave blank for full range): ")
            userBand = input()
            if(userBand!=""):
                START_SCAN_MHZ, STOP_SCAN_MHZ = bandLookup.bandLookup(userBand)

            #Control settings
            SpanSize, StartFreq, StopFreq = ControlSettings(objRFE)

            nScans = math.ceil((STOP_SCAN_MHZ - START_SCAN_MHZ)/SPAN_SIZE_MHZ)

            if(SpanSize and StartFreq and StopFreq):
                nInd = 0
                while (True): 
                    #Set new configuration into device
                    objRFE.UpdateDeviceConfig(StartFreq, StopFreq)

                    objSweep=None
                    #Wait for new configuration to arrive (as it will clean up old sweep data)
                    while(True):
                        objRFE.ProcessReceivedString(True)
                        if (objRFE.SweepData.Count>0):
                            objSweep=objRFE.SweepData.GetData(objRFE.SweepData.Count-1)

                            nInd += 1
                            PrintScan(objRFE, nInd)
                        if(math.fabs(objRFE.StartFrequencyMHZ - StartFreq) <= 0.001):
                                break
  
                    #set new frequency range
                    StartFreq = StopFreq
                    StopFreq = StartFreq + SpanSize
                    if (StopFreq > STOP_SCAN_MHZ):
                        StopFreq = STOP_SCAN_MHZ

                    if (StartFreq >= StopFreq):
                        break
            else:
                print("Error: settings are wrong.\nPlease, change and try again")
    else:
        print("Not Connected")
except Exception as obEx:
    print("Error: " + str(obEx))

#---------------------------------------------------------
# Close object and release resources
#---------------------------------------------------------

objRFE.Close()    #Finish the thread and close port
objRFE = None 
