from enum import Enum

# Image Sensor Types for Use with SPOT_IMAGESENSORTYPE
#define SPOT_IMAGESENSORTYPE_CCDINTERLINE        0x0011 // Conventional interline CCD
#define SPOT_IMAGESENSORTYPE_CCDFULLFRAME        0x0021 // Conventional full-frame CCD
#define SPOT_IMAGESENSORTYPE_CCDFRAMETRANSFER    0x0031 // Conventional frame-transfer CCD
#define SPOT_IMAGESENSORTYPE_CCDINTERLINEEM      0x0111 // Electron-Multiplication interline CCD
#define SPOT_IMAGESENSORTYPE_CCDFRAMETRANSFEREM  0x0131 // Electron-Multiplication frame-transfer CCD
#define SPOT_IMAGESENSORTYPE_CMOSROLLINGSHUTTER  0x0042 // CMOS rolling shutter
#define SPOT_IMAGESENSORTYPE_CMOSGLOBALSHUTTER   0x0012 // CMOS global shutter

class SensorType(Enum):
    CCDInterline = 0x011
    CCDFullFrame = 0x0021
    CCDFrameTransfer = 0x0031
    CCDInterlineEM = 0x011
    CCDFrameTransferEM = 0x0131
    CMOSRollingShutter = 0x0042
    CMOSGlobalShutter = 0x0012


#// Color Values Used with SpotGetLiveImages
#define SPOT_COLORRED                    1
#define SPOT_COLORGREEN                  2
#define SPOT_COLORBLUE                   3
#define SPOT_COLORCLEAR                 10
#define SPOT_COLORRGB                    0
#define SPOT_COLORRG                    21   // Red-Green
#define SPOT_COLORRB                    22   // Red-Blue
#define SPOT_COLORGB                    23   // Green-Blue
#define SPOT_COLORNONE                  99

class Color(Enum):
    Red = 1
    Green = 2
    Blue = 3
    Clear = 10
    RGB = 0
    RG = 21
    RB = 22
    GB = 23
    none = 99

#// Rotate Values Used with SpotGetLiveImages
#define SPOT_ROTATENONE         0
#define SPOT_ROTATELEFT         1
#define SPOT_ROTATERIGHT        2

class Rotate(Enum):
    none = 0
    Left = 1
    Right = 2

#// Color Enhancement Rendering Intent Values for Use with SPOT_COLORRENDERINGINTENT
#define SPOT_COLORRENDERINGINTENT_RELATIVECOLORIMETRIC  1
#define SPOT_COLORRENDERINGINTENT_ABSOLUTECOLORIMETRIC  2
#define SPOT_COLORRENDERINGINTENT_PERCEPTUAL            3
#define SPOT_COLORRENDERINGINTENT_SATURATION            4

class ColorRengering(Enum):
    RelativeColorMetric = 1
    AbsoluteColorMetric = 2
    Perceptual = 3
    Saturation = 4

#// Image Types for Use with SPOT_IMAGETYPE
#define SPOT_IMAGEBRIGHTFLD              1
#define SPOT_IMAGEDARKFLD                2

class ImageFld(Enum):
    Bright = 1
    Dark = 2


#// External Trigger Types for Use with SPOT_EXTERNALTRIGGERMODE
#define SPOT_TRIGMODENONE      0   // No trigger
#define SPOT_TRIGMODEEDGE      1   // Edge Trigger
#define SPOT_TRIGMODEBULB      2   // Bulb Trigger

class TriggerMode(Enum):
    none = 0
    Edge = 1
    Bulb = 2

#// Bus Bandwidth Levels for Use with SPOT_BUSBANDWIDTH
#define SPOT_HIGHBW            1
#define SPOT_MEDIUMBW          2
#define SPOT_LOWBW             3

class BandWidth(Enum):
    High = 1
    Medium= 2
    Low = 3

#// External Trigger Active States for Use with SPOT_EXTERNALTRIGGERACTIVESTATE
#define SPOT_TRIGACTIVESTATE_LOW    0
#define SPOT_TRIGACTIVESTATE_HIGH   1

class TrigActiveState(Enum):
    Low = 0
    High = 1

#// TTL Output Active States for Use with SPOT_TTLOUTPUTACTIVESTATE
#define SPOT_TTLACTIVESTATE_LOW     0
#define SPOT_TTLACTIVESTATE_HIGH    1

class TTLActiveState(Enum):
    Low = 0
    High = 1

#// Values for Use with SpotGetSequentialImages
IntervalShortAsPossible = -1
InfiniteImages = 0x7fffffff



#// Mosaic Pattern Types for Use with SPOT_MOSAICPATTERN
#define SPOT_MOSAICBAYERGRBG   1   // Bayer pattern - Even lines: GRG.. Odd lines: BGB...  (zero-based)
#define SPOT_MOSAICBAYERRGGB   2   // Bayer pattern - Even lines: RGR.. Odd lines: GBG...
#define SPOT_MOSAICBAYERBGGR   3   // Bayer pattern - Even lines: BGB.. Odd lines: RGR...
#define SPOT_MOSAICBAYERGBRG   4   // Bayer pattern - Even lines: GBG.. Odd lines: RGR...

class MosaicBayer(Enum):
    GRBG = 1
    RGGB = 2
    BGGR = 3
    GBRG = 4


#// 24 BPP Image Formats for Use with SPOT_24BPPIMAGEBUFFERFORMAT
#define SPOT_24BPPIMAGEBUFFERFORMATBGR   1   // Blue, Green, Red (3 bytes per pixel with padding) (standard Window BITMAP)
#define SPOT_24BPPIMAGEBUFFERFORMATRGB   2   // Red, Green, Blue (3 bytes per pixel with padding)
#define SPOT_24BPPIMAGEBUFFERFORMATARGB  3   // Alpha, Red, Green, Blue (4 bytes per pixel)
#define SPOT_24BPPIMAGEBUFFERFORMATABGR  4   // Alpha, Blue, Green, Red (4 bytes per pixel)
#define SPOT_24BPPIMAGEBUFFERFORMATRGBA  5   // Red, Green, Blue, Alpha (4 bytes per pixel)
#define SPOT_24BPPIMAGEBUFFERFORMATBGRA  6   // Blue, Green, Red, Alpha (4 bytes per pixel)

class BufferFormat(Enum):
    BGR = 1
    RGB = 2
    ARGB = 3
    ABGR = 4
    RGBA = 5
    BGRA = 6

#// Gain Port Attribute Flags for Use with SPOT_PORTnGAINATTRIBUTES
#define SPOT_GAINATTR_COMPUTABLE    0x01  // The actual gain can be computed with SpotGetActualGainValue() or SpotGetActualLiveGainValue()
#define SPOT_GAINATTR_SAMEASPORT0   0x02  // This gain port is the same as port 0, except that a range is provided (instead of a discrete value list)
#define SPOT_GAINATTR_ELECTRONMULT  0x04  // Electron multiplication gain
#define SPOT_GAINATTR_GATING        0x08  // Gating gain

class GainAttr(Enum):
    Computable = 0x01
    SameAsPort0 = 0x02
    ElectronMult = 0x04
    Gating = 0x08

#// Shutter Modes for Use with SPOT_SHUTTERMODE
#define SPOT_SHUTTERMODE_NORMAL        0
#define SPOT_SHUTTERMODE_OPEN          1
#define SPOT_SHUTTERMODE_CLOSED        2

class Shutter(Enum):
    Normal = 0
    Open = 1
    Closed = 2

#// Sensor Clear Modes for Use with SPOT_SENSORCLEARMODE and SPOT_SENSORCLEARMODES
#define SPOT_SENSORCLEARMODE_CONTINUOUS    0x01   // Continuously clear sensor
#define SPOT_SENSORCLEARMODE_PREEMPTABLE   0x02   // Allow exposures to pre-emp sensor clearing
#define SPOT_SENSORCLEARMODE_NEVER         0x04   // Never clear sensor

class ClearMode(Enum):
    Continuous = 0x01
    Preemptable = 0x02
    Never = 0x04


#// Sensor Response Modes for use with SPOT_SENSORRESPONSEMODE
#define SPOT_SENSORRESPMODE_IR               0x01  // Enhanced IR response
#define SPOT_SENSORRESPMODE_DYNAMICRANGE     0x02  // Enhanced dynamic range
#define SPOT_SENSORRESPMODE_SENSITIVITY      0x04  // Enhanced sensitivity
#define SPOT_SENSORRESPMODE_ANTIBLOOMING     0x08  // Enhanced anti-blooming
#define SPOT_SENSORRESPMODE_GLOWSUPPRESSION  0x10  // Suppression of sensor glow

class SensorRespMode(Enum):
    IR = 0x01
    DynamicRange = 0x02
    Sensitivity = 0x04
    AntiBlooming= 0x08
    GlowSupression = 0x10


#// Control Flags for Use with SpotUpdateFirmware
#define SPOT_UPDATEFWCONTROL_FORCEUPDATECAMERA      1  // Load camera firmware even if older than current
#define SPOT_UPDATEFWCONTROL_FORCEUPDATEINTFCARD    2  // Load interface card firmware even if older than current


#// Result Flags for Use with SpotUpdateFirmware
#define SPOT_UPDATEFWRESULT_POWEROFFDEV        1  // Power off the device before using
#define SPOT_UPDATEFWRESULT_POWEROFFCOMPUTER   2  // Power off the computer before using the camera
#define SPOT_UPDATEFWRESULT_REBOOTCOMPUTER     4  // Reboot the computer before using the camera


#// Message Types for Use in SPOT_MESSAGE_STRUCT
#define SPOT_MESSAGETYPE_INFO               1
#define SPOT_MESSAGETYPE_WARNING            2
#define SPOT_MESSAGETYPE_ERROR              3

class MessageType(Enum):
    Info = 1
    Warning = 2
    Error = 2


#// Interface Types for use with SpotFindDevices()
#define SPOT_INTFTYPE_PCI           2    // PCI card
#define SPOT_INTFTYPE_1394          3    // 1394 (FireWire) camera
#define SPOT_INTFTYPE_USB           4    // USB camera

class IntfType(Enum):
    PCI = 2
    IEEE_1394 = 3
    USB = 4

#// Device Types for use with SpotFindDevices()
#define SPOT_DEVTYPE_RTCARD          3   // SPOT RT card
#define SPOT_DEVTYPE_RTINSIGHTCARD   SPOT_DEVTYPE_RTCARD
#define SPOT_DEVTYPE_INSIGHTCARD     4   // SPOT Insight card
#define SPOT_DEVTYPE_RTSE18CARD      6   // SPOT RT-SE18 card
#define SPOT_DEVTYPE_RT2CARD         7   // SPOT RT2 card
#define SPOT_DEVTYPE_BOOSTCARD       8   // SPOT Boost card
#define SPOT_DEVTYPE_1394CAMERA      32  // SPOT 1394 camera
#define SPOT_DEVTYPE_USBCAMERA       41  // SPOT USB camera

class DevType(Enum):
    RTCard = 3
    InsightCard = 4
    RTSE18Card = 6
    RT2Card = 7
    BoostCard = 8
    IEEE1394Camera = 32
    USBCamera = 41


#// Status Values
#define SPOT_STATUSIDLE                  0   // Doing nothing (operation completed)
#define SPOT_STATUSDRVNOTINIT            1   // Driver not initialized
#define SPOT_STATUSEXPOSINGRED           2   // Exposing in Red -
#define SPOT_STATUSEXPOSINGGREEN         3   // Exposing in Green -
#define SPOT_STATUSEXPOSINGBLUE          4   // Exposing in Blue -
#define SPOT_STATUSIMAGEREADRED          5   // Downloading Red image -
#define SPOT_STATUSIMAGEREADGREEN        6   // Downloading Green image -
#define SPOT_STATUSIMAGEREADBLUE         7   // Downloading Blue image -
#define SPOT_STATUSCOMPEXP               8   // Computing exposure
#define SPOT_STATUSCOMPWHITEBAL          9   // Computing white balance
#define SPOT_STATUSGETIMAGE              10  // Getting an image
#define SPOT_STATUSLIVEIMAGEREADY        11  // Live image is available in buffer
#define SPOT_STATUSEXPOSINGCLEAR         12  // Exposing in Clear -
#define SPOT_STATUSEXPOSING              13  // Exposing (filter off or no filter) -
#define SPOT_STATUSIMAGEREADCLEAR        14  // Downloading monchrome image (clear filter)
#define SPOT_STATUSIMAGEREAD             15  // Downloading monchrome image (no filter)
#define SPOT_STATUSSEQIMAGEWAITING       16  // Waiting to acquire the next sequential image
#define SPOT_STATUSSEQIMAGEREADY         17  // A sequential image is available for
#define SPOT_STATUSIMAGEPROCESSING       18  // Processing an acquired image
#define SPOT_STATUSWAITINGFORTRIGGER     19  // Waiting for a trigger
#define SPOT_STATUSWAITINGFORBLOCKLIGHT  20  // The user should block all light to the camera
#define SPOT_STATUSWAITINGFORMOVETOBKGD  21  // The user should move the specimen out of the path
#define SPOT_STATUSTTLOUTPUTDELAY        22  // Waiting for the specified TTL output delay to elapse
#define SPOT_STATUSEXTERNALTRIGGERDELAY  23  // Waiting for the specified extrenal trigger delay to elapse
#define SPOT_STATUSWAITINGFORCOLORFILTER 24  // Waiting for the color filter to change
#define SPOT_STATUSGETLIVEIMAGES         25  // Starting live image acquisition mode
#define SPOT_STATUSFANDELAY              26  // Waiting for specified delay after changing fan speed 
#define SPOT_STATUSFIRMWAREUPDATING      27  // Updating firmware for a device
#define SPOT_STATUSRUNNING               500 // The process is running (only applicable when SPOT_WAITFORSTATUSCHANGES is TRUE)
#define SPOT_STATUSABORTED               100 // Last operation was aborted
#define SPOT_STATUSERROR                 101 // Last operation ended in an error -


class Status(Enum):
    Idle = 0
    DrvNotInit = 1
    ExposingRed = 2
    ExposingGreen = 3
    ExposingBlue = 4
    ImageReadRed = 5
    ImageReadGreen = 6
    ImageReadBlue = 7
    CompExp = 8
    CompWhitBal = 9
    GetImage = 10
    LiveImageReady = 11
    ExposingClear = 12
    Exposing = 13
    ImageReadClear = 14
    ImageRead = 15
    SeqImageWaitting = 16
    SeqImageReady = 17
    ImageProcessing = 18
    WaitingForTrigger = 19
    WaittingForBlockLight = 20
    WaitingForMoveToBkGd = 21
    TTLOutputDelay = 22
    ExternalTriggerDelay = 23
    WaittingForColorFilter = 24
    GetLiveImages = 25
    FanDelay = 26
    FirmwareUpdating = 27
    Runnig = 500
    Aborted = 100
    Error = 101


