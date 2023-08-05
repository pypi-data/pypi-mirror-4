import numpy as np
import ctypes
import SpotCamConstant
import SpotCamEnum
import SpotCamTuple
import SpotCamCStructure
from SpotValueClassDefinition import *

class ImageBufferFormat24Bpp(GetSpotValue, EnumSpotValue):
    """The format used for storing 24 bpp images in memory. """
    #Data type : short (one of the SPOT_24BPPIMAGEBUFFERFORMATxxx values).
    _nParam = SpotCamConstant.IMAGEBUFFERFORMAT
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.BufferFormat

class AcquiredImageSize(GetSpotValue, NamedTupleSpotValue):
    """The width and height, in pixels, of images acquired by SpotGetImage or 
    SpotGetSequentialImages. """
    #Data type : two short values, first value is width, second is height
    _nParam = SpotCamConstant.ACQUIREDIMAGESIZE
    _ctype = ctypes.c_short*2
    _tuple_class = SpotCamTuple.Size

class AcquiredLiveImageSize(GetSpotValue, NamedTupleSpotValue):
    """The width and height, in pixels, of images acquired by 
    SpotGetLiveImages """
    #Data type : two short values, first value is width, second is height
    _nParam = SpotCamConstant.ACQUIREDLIVEIMAGESIZE
    _ctype = ctypes.c_short*2
    _tuple_class = SpotCamTuple.Size

class AutoExpose(GetSetSpotValue, CTypeValue):
    """The auto-exposure setting. Specifies whether exposure computation is 
    performed automatically when SpotGetImage, SpotGetSequentialImages, 
    SpotGetFlatfield, SpotGetFlatfield2, or SpotGetBackgroundImage are 
    called. """
    #Data type : BOOL
    _nParam = SpotCamConstant.AUTOEXPOSE
    _ctype = ctypes.c_bool

class AutoGainLimit(GetSetSpotValue, CTypeValue):
    """The maximum gain level to be allowed for computed exposures for 
    non-live mode images. """
    #Data type : short
    _nParam = SpotCamConstant.AUTOGAINLIMIT
    _ctype = ctypes.c_short

class BiasFrmSubtract(GetSetSpotValue, CTypeValue):
    """The name of the file to be used for bias frame subtraction or NULL if 
    bias frame subtraction is disabled. """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.BIASFRMSUBTRACT
    _ctype = ctypes.c_char

class BinSize(GetSetSpotValue, CTypeValue):
    """The binning size to be used for all modes of image acquisition. """
    #Data type : short
    _nParam = SpotCamConstant.BINSIZE
    _ctype = ctypes.c_short

class BinSizeLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable bin size values (superseded by 
    SPOT_BINSIZES). """
    #Data type : two short values, first value is minimum, second is maximum
    _nParam = SpotCamConstant.BINSIZELIMITS
    _ctype = ctypes.c_short*2
    _tuple_class = SpotCamTuple.Limit

class BinSizes(GetSpotValue, ArraySpotValue):
    """The allowable bin size values. """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.BINSIZES
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class BitDepth(GetSetSpotValue, CTypeValue):
    """The bit depth to be used for still image capture and exposure 
    computation. """
    #Data type : short
    _nParam = SpotCamConstant.BITDEPTH
    _ctype = ctypes.c_short

class BitDepths(GetSpotValue, ArraySpotValue):
    """The allowable bit depth values for still image capture. """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.BITDEPTHS
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class BkGdImageSubtract(GetSetSpotValue, CTypeValue):
    """The name of the file to be used for background image subtraction or 
    NULL if background image subtraction is disabled. """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.BKGDIMAGESUBTRACT
    _ctype = ctypes.c_char

class BrightnessAdj(GetSetSpotValue, CTypeValue):
    """The adjustment factor to be applied to computed exposures to adjust 
    brightness. """
    #Data type : float
    _nParam = SpotCamConstant.BRIGHTNESSADJ
    _ctype = ctypes.c_float

class BrightnessAdjLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable brightness adjustment values. """
    #Data type : two float values, first value is minimum, second is maximum
    _nParam = SpotCamConstant.BRIGHTNESSADJLIMITS
    _ctype = ctypes.c_float*2
    _tuple_class = SpotCamTuple.Limit

class BrightnessAdjLimitsX1000(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable brightness adjustment values 
    multiplied by 1000. """
    #Data type : two long values, first value is minimum, second is maximum (multiplied by 1000)
    _nParam = SpotCamConstant.BRIGHTNESSADJLIMITSX1000
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class BrightnessAdjX1000(GetSetSpotValue, CTypeValue):
    """The adjustment factor to be applied to computed exposures to adjust 
    brightness multiplied by 1000. """
    #Data type : long
    _nParam = SpotCamConstant.BRIGHTNESSADJX1000
    _ctype = ctypes.c_long

class BusBandWidth(GetSetSpotValue, EnumSpotValue):
    """The desired maximum 1394 bus bandwidth level. """
    #Data type : short (SPOT_HIGHBW, SPOT_MEDIUMBW, or SPOT_LOWBW)
    _nParam = SpotCamConstant.BUSBANDWIDTH
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.BandWidth

class ClearMode(GetSetSpotValue, CTypeValue):
    """The mode to be used for clearing the image sensor. """
    #Data type : DWORD
    _nParam = SpotCamConstant.CLEARMODE
    _ctype = ctypes.c_ulong

class ClearModes(GetSpotValue, CTypeValue):
    """The clear modes which supported by the camera. """
    #Data type : DWORD
    _nParam = SpotCamConstant.CLEARMODES
    _ctype = ctypes.c_ulong

class ColorBinSize(GetSetSpotValue, CTypeValue):
    """The color binning size to be used for all modes of image acquisition. """
    #Data type : short
    _nParam = SpotCamConstant.COLORBINSIZE
    _ctype = ctypes.c_short

class ColorBinSizes(GetSpotValue, ArraySpotValue):
    """The allowable color binning size values. """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.COLORBINSIZES
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class ColorEnable(GetSetSpotValue, StructureSpotValue):
    """The filter colors which are enabled for image acquisition and exposure 
    computation. """
    #Data type : SPOT_COLOR_ENABLE_STRUCT structure
    _nParam = SpotCamConstant.COLORENABLE
    _ctype = SpotCamCStructure.COLOR_ENABLE_STRUCT

class ColorEnable2(GetSetSpotValue, StructureSpotValue):
    """The filter colors which are enabled for image acquisition and exposure 
    computation. """
    #Data type : SPOT_COLOR_ENABLE_STRUCT2 structure
    _nParam = SpotCamConstant.COLORENABLE2
    _ctype = SpotCamCStructure.COLOR_ENABLE_STRUCT2

class ColorOrder(GetSetSpotValue, CTypeValue):
    """The order in which the colors channels are to be acquired for 
    multi-shot images. """
    #Data type : char (NULL-terminated string (eg. "RBG", "RG", etc.))
    _nParam = SpotCamConstant.COLORORDER
    _ctype = ctypes.c_char

class ColorRenderingIntent(GetSetSpotValue, EnumSpotValue):
    """The rendering intent to be used for color enhancements """
    #Data type : short (one of the defined SPOT_COLORRENDERINGINTENT_xxx values)
    _nParam = SpotCamConstant.COLORRENDERINGINTENT
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.ColorRengering

class CoolerModeOnExit(GetSetSpotValue, CTypeValue):
    """The mode for the cooler after SpotExit is called. """
    #Data type : short (0:turn off, 1:leave on)
    _nParam = SpotCamConstant.COOLERMODEONEXIT
    _ctype = ctypes.c_short

class CoolingLevel(GetSetSpotValue, CTypeValue):
    """The level of cooling of the camera's image sensor """
    #Data type : short
    _nParam = SpotCamConstant.COOLINGLEVEL
    _ctype = ctypes.c_short

class CoolingLevels(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum supported levels of cooling of the camera's 
    image sensor. """
    #Data type : two short values, first value is minimum, second is maximum
    _nParam = SpotCamConstant.COOLINGLEVELS
    _ctype = ctypes.c_short*2
    _tuple_class = SpotCamTuple.Limit

class CorrectChipDefects(GetSetSpotValue, CTypeValue):
    """Enables or disables chip defect correction for still captured images. """
    #Data type : BOOL
    _nParam = SpotCamConstant.CORRECTCHIPDEFECTS
    _ctype = ctypes.c_bool

class DeviceUID(GetSetSpotValue, StructureSpotValue):
    """The unique ID of the current camera device. """
    #Data type : SPOT_DEVICE_UID union
    _nParam = SpotCamConstant.DEVICEUID
    _ctype = SpotCamCStructure.DEVICE_UID

class DriverDeviceNumber(GetSetSpotValue, CTypeValue):
    """The zero-based index of the current camera device in the list of found 
    devices. """
    #Data type : short
    _nParam = SpotCamConstant.DRIVERDEVICENUMBER
    _ctype = ctypes.c_short

class EnablePowerStateControl(GetSetSpotValue, CTypeValue):
    """Enables or disables the control of system power state changes """
    #Data type : BOOL
    _nParam = SpotCamConstant.ENABLEPOWERSTATECONTROL
    _ctype = ctypes.c_bool

class EnableTTLOutput(GetSetSpotValue, CTypeValue):
    """Enables or disables the TTL output. """
    #Data type : BOOL
    _nParam = SpotCamConstant.ENABLETTLOUTPUT
    _ctype = ctypes.c_bool

class EnhanceColors(GetSetSpotValue, CTypeValue):
    """Enables or disables automatic color enhancement for still captured 
    images. """
    #Data type : BOOL
    _nParam = SpotCamConstant.ENHANCECOLORS
    _ctype = ctypes.c_bool

class Exposure(GetSetSpotValue, StructureSpotValue):
    """The exposure times and gain to be used for acquisition of still 
    captured images. """
    #Data type : SPOT_EXPOSURE_STRUCT structure
    _nParam = SpotCamConstant.EXPOSURE
    _ctype = SpotCamCStructure.EXPOSURE_STRUCT

class Exposure2(GetSetSpotValue, StructureSpotValue):
    """The exposure times and gain to be used for acquisition of still 
    captured images. """
    #Data type : SPOT_EXPOSURE_STRUCT2 structure
    _nParam = SpotCamConstant.EXPOSURE2
    _ctype = SpotCamCStructure.EXPOSURE_STRUCT2

class ExposureCompRect(GetSetSpotValue, StructureSpotValue):
    """The area of sensor chip to be used for exposure computation (NULL for 
    full chip). """
    #Data type : RECT struct
    _nParam = SpotCamConstant.EXPOSURECOMPRECT
    _ctype = SpotCamCStructure.RECT

class ExposureConvFactor(GetSpotValue, CTypeValue):
    """The factor to use to convert live mode exposures to still image 
    acquisition exposures. """
    #Data type : float
    _nParam = SpotCamConstant.EXPOSURECONVFACTOR
    _ctype = ctypes.c_float

class ExposureConvFactorX1000(GetSpotValue, CTypeValue):
    """The factor to use to convert live mode exposures to still image 
    acquisition exposures multiplied by 1000. """
    #Data type : long
    _nParam = SpotCamConstant.EXPOSURECONVFACTORX1000
    _ctype = ctypes.c_long

class ExposureIncrement(GetSetSpotValue, CTypeValue):
    """The exposure increment, in nanoseconds, of exposure values (except 
    where they are explicitly expressed in msec). """
    #Data type : long
    _nParam = SpotCamConstant.EXPOSUREINCREMENT
    _ctype = ctypes.c_long

class ExposureLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable exposure durations in msec. """
    #Data type : two long values, first value is minimum, second is maximum
    _nParam = SpotCamConstant.EXPOSURELIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class ExposureLimits2(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable exposure durations. """
    #Data type : two DWORD values, first value is minimum, second is maximum (in increments defined by SPOT_EXPOSUREINCREMENT)
    _nParam = SpotCamConstant.EXPOSURELIMITS2
    _ctype = ctypes.c_ulong*2
    _tuple_class = SpotCamTuple.Limit

class ExposureResolution(GetSpotValue, CTypeValue):
    """The smallest exposure duration increment supported by the camera in 
    nsec. """
    #Data type : long
    _nParam = SpotCamConstant.EXPOSURERESOLUTION
    _ctype = ctypes.c_long

class ExternalTriggerActiveState(GetSetSpotValue, EnumSpotValue):
    """The level (high or low) of the external trigger input required to 
    trigger acquisition. """
    #Data type : short (SPOT_TRIGACTIVESTATE_LOW or SPOT_TRIGACTIVESTATE_HIGH)
    _nParam = SpotCamConstant.EXTERNALTRIGGERACTIVESTATE
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.TrigActiveState

class ExternalTriggerDelay(GetSetSpotValue, CTypeValue):
    """The delay between the trigger signal and the beginning of exposure in 
    usec. """
    #Data type : long
    _nParam = SpotCamConstant.EXTERNALTRIGGERDELAY
    _ctype = ctypes.c_long

class ExternalTriggerDelayLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable external trigger delay values in 
    usec. """
    #Data type : two long values, first value is minimum, second is maximum (in usec)
    _nParam = SpotCamConstant.EXTERNALTRIGGERDELAYLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class ExternalTriggerMode(GetSetSpotValue, EnumSpotValue):
    """The external trigger mode. """
    #Data type : short (SPOT_TRIGMODENONE, SPOT_TRIGMODEEDGE, or
    _nParam = SpotCamConstant.EXTERNALTRIGGERMODE
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.TriggerMode

class FanExposureDelayMs(GetSetSpotValue, CTypeValue):
    """The delay to wait before exposing after changing the fan speed, in ms. """
    #Data type : short
    _nParam = SpotCamConstant.FANEXPOSUREDELAYMS
    _ctype = ctypes.c_short

class FanExposureSpeed(GetSetSpotValue, CTypeValue):
    """The speed to which the fan is set for exposure. """
    #Data type : short
    _nParam = SpotCamConstant.FANEXPOSURESPEED
    _ctype = ctypes.c_short

class FanSpeed(GetSetSpotValue, CTypeValue):
    """The speed setting for the camera's cooling fan. """
    #Data type : short
    _nParam = SpotCamConstant.FANSPEED
    _ctype = ctypes.c_short

class FanSpeeds(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum speed settings supported for the camera's 
    cooling fan. """
    #Data type : two short values, first value is minimum, second is maximum
    _nParam = SpotCamConstant.FANSPEEDS
    _ctype = ctypes.c_short*2
    _tuple_class = SpotCamTuple.Limit

class FlatFLDCorrect(GetSetSpotValue, CTypeValue):
    """The name of the file to be used for flatfield correction or NULL if 
    flatfield correction is disabled. """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.FLATFLDCORRECT
    _ctype = ctypes.c_char

class ForceSingleChanLiveMode(GetSetSpotValue, CTypeValue):
    """Forces live mode to use a single amplifier circuit. """
    #Data type : BOOL
    _nParam = SpotCamConstant.FORCESINGLECHANLIVEMODE
    _ctype = ctypes.c_bool

class GainPortNumber(GetSetSpotValue, CTypeValue):
    """The currently selected gain port. """
    #Data type : short
    _nParam = SpotCamConstant.GAINPORTNUMBER
    _ctype = ctypes.c_short

class GainVals16(GetSpotValue, ArraySpotValue):
    """The allowable gain values for 10-16 bit per channel still image 
    capture. """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.GAINVALS16
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class GainVals8(GetSpotValue, ArraySpotValue):
    """The allowable gain values for 8 bit per channel still image capture. """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.GAINVALS8
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class HorizReadoutFrequencies(GetSpotValue, CTypeValue):
    """The allowable still image capture sensor horizontal readout 
    frequencies in kHz. """
    #Data type : array of long values, first value is count of values following
    _nParam = SpotCamConstant.HORIZREADOUTFREQUENCIES
    _ctype = ctypes.c_long

class HorizReadoutFrequency(GetSetSpotValue, CTypeValue):
    """The frequency at which each line of the sensor is read for still 
    captured images, in kHz. """
    #Data type : long
    _nParam = SpotCamConstant.HORIZREADOUTFREQUENCY
    _ctype = ctypes.c_long

class ImageRect(GetSetSpotValue, StructureSpotValue):
    """The area of the sensor chip to be used for image acquisition. """
    #Data type : RECT structure
    _nParam = SpotCamConstant.IMAGERECT
    _ctype = SpotCamCStructure.RECT

class ImageSensorModelDescr(GetSpotValue, CTypeValue):
    """The text description of the model of image sensor chip in the camera. """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.IMAGESENSORMODELDESCR
    _ctype = ctypes.c_char

class ImageSensorType(GetSpotValue, EnumSpotValue):
    """The type of image sensor chip in the camera. """
    #Data type : DWORD (one of the SPOT_IMAGESENSORTYPE_xxx values)
    _nParam = SpotCamConstant.IMAGESENSORTYPE
    _ctype = ctypes.c_ulong
    _enum_class = SpotCamEnum.SensorType

class ImageType(GetSetSpotValue, EnumSpotValue):
    """The image type (bright or dark field) used for exposure computation. """
    #Data type : short (SPOT_IMAGEBRIGHTFLD or SPOT_IMAGEDARKFLD)
    _nParam = SpotCamConstant.IMAGETYPE
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.ImageFld

class InputColorProfile(GetSetSpotValue, CTypeValue):
    """The name of the file containing the input ICC profile information for 
    color enhancements. """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.INPUTCOLORPROFILE
    _ctype = ctypes.c_char

class LiveAccelerationLevel(GetSetSpotValue, CTypeValue):
    """The acceleration level for live image mode. """
    #Data type : short
    _nParam = SpotCamConstant.LIVEACCELERATIONLEVEL
    _ctype = ctypes.c_short

class LiveAutoBrightness(GetSetSpotValue, CTypeValue):
    """Enables or disables auto brightness adjustments in live mode. """
    #Data type : BOOL
    _nParam = SpotCamConstant.LIVEAUTOBRIGHTNESS
    _ctype = ctypes.c_bool

class LiveAutoBrightnessAdj(GetSpotValue, CTypeValue):
    """The current live mode auto-brightness adjustment factor. """
    #Data type : float
    _nParam = SpotCamConstant.LIVEAUTOBRIGHTNESSADJ
    _ctype = ctypes.c_float

class LiveAutoBrightnessAdjX1000(GetSpotValue, CTypeValue):
    """The current live mode auto-brightness adjustment factor multiplied by 
    1000. """
    #Data type : long
    _nParam = SpotCamConstant.LIVEAUTOBRIGHTNESSADJX1000
    _ctype = ctypes.c_long

class LiveAutoGainLimit(GetSetSpotValue, CTypeValue):
    """The maximum gain level to be allowed for computed exposures for live 
    mode exposure computation. """
    #Data type : short
    _nParam = SpotCamConstant.LIVEAUTOGAINLIMIT
    _ctype = ctypes.c_short

class LiveBrightNessAdj(GetSetSpotValue, CTypeValue):
    """The brightness adjustment used for live image acquisition. """
    #Data type : float
    _nParam = SpotCamConstant.LIVEBRIGHTNESSADJ
    _ctype = ctypes.c_float

class LiveBrightNessAdjX1000(GetSetSpotValue, CTypeValue):
    """The brightness adjustment used for live image acquisition multiplied 
    by 1000 """
    #Data type : long
    _nParam = SpotCamConstant.LIVEBRIGHTNESSADJX1000
    _ctype = ctypes.c_long

class LiveEnhanceColors(GetSetSpotValue, CTypeValue):
    """Enables or disables automatic color enhancement for live mode images. """
    #Data type : BOOL
    _nParam = SpotCamConstant.LIVEENHANCECOLORS
    _ctype = ctypes.c_bool

class LiveExposure(GetSetSpotValue, StructureSpotValue):
    """The exposure durations and gain used for live image acquisition. """
    #Data type : SPOT_EXPOSURE_STRUCT2 structure
    _nParam = SpotCamConstant.LIVEEXPOSURE
    _ctype = SpotCamCStructure.EXPOSURE_STRUCT2

class LiveGainVals(GetSpotValue, ArraySpotValue):
    """The allowable gain values for live image acquisition. """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.LIVEGAINVALS
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class LiveGammaAdj(GetSetSpotValue, CTypeValue):
    """The gamma adjustment applied to live images. """
    #Data type : float
    _nParam = SpotCamConstant.LIVEGAMMAADJ
    _ctype = ctypes.c_float

class LiveGammaAdjX1000(GetSetSpotValue, CTypeValue):
    """The gamma adjustment applied to live images multiplied by 1000. """
    #Data type : long
    _nParam = SpotCamConstant.LIVEGAMMAADJX1000
    _ctype = ctypes.c_long

#class LiveHistogram(GetSetSpotValue, StructureSpotValue):
#    """The buffers for holding live image histogram data. """
#    #Data type : SPOT_LIVE_HISTOGRAM_STRUCT structure
#    _nParam = SpotCamConstant.LIVEHISTOGRAM
#    _ctype = SpotCamCStructure.LIVE_HISTOGRAM_STRUCT

class LiveImageScaling(GetSetSpotValue, StructureSpotValue):
    """Specifies live mode image scaling. """
    #Data type : SPOT_LIVE_IMAGE_SCALING_STRUCT structure
    _nParam = SpotCamConstant.LIVEIMAGESCALING
    _ctype = SpotCamCStructure.LIVE_IMAGE_SCALING_STRUCT

class LiveMaxExposureMsec(GetSetSpotValue, CTypeValue):
    """The maximum allowable exposure for live image acquisition in msec. """
    #Data type : long
    _nParam = SpotCamConstant.LIVEMAXEXPOSUREMSEC
    _ctype = ctypes.c_long

class LivePixelResolutionLevel(GetSetSpotValue, CTypeValue):
    """The pixel resolution level used for live image acquisition. """
    #Data type : short
    _nParam = SpotCamConstant.LIVEPIXELRESOLUTIONLEVEL
    _ctype = ctypes.c_short

class LiveSubtractBlackLevel(GetSetSpotValue, CTypeValue):
    """Enables or disables automatic black level subtraction for live 
    monochrome images. """
    #Data type : BOOL
    _nParam = SpotCamConstant.LIVESUBTRACTBLACKLEVEL
    _ctype = ctypes.c_bool

class MaxExposureMsec(GetSetSpotValue, CTypeValue):
    """The maximum allowable exposure still image capture in msec. """
    #Data type : long
    _nParam = SpotCamConstant.MAXEXPOSUREMSEC
    _ctype = ctypes.c_long

class MaxGainPortNumber(GetSpotValue, CTypeValue):
    """The maximum gain port number. """
    #Data type : short
    _nParam = SpotCamConstant.MAXGAINPORTNUMBER
    _ctype = ctypes.c_short

class MaxImageRectSize(GetSpotValue, ArraySpotValue):
    """The maximum allowable image area width and height, which is the size 
    of the camera's image sensor chip. """
    #Data type : array of short values, first value is maximum width, second is maximum height
    _nParam = SpotCamConstant.MAXIMAGERECTSIZE
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class MaxLiveAccelerationLevel(GetSpotValue, CTypeValue):
    """The maximum allowable live image acceleration level. """
    #Data type : short
    _nParam = SpotCamConstant.MAXLIVEACCELERATIONLEVEL
    _ctype = ctypes.c_short

class MaxNumberSeqImageExpDurs(GetSpotValue, CTypeValue):
    """The maximum number of sequential acquisition exposure durations 
    supported. """
    #Data type : short
    _nParam = SpotCamConstant.MAXNUMBERSEQIMAGEEXPDURS
    _ctype = ctypes.c_short

class MaxNumberSkipLines(GetSpotValue, CTypeValue):
    """The maximum allowable number of image lines to skip during readout. """
    #Data type : short
    _nParam = SpotCamConstant.MAXNUMBERSKIPLINES
    _ctype = ctypes.c_short

class MaxPixelResolutionLevel(GetSpotValue, CTypeValue):
    """The maximum allowable pixel resolution level. """
    #Data type : short
    _nParam = SpotCamConstant.MAXPIXELRESOLUTIONLEVEL
    _ctype = ctypes.c_short

class MaxVertClockVoltageBoost(GetSpotValue, CTypeValue):
    """The maximum allowable vertical clock voltage boost level. """
    #Data type : short
    _nParam = SpotCamConstant.MAXVERTCLOCKVOLTAGEBOOST
    _ctype = ctypes.c_short

class MaxWhiteBalanceRatio(GetSpotValue, CTypeValue):
    """The maximum allowable white balance ratio. """
    #Data type : float
    _nParam = SpotCamConstant.MAXWHITEBALANCERATIO
    _ctype = ctypes.c_float

class MaxWhiteBalanceRatioX1000(GetSpotValue, CTypeValue):
    """The maximum allowable white balance ratio multiplied by 1000. """
    #Data type : long
    _nParam = SpotCamConstant.MAXWHITEBALANCERATIOX1000
    _ctype = ctypes.c_long

class MessageEnable(GetSetSpotValue, CTypeValue):
    """Enables or disables processing of OS messages during camera operation. """
    #Data type : BOOL
    _nParam = SpotCamConstant.MESSAGEENABLE
    _ctype = ctypes.c_bool

class MinExposureMsec(GetSetSpotValue, CTypeValue):
    """The minimum exposure, in msec, to be allowed for computed exposures. """
    #Data type : short
    _nParam = SpotCamConstant.MINEXPOSUREMSEC
    _ctype = ctypes.c_short

class MinImageRectSize(GetSpotValue, ArraySpotValue):
    """The minimum allowable image area width and height """
    #Data type : array of short values, first value is minimum width, second is minimum height
    _nParam = SpotCamConstant.MINIMAGERECTSIZE
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class MinFastSeqImageExpDur(GetSpotValue, CTypeValue):
    """The minimum possible exposure for fast sequential image acquisition 
    (SPOT_INTERVALSHORTASPOSSIBLE). """
    #Data type : QWORD
    _nParam = SpotCamConstant.MINFASTSEQIMAGEEXPDUR
    _ctype = ctypes.c_int64

class MinPixelResolutionLevel(GetSpotValue, CTypeValue):
    """The minimum allowable pixel resolution level. """
    #Data type : short
    _nParam = SpotCamConstant.MINPIXELRESOLUTIONLEVEL
    _ctype = ctypes.c_short

class MonitorFilterPos(GetSetSpotValue, CTypeValue):
    """Enables or disables the monitoring of the color filter position for 
    slider cameras. """
    #Data type : BOOL
    _nParam = SpotCamConstant.MONITORFILTERPOS
    _ctype = ctypes.c_bool

class MosaicPattern(GetSpotValue, EnumSpotValue):
    """The description of the mosaic color pattern on the camera's sensor 
    chip. """
    #Data type : short (one of the SPOT_MOSAICxxx values)
    _nParam = SpotCamConstant.MOSAICPATTERN
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.MosaicBayer

class NoiseFilterThresPct(GetSetSpotValue, CTypeValue):
    """The threshold percentage to be used for noise filtering or 0 to 
    disable noise filtering. """
    #Data type : short
    _nParam = SpotCamConstant.NOISEFILTERTHRESPCT
    _ctype = ctypes.c_short

class NumberBytesPerImageRow(GetSetSpotValue, CTypeValue):
    """The number of bytes in the image data buffer per image row. """
    #Data type : long
    _nParam = SpotCamConstant.NUMBERBYTESPERIMAGEROW
    _ctype = ctypes.c_long

class NumberReadoutCircuits(GetSpotValue, CTypeValue):
    """The number of image readout circuits available in the camera. """
    #Data type : short
    _nParam = SpotCamConstant.NUMBERREADOUTCIRCUITS
    _ctype = ctypes.c_short

class NumberSkipLines(GetSetSpotValue, CTypeValue):
    """The number of image lines to skip during readout. """
    #Data type : short
    _nParam = SpotCamConstant.NUMBERSKIPLINES
    _ctype = ctypes.c_short

class OutputColorProfile(GetSetSpotValue, CTypeValue):
    """The name of the file containing the output ICC profile information for 
    color enhancements. """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.OUTPUTCOLORPROFILE
    _ctype = ctypes.c_char

class PixelResolutionImgSizeFactors(GetSpotValue, CTypeValue):
    """The approximate image size adjustment factors for each pixel 
    resolution level. """
    #Data type : array of floats, one for each pixel resolution level from minimum to maximum
    _nParam = SpotCamConstant.PIXELRESOLUTIONIMGSIZEFACTORS
    _ctype = ctypes.c_float

class PixelResolutionLevel(GetSetSpotValue, CTypeValue):
    """The pixel resolution level used for still image acquisition. """
    #Data type : short
    _nParam = SpotCamConstant.PIXELRESOLUTIONLEVEL
    _ctype = ctypes.c_short

class PixelSize(GetSpotValue, NamedTupleSpotValue):
    """The x and y sizes of the sensor pixels, in nm. """
    #Data type : array of two longs, first value is x size, second is y size
    _nParam = SpotCamConstant.PIXELSIZE
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.PSize

class Port0GainAttributes(GetSpotValue, EnumSpotValue):
    """The attributes of gain port 0 """
    #Data type : DWORD (SPOT_GAINATTR_xxx bit-fields)
    _nParam = SpotCamConstant.PORT0GAINATTRIBUTES
    _ctype = ctypes.c_ulong
    _enum_class = SpotCamEnum.GainAttr

class Port0GainVals16(GetSpotValue, ArraySpotValue):
    """The allowable port 0 gain values for 10-16 bit per channel still image 
    capture. (same as SPOT_GAINVALS16) """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.PORT0GAINVALS16
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class Port0GainVals8(GetSpotValue, ArraySpotValue):
    """The allowable port 0 gain values for 8 bit per channel still image 
    capture. (same as SPOT_GAINVALS8) """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.PORT0GAINVALS8
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class Port0LiveGainVals(GetSpotValue, ArraySpotValue):
    """The allowable port 0 gain values for live image acquisition. (same as 
    SPOT_LIVEGAINVALS) """
    #Data type : array of short values, first value is count of values following
    _nParam = SpotCamConstant.PORT0LIVEGAINVALS
    _ctype = ctypes.c_short*257
    _dtype = np.int16

class Port1GainAttributes(GetSpotValue, EnumSpotValue):
    """The attributes of gain port 1 """
    #Data type : DWORD (SPOT_GAINATTR_xxx bit-fields)
    _nParam = SpotCamConstant.PORT1GAINATTRIBUTES
    _ctype = ctypes.c_ulong
    _enum_class = SpotCamEnum.GainAttr

class Port1GainValLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable port 1 gain values for still image 
    capture. """
    #Data type : two long values, first value is minimum port 1 gain, second is maximum
    _nParam = SpotCamConstant.PORT1GAINVALLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class Port1LiveGainValLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable port 1 live mode gain values. """
    #Data type : two long values, first value is minimum port 1 live mode gain, second is maximum
    _nParam = SpotCamConstant.PORT1LIVEGAINVALLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class Port2GainAttributes(GetSpotValue, EnumSpotValue):
    """The attributes of gain port 2 """
    #Data type : DWORD (SPOT_GAINATTR_xxx bit-fields)
    _nParam = SpotCamConstant.PORT2GAINATTRIBUTES
    _ctype = ctypes.c_ulong
    _enum_class = SpotCamEnum.GainAttr

class Port2GainValLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable port 2 gain values for still image 
    capture. """
    #Data type : two long values, first value is minimum port 2 gain, second is maximum
    _nParam = SpotCamConstant.PORT2GAINVALLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class Port2LiveGainValLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable port 2 live mode gain values. """
    #Data type : two long values, first value is minimum port 2 live mode gain, second is maximum
    _nParam = SpotCamConstant.PORT2LIVEGAINVALLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class Port3GainAttributes(GetSpotValue, EnumSpotValue):
    """The attributes of gain port 3 """
    #Data type : DWORD (SPOT_GAINATTR_xxx bit-fields)
    _nParam = SpotCamConstant.PORT3GAINATTRIBUTES
    _ctype = ctypes.c_ulong
    _enum_class = SpotCamEnum.GainAttr

class Port3GainValLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable port 3 gain values for still image 
    capture. """
    #Data type : two long values, first value is minimum port 3 gain, second is maximum
    _nParam = SpotCamConstant.PORT3GAINVALLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class Port3LiveGainValLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable port 3 live mode gain values. """
    #Data type : two long values, first value is minimum port 3 live mode gain, second is maximum
    _nParam = SpotCamConstant.PORT3LIVEGAINVALLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class PreampGainVals(GetSpotValue, CTypeValue):
    """The allowable pre-amplifier gain values. """
    #Data type : array of float values, first value is count of values following
    _nParam = SpotCamConstant.PREAMPGAINVALS
    _ctype = ctypes.c_float

class PreampGainVal(GetSetSpotValue, CTypeValue):
    """The pre-amplifier gain value. """
    #Data type : float
    _nParam = SpotCamConstant.PREAMPGAINVAL
    _ctype = ctypes.c_float

class ReadoutCircuit(GetSetSpotValue, CTypeValue):
    """The index of the image data readout circuit to be used during image 
    acquisitions. """
    #Data type : short
    _nParam = SpotCamConstant.READOUTCIRCUIT
    _ctype = ctypes.c_short

class ReadoutCircuitDescr(GetSpotValue, CTypeValue):
    """The text description of the currently selected image readout circuit. """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.READOUTCIRCUITDESCR
    _ctype = ctypes.c_char

class RegulatedTemperature(GetSpotValue, CTypeValue):
    """The temperature to which the image sensor is regulated, in tenths of a 
    degree C. """
    #Data type : short
    _nParam = SpotCamConstant.REGULATEDTEMPERATURE
    _ctype = ctypes.c_short

class RegulatedTemperatureLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable regulated temperature values, in 
    tenths of a degree C. """
    #Data type : two short values, first value is minimum, second is maximum
    _nParam = SpotCamConstant.REGULATEDTEMPERATURELIMITS
    _ctype = ctypes.c_short*2
    _tuple_class = SpotCamTuple.Limit

class RegulateTemperature(GetSetSpotValue, CTypeValue):
    """Enables or disables temperature regulation for the image sensor. """
    #Data type : BOOL
    _nParam = SpotCamConstant.REGULATETEMPERATURE
    _ctype = ctypes.c_bool

class ReturnRawMosaicData(GetSetSpotValue, CTypeValue):
    """Enables or disables the return of raw image data from mosaic cameras. """
    #Data type : BOOL
    _nParam = SpotCamConstant.RETURNRAWMOSAICDATA
    _ctype = ctypes.c_bool

class SensorResponseMode(GetSetSpotValue, EnumSpotValue):
    """The sensor response mode. """
    #Data type : DWORD (SPOT_SENSORRESPONSEMODE_xxx bit-fields)
    _nParam = SpotCamConstant.SENSORRESPONSEMODE
    _ctype = ctypes.c_ulong
    _enum_class = SpotCamEnum.SensorRespMode

class SensorResponseModes(GetSpotValue, CTypeValue):
    """The sensor response modes which supported by the camera. """
    #Data type : array of DWORDs, first value is count of values following
    _nParam = SpotCamConstant.SENSORRESPONSEMODES
    _ctype = ctypes.c_ulong

class SeqImageDiskCachePath(GetSetSpotValue, CTypeValue):
    """The path to which cache files should be written during sequential 
    acquisition """
    #Data type : char (NULL-terminated string)
    _nParam = SpotCamConstant.SEQIMAGEDISKCACHEPATH
    _ctype = ctypes.c_char

class SeqImageExpDurs(GetSetSpotValue, CTypeValue):
    """The exposure durations to be used for sequential acquisition """
    #Data type : array of DWORD values, first value is the count
    _nParam = SpotCamConstant.SEQIMAGEEXPDURS
    _ctype = ctypes.c_ulong

class ShutterMode(GetSetSpotValue, EnumSpotValue):
    """The mode of operation of the camera's internal shutter. """
    #Data type : short (SPOT_SHUTTERMODE_NORMAL, SPOT_SHUTTERMODE_OPEN, or
    _nParam = SpotCamConstant.SHUTTERMODE
    _ctype = ctypes.c_short
    _enum_class = SpotCamEnum.Shutter

class SubtractBlackLevel(GetSetSpotValue, CTypeValue):
    """Enables or disables automatic black level subtraction for acquisition 
    of 10+ bpp monochrome images. """
    #Data type : BOOL
    _nParam = SpotCamConstant.SUBTRACTBLACKLEVEL
    _ctype = ctypes.c_bool

class TTLOutputActiveState(GetSetSpotValue, CTypeValue):
    """The level (high or low) of the TTL output signal when active. """
    #Data type : short
    _nParam = SpotCamConstant.TTLOUTPUTACTIVESTATE
    _ctype = ctypes.c_short

class TTLOutputDelay(GetSetSpotValue, CTypeValue):
    """The delay between the activation of the TTL output signal and the 
    beginning of exposure, in usec. A negative value indicates activation 
    during exposure. """
    #Data type : long
    _nParam = SpotCamConstant.TTLOUTPUTDELAY
    _ctype = ctypes.c_long

class TTLOutputDelayLimits(GetSpotValue, NamedTupleSpotValue):
    """The minimum and maximum allowable TTL output delay values, in usec. """
    #Data type : two long values, first value is minimum, second is maximum
    _nParam = SpotCamConstant.TTLOUTPUTDELAYLIMITS
    _ctype = ctypes.c_long*2
    _tuple_class = SpotCamTuple.Limit

class TTLOutputDelayMs(GetSetSpotValue, CTypeValue):
    """The wait time, in msec after raising the TTL output before exposing. """
    #Data type : short
    _nParam = SpotCamConstant.TTLOUTPUTDELAYMS
    _ctype = ctypes.c_short

class VertClockVoltageBoost(GetSetSpotValue, CTypeValue):
    """The vertical clock voltage boost level. """
    #Data type : short
    _nParam = SpotCamConstant.VERTCLOCKVOLTAGEBOOST
    _ctype = ctypes.c_short

class VertShiftPeriod(GetSetSpotValue, CTypeValue):
    """The vertical shift period, in ns. """
    #Data type : long
    _nParam = SpotCamConstant.VERTSHIFTPERIOD
    _ctype = ctypes.c_long

class VertShiftPeriods(GetSpotValue, CTypeValue):
    """The allowable vertical shift periods, in ns. """
    #Data type : array of long values, first value is count of values following
    _nParam = SpotCamConstant.VERTSHIFTPERIODS
    _ctype = ctypes.c_long

class WaitForStatusChanges(GetSetSpotValue, CTypeValue):
    """Enables use of SpotWaitForStatusChange for status notifications """
    #Data type : BOOL
    _nParam = SpotCamConstant.WAITFORSTATUSCHANGES
    _ctype = ctypes.c_bool

class WhiteBalance(GetSetSpotValue, StructureSpotValue):
    """The red, green, and blue white balance ratios. """
    #Data type : SPOT_WHITE_BAL_STRUCT structure
    _nParam = SpotCamConstant.WHITEBALANCE
    _ctype = SpotCamCStructure.WHITE_BAL_STRUCT

class WhiteBalanceX1000(GetSetSpotValue, StructureSpotValue):
    """The red, green, and blue white balance ratios multiplied by 1000. """
    #Data type : SPOT_WHITE_BAL_INT_STRUCT structure
    _nParam = SpotCamConstant.WHITEBALANCEX1000
    _ctype = SpotCamCStructure.WHITE_BAL_INT_STRUCT

class WhiteBalCompRect(GetSetSpotValue, StructureSpotValue):
    """The area of the sensor chip to be used for white balance computation 
    (NULL for full chip). """
    #Data type : RECT structure
    _nParam = SpotCamConstant.WHITEBALCOMPRECT
    _ctype = SpotCamCStructure.RECT

class ImageOrientation(GetSetSpotValue, CTypeValue):
    """No documentation """
    #Data type : short
    _nParam = SpotCamConstant.IMAGEORIENTATION
    _ctype = ctypes.c_short
