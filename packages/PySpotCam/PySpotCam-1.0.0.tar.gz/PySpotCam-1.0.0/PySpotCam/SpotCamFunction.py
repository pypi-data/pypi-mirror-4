import ctypes
from ctypes import *

import SpotCamEnum
import SpotCamCStructure

try:
    _SpotCam=windll.LoadLibrary("SpotCam.dll")
except:
    class _nothing():
        def __getattr__(self, name):
            return lambda *args:0
    _SpotCam = _nothing()

SPOT_ERROR = {
100:('SPOT_ABORT',              "Operation was aborted by the application"),
101:('SPOT_ERROUTOFMEMORY',     "Memory allocation failure"),
102:('SPOT_ERREXPTOOSHORT',     "Exposure time is too short"),
103:('SPOT_ERREXPTOOLONG',      "Exposure time is too long"),
104:('SPOT_ERRNOCAMERARESP',    "Camera is not responding to command"),
105:('SPOT_ERRVALOUTOFRANGE',   "Specified value is out of valid range"),
106:('SPOT_ERRINVALIDPARAM',    "Specified parameter number is not valid"),
107:('SPOT_ERRDRVNOTINIT',      "SpotInit has not yet been successfully called"),
109:('SPOT_ERRREGISTRYQUERY',   "Error getting value from Windows Registry"),
110:('SPOT_ERRREGISTRYSET',     "Error setting value in Windows Registry"),
111:('SPOT_ERRVXDOPEN',         "Error opening Win95 VxD loader"),
112:('SPOT_ERRWINRTLOAD',       "Error loading WinRT driver"),
112:('SPOT_ERRDEVDRVLOAD',     "Error loading device driver"),
113:('SPOT_ERRWINRTUNLOAD',     "Error unloading WinRT driver"),
114:('SPOT_ERRCAMERAERROR',     "Camera is malfunctioning"),
115:('SPOT_ERRDRVALREADYINIT',  "SpotInit has already been called"),
116:('SPOT_ERRNOCAMERAINFOFILE',"A camera info file cannot be found"),
117:('SPOT_ERRDMASETUP',        "The DMA buffer could not be setup (RT only)"),
118:('SPOT_ERRREADCAMINFO',     "There was an error reading the camera information (RT only)"),
119:('SPOT_ERRNOTCAPABLE',      "The camera is not capable of performing the command"),
120:('SPOT_ERRCOLORFILTERNOTIN',"The color filter is not in the IN position"),
121:('SPOT_ERRCOLORFILTERNOTOUT',"The color filter is not in the OUT position"),
122:('SPOT_ERRCAMERABUSY',      "The camera is currently in another operation"),
123:('SPOT_ERRCAMERANOTSUPPORTED',"The camera model is not supported by this version"),
125:('SPOT_ERRNOIMAGEAVAILABLE',"There is no image available"),
126:('SPOT_ERRFILEOPEN',        "The specified file cannot be opened or created"),
127:('SPOT_ERRFLATFLDINCOMPATIBLE',"The specified flatfield is incompatible with the current camera/parameters"),
128:('SPOT_ERRNODEVICESFOUND',  "No SPOT interface cards or 1394 camera were found"),
#SPOT_ERRNOINTFCARDSFOUND = SPOT_ERRNODEVICESFOUND
129:('SPOT_ERRBRIGHTNESSCHANGED',"The brightness changed while exposure was being computed"),
130:('SPOT_ERRCAMANDCARDINCOMPATIBLE',"The camera is incompatible with the interface card"),
201:('SPOT_ERRINSUF1394ISOCBANDWIDTH',"The is insufficient isochronous bandwidth available on the 1394 bus"),
202:('SPOT_ERRINSUF1394ISOCRESOURCES',"There are insufficient 1394 isochronous resources available"),
203:('SPOT_ERRNO1394ISOCCHANNEL',"There is no isochronous channel available on the 1394 bus")
}


class SpotCamError(Exception):
    """Exception raised from the SpotCam driver.

    Attributes:
        error -- Error number
        fname -- Name of the function which raised the error
    """
    def __init__(self, error, fname):
        self.error = error
        self.fname = fname
    def __str__(self):
        if SPOT_ERROR.has_key(self.error):
            return "%s error in function %s (error %i). %s"%(SPOT_ERROR[self.error][0], self.fname, self.error, SPOT_ERROR[self.error][1])
        else:  
            return "Error %i in function %s"%(self.error, self.fname)

def catch_error(f):
    def mafunction(*arg):
        error = f(*arg)
        if error<>0:
            raise SpotCamError(error=error, fname=f.__name__)
        return error
    mafunction.__name__ = f.__name__
    return mafunction

_SetValue = catch_error(_SpotCam.SpotSetValue)
_GetValue = catch_error(_SpotCam.SpotGetValue)
#_GetValueSize = catch_error(_SpotCam.SpotGetValueSize)
_GetValueSize = _SpotCam.SpotGetValueSize
_GetCameraAttributes = catch_error(_SpotCam.SpotGetCameraAttributes)
#_GetVersionInfo = catch_error(_SpotCam.SpotGetVersionInfo)
_GetVersionInfo = _SpotCam.SpotGetVersionInfo
#_GetVersionInfo2 = catch_error(_SpotCam.SpotGetVersionInfo2)
_GetVersionInfo2 = _SpotCam.SpotGetVersionInfo2
_ComputeExposure = catch_error(_SpotCam.SpotComputeExposure)
_ComputeExposure2 = catch_error(_SpotCam.SpotComputeExposure2)
_ComputeExposureConversionFactor = catch_error(_SpotCam.SpotComputeExposureConversionFactor)
_ComputeExposureConversionFactorX1000 = catch_error(_SpotCam.SpotComputeExposureConversionFactorX1000)
_ComputeWhiteBalance = catch_error(_SpotCam.SpotComputeWhiteBalance)
_ComputeWhiteBalanceX1000 = catch_error(_SpotCam.SpotComputeWhiteBalanceX1000)
_GetFlatfield = catch_error(_SpotCam.SpotGetFlatfield)
_GetFlatfield2 = catch_error(_SpotCam.SpotGetFlatfield2)
_GetBiasFrame = catch_error(_SpotCam.SpotGetBiasFrame)
_GetBackgroundImage = catch_error(_SpotCam.SpotGetBackgroundImage)
_GetSensorCurrentTemperature = catch_error(_SpotCam.SpotGetSensorCurrentTemperature)
_GetSensorExposureTemperature = catch_error(_SpotCam.SpotGetSensorExposureTemperature)
_GetExposureTimestamp = catch_error(_SpotCam.SpotGetExposureTimestamp)
_GetImage = catch_error(_SpotCam.SpotGetImage)
_GetSequentialImages = catch_error(_SpotCam.SpotGetSequentialImages)
_RetrieveSequentialImage = catch_error(_SpotCam.SpotRetrieveSequentialImage)
_GetLiveImages = catch_error(_SpotCam.SpotGetLiveImages)
#_SetAbortFlag = catch_error(_SpotCam.SpotSetAbortFlag)
_SetAbortFlag = _SpotCam.SpotSetAbortFlag
#_SetCallback = catch_error(_SpotCam.SpotSetCallback)
_SetCallback = _SpotCam.SpotSetCallback
#_SetDeviceNotificationCallback = catch_error(_SpotCam.SpotSetDeviceNotificationCallback)
_SetDeviceNotificationCallback = _SpotCam.SpotSetDeviceNotificationCallback
#_SetBusyCallback = catch_error(_SpotCam.SpotSetBusyCallback)

#_SetBusyCallback = _SpotCam.SpotSetBusyCallback

_QueryStatus = catch_error(_SpotCam.SpotQueryStatus)
_ClearStatus = catch_error(_SpotCam.SpotClearStatus)
_QueryColorFilterPosition = catch_error(_SpotCam.SpotQueryColorFilterPosition)
_QueryCameraPresent = catch_error(_SpotCam.SpotQueryCameraPresent)
_SetTTLOutputState = catch_error(_SpotCam.SpotSetTTLOutputState)
_Init = catch_error(_SpotCam.SpotInit)
_Exit = catch_error(_SpotCam.SpotExit)
_DumpCameraMemory = catch_error(_SpotCam.SpotDumpCameraMemory)
_FindDevices = catch_error(_SpotCam.SpotFindDevices)
_GetActualGainValue = catch_error(_SpotCam.SpotGetActualGainValue)
_GetActualGainValueX10000 = catch_error(_SpotCam.SpotGetActualGainValueX10000)
_GetActualLiveGainValue = catch_error(_SpotCam.SpotGetActualLiveGainValue)
_GetActualLiveGainValueX10000 = catch_error(_SpotCam.SpotGetActualLiveGainValueX10000)
_GetBiasFrameCompatibilityInformation = catch_error(_SpotCam.SpotGetBiasFrameCompatibilityInformation)
_GetFlatfieldCompatibilityInformation = catch_error(_SpotCam.SpotGetFlatfieldCompatibilityInformation)
_GetBackgroundImageCompatibilityInformation = catch_error(_SpotCam.SpotGetBackgroundImageCompatibilityInformation)
# _WaitForStatusChange = catch_error(_SpotCam.SpotWaitForStatusChange)
_WaitForStatusChange = _SpotCam.SpotWaitForStatusChange
# _GetCameraErrorCode = catch_error(_SpotCam.SpotGetCameraErrorCode)
_GetCameraErrorCode = _SpotCam.SpotGetCameraErrorCode
#_UpdateFirmware = catch_error(_SpotCam.SpotUpdateFirmware)


SetValue = _SetValue
GetValue = _GetValue
GetValueSize = _GetValueSize
GetCameraAttributes = _GetCameraAttributes
GetVersionInfo = _GetVersionInfo
GetVersionInfo2 = _GetVersionInfo2
ComputeExposure = _ComputeExposure
ComputeExposure2 = _ComputeExposure2
ComputeExposureConversionFactor = _ComputeExposureConversionFactor
ComputeExposureConversionFactorX1000 = _ComputeExposureConversionFactorX1000
ComputeWhiteBalance = _ComputeWhiteBalance
ComputeWhiteBalanceX1000 = _ComputeWhiteBalanceX1000
GetFlatfield = _GetFlatfield
GetFlatfield2 = _GetFlatfield2
GetBiasFrame = _GetBiasFrame
GetBackgroundImage = _GetBackgroundImage
GetSensorCurrentTemperature = _GetSensorCurrentTemperature
GetSensorExposureTemperature = _GetSensorExposureTemperature
GetExposureTimestamp = _GetExposureTimestamp
GetImage = _GetImage
GetSequentialImages = _GetSequentialImages
RetrieveSequentialImage = _RetrieveSequentialImage
GetLiveImages = _GetLiveImages
SetAbortFlag = _SetAbortFlag
SetCallback = _SetCallback
SetDeviceNotificationCallback = _SetDeviceNotificationCallback
#SetBusyCallback = _SetBusyCallback
QueryStatus = _QueryStatus
ClearStatus = _ClearStatus
QueryColorFilterPosition = _QueryColorFilterPosition
QueryCameraPresent = _QueryCameraPresent
SetTTLOutputState = _SetTTLOutputState
Init = _Init
Exit = _Exit
DumpCameraMemory = _DumpCameraMemory
FindDevices = _FindDevices
GetActualGainValue = _GetActualGainValue
GetActualGainValueX10000 = _GetActualGainValueX10000
GetActualLiveGainValue = _GetActualLiveGainValue
GetActualLiveGainValueX10000 = _GetActualLiveGainValueX10000
GetBiasFrameCompatibilityInformation = _GetBiasFrameCompatibilityInformation
GetFlatfieldCompatibilityInformation = _GetFlatfieldCompatibilityInformation
GetBackgroundImageCompatibilityInformation = _GetBackgroundImageCompatibilityInformation
WaitForStatusChange = _WaitForStatusChange
GetCameraErrorCode = _GetCameraErrorCode
#UpdateFirmware = _UpdateFirmware


def ClearStatus():
    """Reset the current status value to either SPOT_STATUSDRVNOTINIT or SPOT_STATUSIDLE,
    depending on whether or not the driver has been initialized"""
    _ClearStatus()

def ComputeExposure():
    """Compute appropriate exposure times and gain level for the image currently in the camera's
    view. If exposure resolution finer than 1ms is desired, ComputeExposure2 should be called instead.
    """
    exposure = SpotCamCStructure.EXPOSURE_STRUCT()
    _ComputeExposure(byref(exposure))
    return exposure

def ComputeExposure2():
    """Ccompute appropriate exposure times and gain level for the image currently in the camera's
    view. It provides finer exposure time resolution than ComputeExposure.
    """
    exposure = SpotCamCStructure.EXPOSURE_STRUCT2()
    _ComputeExposure(byref(exposure))
    return exposure

def ComputeExposureConversionFactor():
    """compute a factor which can be used for converting live mode exposure values
    for still image capture for cameras which have separate amplifier circuits for live and still image capture modes.
    """
    out = ctypes.c_float()
    _ComputeExposureConversionFactor(byref(out))
    return out.value


def ComputeExposureConversionFactorX1000():
    """Compute a factor which can be used for converting live mode exposure values
    for still image capture for cameras which have separate amplifier circuits for live 
    and still image capture modes. It is the same as SpotComputeExposureConversionFactor, 
    except that the returned value is an integer.
    """
    out = ctypes.c_long()
    _ComputeExposureConversionFactorX1000(byref(out))
    return out.value

def ComputeWhiteBalance():
    """compute white balance values for the image currently in the camera's view."""
    bal = SpotCamCStructure.WHITE_BAL_STRUCT()
    _ComputeWhiteBalance(byref(bal))
    return bal

def ComputeWhiteBalanceX1000():
    """same as the ComputeWhiteBalance function, except that it returns results as
    integers in a SPOT_WHITE_BAL_INT_STRUCT structure"""
    bal = SpotCamCStructure.WHITE_BAL_INT_STRUCT()
    _ComputeWhiteBalance(byref(bal))
    return bal

def DumpCameraMemory(filename):
    """Dump the contents of the camera's memory to a file for diagnostic purposes."""
    c_s = ctypes.c_char_p(filename)
    _DumpCameraMemory(c_s)

def Exit():
    try:
        _Exit()
    except SpotCamError, instance:
        pass

def FindDevices():
    """Obtain a list of available camera devices on the machine"""
    pstDevices = (SpotCamCStructure.SPOT_DEVICE_STRUCT*SpotCamConstant.SPOT_MAX_DEVICES)()
    pnNumDevices = (ctypes.c_int*SpotCamConstant.SPOT_MAX_DEVICES)()
    _FindDevices(pstDevices, pnNumDevices)
    return zip(pnNumDevices[:], pstDevices[:]) # Look 

def GetActualGainValue(GainPort, GainValue):
    """Get actual gain values for cameras which provide non-integer gains. An application should
    check the value of the PortnGainAtributes parameter for the GAINATTR_COMPUTABLE bit to verify that the actual
    gain can be computed before calling this function"""
    ActualGainValue = ctypes.c_float()
    _GetActualGainValue(ctypes.c_int(GainPort), ctypes.c_int(GainValue), byref(ActualGainValue))
    return ActualGainValue.value

def GetActualLiveGainValue(GainPort, GainValue):
    """Get actual live mode gain values for cameras which provide non-integer gains. An application should
    check the value of the PortnGainAtributes parameter for the GAINATTR_COMPUTABLE bit to verify that the actual
    gain can be computed before calling this function"""
    ActualGainValue = ctypes.c_float()
    _GetActualGainValue(ctypes.c_int(GainPort), ctypes.c_int(GainValue), byref(ActualGainValue))
    return ActualGainValue.value


def GetActualGainValueX1000(GainPort, GainValue):
    """Get actual gain values for cameras which provide non-integer gains. It is the same as
    SpotGetActualGainValue, except that the actual gain value is expressed as an integer. An application should check the value of the
    PortnGainAtributes parameter for the SPOT_GAINATTR_COMPUTABLE bit to verify that the actual gain can be computed
    before calling this function."""
    ActualGainValue = ctypes.c_int()
    _GetActualGainValue(ctypes.c_int(GainPort), ctypes.c_int(GainValue), byref(ActualGainValue))
    return ActualGainValue.value

def GetActualLiveGainValueX1000(GainPort, GainValue):
    """Get actual live mode gain values for cameras which provide non-integer gains. It is the same as
    SpotGetActualGainValue, except that the actual gain value is expressed as an integer. An application should check the value of the
    PortnGainAtributes parameter for the SPOT_GAINATTR_COMPUTABLE bit to verify that the actual gain can be computed
    before calling this function."""
    ActualGainValue = ctypes.c_int()
    _GetActualGainValue(ctypes.c_int(GainPort), ctypes.c_int(GainValue), byref(ActualGainValue))
    return ActualGainValue.value

def GetBackgroundImage(filename, NumFramesToAvg):
    """Acquire a background image for correcting acquired images."""
    c_s = ctypes.c_char_p(filename)
    _GetBackgroundImage(c_s, ctypes.c_int(NumFramesToAvg))

def GetBackgroundImageCompatibilityInformation(filename):
    """obtain information about a background image to allow an
    application to determine is it can be used to correct acquired images"""
    Info = SpotCamCStructure.BKGD_IMAGE_COMPATIBILITY_INFO_STRUCT()
    _GetBackgroundImageCompatibilityInformation(c_s, byref(info))
    return Info

def GetBiasFrame(filename, NumFramesToAvg):
    """Acquire a bias frame for correcting acquired images."""
    c_s = ctypes.c_char_p(filename)    
    _GetBiasFrame(c_s, ctypes.c_int(NumFramesToAvg))

def GetBiasFrameCompatibilityInformation(filename):
    """obtain information about a bias frame to allow an application to
    determine is it can be used to correct acquired images."""
    Info = SpotCamCStructure.BIAS_FRAME_COMPATIBILITY_INFO_STRUCT()
    _GetBiasFrameCompatibilityInformation(c_s, byref(info))
    return Info


# Flags for use with SpotGetCameraAttributes()
AttributesDictionnary = dict(
color                    = (0x00000001  ," camera can return color images"),
slider                   = (0x00000002  ," camera has a color filter slider"),
live_mode                 = (0x00000004  ," camera can run live mode"),
mosaic                   = (0x00000008  ," camera has a Bayer pattern color mosaic CCD chip"),
edge_trigger              = (0x00000010  ," camera has an edge-type external trigger"),
bulb_trigger              = (0x00000020  ," camera has a bulb-type external trigger"),
clear_filter              = (0x00000040  ," camera has a color filter with a clear state"),
ieee_1394                 = (0x00000080  ," camera is an IEEE-1394/FireWire device"),
color_filter              = (0x00000100  ," camera has a color filter (color images require multiple shots)"),
temperature_readout       = (0x00000200  ," camera can read the sensor temperature"),
temperature_regulation    = (0x00000400  ," camera can regulate the sensor temperature"),
trigger_activestate       = (0x00000800  ," camera can set trigger input active state"),
dual_amplifier            = (0x00001000  ," camera has separate amplifier circuits for live mode and capture"),
accurate_ttl_delay_timing   = (0x00002000  ," camera can accurately time TTL output and trigger delays (to microseconds)"),
slider_position_detection  = (0x00004000  ," camera can detect the color filter slider position"),
auto_exposure             = (0x00008000  ," camera can compute exposure"),
ttl_output                = (0x00010000  ," camera has a TTL output"),
sensor_shifting           = (0x00020000  ," camera can shift the position of the image sensor for higher resolution"),
filter_wheel              = (0x00040000  ," camera has a mechanical filter wheel"),
black_level_subtract       = (0x00080000  ," camera can do black-level subtraction"),
chip_defect_correction     = (0x00100000  ," camera can do chip defect correction"),
internal_shutter          = (0x00200000  ," camera has an internal mechanical shutter"),
exposure_shutter          = (0x00400000  ," camera's internal shutter can be used for exposure"),
ttl_output_during_exposure  = (0x00800000  ," camera can activate TTL output during exposure"),
single_chan_live_mode       = (0x01000000  ," camera can use a single readout channel in live mode"),
multi_chan_live_mode        = (0x02000000  ," camera can use mutiple parallel readout channels in live mode"),
firmware_update           = (0x04000000  ," camera's firmware can be updated through the SpotCam API"),
live_histogram            = (0x08000000  ," camera can provide histogram information and do stretching in live mode")
)

class SpotCamAttributes():
    attribute_liste = ['color','slider', 'live_mode', 'mosaic', 'edge_trigger',
                      'bulb_trigger', 'clear_filter', 'ieee_1394']
    def __init__(self, attribute_value):
        for key,val in AttributesDictionnary.iteritems():
            setattr(self, key, (attribute_value & val[0])<>0)
    def __repr__(self):
        s = "SpotCamAttributes :\n\t" 
        s += '\n\t'.join(['%s = %s'%(name, getattr(self, name)) for name in AttributesDictionnary.keys()])

        return s
    def __str__(self):
        s = "SpotCamAttributes :\n\t" 
        for key,val in AttributesDictionnary.iteritems():
            if getattr(self, key):
                s += val[1]+'\n'
        return s


def GetCameraAttributes():
    """Get the current camera's attributes"""
    attr = c_ulong()
    _GetCameraAttributes(byref(attr))
    return SpotCamAttributes(attr.value)




def GetCameraErrorCode():
    """ retrieve the error code from the camera after an error occurs. Currently, only certain
    camera models support this function. This error code may be useful in diagnosing camera malfunctions. """
    return _GetCameraErrorCode()


def GetExposureTimestamp():
    """Obtain the timestamp of the beginning of the last exposure for still image acquisition"""
    Timestamp = SpotCamCStructure.TIMESTAMP_STRUCT()
    _GetExposureTimestamp(byref(Timestamp))
    return Timestamp

def GetFlatfield(filename):
    """Acquire a flatfield which can be used to correct acquired images."""
    c_s = ctypes.c_char_p(filename)
    _GetFlatfield(c_s)

def GetFlatfield2(filename, NumFramesToAvg):
    """Acquire a flatfield for correcting acquired images. It is a replacement for SpotGetFlatfield,
    providing better results"""
    c_s = ctypes.c_char_p(filename)
    _GetFlatfield2(c_s, ctypes.c_int(NumFramesToAvg))


def GetFlatfieldCompatibilityInformation(filename):
    """obtain information about a flatfield to allow an application to determine if
    it can be used to correct acquired images."""
    c_s = ctypes.c_char_p(filename)    
    Info = SpotCamCStructure.FLATFIELD_COMPATIBILITY_INFO_STRUCT()
    _GetFlatfieldCompatibilityInformation(c_s, byref(Info))
    return Info

#GetImage
#GetLiveImages
    
def GetSensorCurrentTemperature(full_output=False):
    """Obtain the current temperature of the camera's image sensor
    If full_output return the value and a boll indicating if the 
    has been updated since the last time the function was
    called
    """
    Temperature = ctypes.c_short()
    IsNewValue = ctypes.c_bool()
    _GetSensorCurrentTemperature(byref(Temperature), byref(IsNewValue))
    if full_output:
        return Temperature.value, IsNewValue.value
    else:
        return Temperature.value

def GetSensorExposureTemperature():
    """Obtain the temperature of the camera's image sensor at the time that the last
    exposure began"""
    Temperature = ctypes.c_short()   
    _GetSensorExposureTemperature(byref(Temperature))
    return Temperature.value

#GetSequentialImages

GetValue.__doc__="""retrieve the values of the various parameters and camera values"""

def GetValueSize(Param):
    """Determine the size of the buffer which needs to be passed to SpotGetValue"""
    return _GetValueSize(ctypes.c_short(Param))


def GetVersionInfo():
    """Query the camera driver for version and camera information. It has been superseded by
    GetVersionInfo2 which provides more detailed camera information"""
    VerInfo = SpotCamCStructure.SPOT_VERSION_STRUCT()
    _GetVersionInfo(byref(VerInfo))
    return VerInfo

def GetVersionInfo2():
    """Query the camera driver for version and camera information. """
    VerInfo = SpotCamCStructure.SPOT_VERSION_STRUCT2()
    _GetVersionInfo2(byref(VerInfo))
    return VerInfo

def Init():
    try:
        _Init()
    except SpotCamError, instance:
        if instance.error <> 115:
            raise instance


def QueryCameraPresent():
    """Determine whether or not a camera is currently connected and powered"""
    CameraPresent = ctypes.c_bool()
    _QueryCameraPresent(byref(CameraPresent))
    return CameraPresent.value


def QueryColorFilterPosition():
    """determine the current color filter position for slider cameras which support this
    capability. Returns a tuple for the Color and B/W position"""
    FilterIn = ctypes.c_bool()
    FilterOut = ctypes.c_bool()
    _QueryColorFilterPosition(byref(FilterIn), byref(FilterOut))
    return FilterIn.value, FilterOut.value


def QueryStatus(abort=False):
    """Query the driver for current status information and to abort camera operation."""
    d = c_long(0)
    _QueryStatus(abort, byref(d))
    return SpotCamEnum.Status(d.value)

#RetrieveSequentialImage
RetrieveSequentialImage.__doc__ = """Retrieve an image acquired by a call to GetSequentialImages"""

def SetAbortFlag(Abort_pointer):
    """Set a pointer to an abort flag. The abort flag is periodically checked by the
    camera driver during camera operation, and if it is found to be TRUE, the current process is aborted."""
    _SetAbortFlag(Abort_pointer)


def SetBusyCallback(func, UserData):
    """set a pointer to a callback function which the SpotCam driver will call
    periodically during long camera operations, giving the application 
    opportunities to process system events and abort the operation"""
    _SetBusyCallback(SpotCamCStructure.SPOTBUSYCALLBACK(func), SpotCamCStructure.DWORD(UserData))

spot_call_back = []

def SetCallback(func, UserData):
    """set a pointer to a callback function which the SpotCam driver will call periodically
    during camera operation to signal status change"""
    spot_call_back.append(SpotCamCStructure.SPOTCALLBACK(func))
    _SetCallback(spot_call_back[-1], SpotCamCStructure.DWORD(UserData))

def SetDeviceNotificationCallback(func, UserData):
    """set a pointer to a callback function which the driver will call
    when cameras are added to or removed from computer or powered on or off."""
    _SetDeviceNotificationCallback(SpotCamCStructure.SPOTDEVNOTIFYCALLBACK(func), SpotCamCStructure.DWORD(UserData))

def SetTTLOutputState(SetActive):
    """Set the state of the TTL output signal."""
    _SetTTLOutputState(ctypes.c_bool(SetActive))

# SetValue

def UpdateFirmware(filename, ControlFlags):
    """update the firmware for all cameras and interface cards which provide this capability and for
    which firmware is available"""
    c_s = ctypes.c_char_p(filename) 
    ResultFlags = SpotCamCStructure.DWORD()
    _UpdateFirmware(c_s, SpotCamCStructure.DWORD(ControlFlags), byref(ResultFlags))

def WaitForStatusChange(TimeoutMSec = -1):
    """Wait for a status notification from the SpotCam driver when operating in polling mode."""
    Status = ctypes.c_int()
    Info = ctypes.c_long()
    out = _WaitForStatusChange(byref(Status), byref(Info), ctypes.c_int(TimeoutMSec))
    if out:
        return Status.value, Info.value
    else:
        return None






