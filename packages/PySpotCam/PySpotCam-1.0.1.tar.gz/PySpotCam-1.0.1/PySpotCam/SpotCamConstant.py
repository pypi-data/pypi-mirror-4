MAX_INTF_CARDS = 25
MAX_DEVICES = 25
MAX_SAMPLE_FRAMES = 50

# Spot Function Return Codes
SUCCESS = 0
# Warning Codes have Negative Values
WARNUNSUPPCAMFEATURES = -100 # The camera has features which are not supported by ths software version
WARNINVALIDINPUTICC = -101 # The input color profile for the camera cannot be found or is invalid
WARNINVALIDOUTPUTICC = -102 # The output color profile for the camera cannot be found or is invalid
# Error Codes have Positive Values below 1000
ABORT = 100 # Operation was aborted by the app
ERROUTOFMEMORY = 101 # Memory allocation failure
ERREXPTOOSHORT = 102 # Exposure times is too short
ERREXPTOOLONG = 103 # Exposure times is too long
ERRNOCAMERARESP = 104 # Camera is not responding to command
ERRVALOUTOFRANGE = 105 # Specified value is out of valid range
ERRINVALIDPARAM = 106 # Specified parameter number is not valid
ERRDRVNOTINIT = 107 # SpotInit has not yet been successfully called
ERRREGISTRYQUERY = 109 # Error getting value from Windows Registry
ERRREGISTRYSET = 110 # Error setting value in Windows Registry
ERRDEVDRVLOAD = 112 # Error loading device driver
ERRCAMERAERROR = 114 # Camera is malfunctioning
ERRDRVALREADYINIT = 115 # SpotInit has already been called
ERRDMASETUP = 117 # The DMA buffer could not be setup
ERRREADCAMINFO = 118 # There was an eror reading the camera information
ERRNOTCAPABLE = 119 # The camera or driver is not capable of performing the command
ERRCOLORFILTERNOTIN = 120 # The color filter is not in the IN position
ERRCOLORFILTERNOTOUT = 121 # The color filter is not in the OUT position
ERRCAMERABUSY = 122 # The camera is currently in another operation
ERRCAMERANOTSUPPORTED = 123 # The camera model is not supported by this version
PROCESSERROR = 124 # Process Manager can't get info for us.
ERRMISC = 135 # misc Mac error
ERRNOIMAGEAVAILABLE = 125 # There is no image available
ERRFILEOPEN = 126 # The specified file cannot be opened or created
ERRFLATFLDINCOMPATIBLE = 127 # The specified flatfield is incompatible with
ERRNODEVICESFOUND = 128 # No SPOT interface cards or cameras were found
ERRBRIGHTNESSCHANGED = 129 # The brightness changed while exposure was being computed
ERRCAMANDCARDINCOMPATIBLE = 130 # The camera is incompatible with the interface card
ERRBIASFRMINCOMPATIBLE = 131 # The specified bias frame is incompatible with
ERRBKGDIMAGEINCOMPATIBLE = 132 # The specified background image is incompatible with
ERRBKGDTOOBRIGHT = 133 # The background is too bright to acquire a background image
ERRINVALIDFILE = 134 # The specified file is invalid
ERRIMAGETOOBRIGHT = 136 # The image is too bright
ERRNOTHINGTODO = 137 # There is nothing to do
ERRNOCAMERAPOWER = 138 # The camera is powered off
ERRINSUF1394ISOCBANDWIDTH = 201 # The is insufficient isochronous bandwidth available on the 1394 bus
ERRINSUF1394ISOCRESOURCES = 202 # The is insufficient 1394 isochronous resources available
ERRNO1394ISOCCHANNEL = 203 # The is no isochronous channel available on the 1394 bus
ERRUSBVERSIONLOWERTHAN2 = 204 # The USB bus version is lower than 2.0

RUNNING = 1001 # The process is running (only applicable when SPOT_WAITFORSTATUSCHANGES is TRUE)

# Image Sensor Types for Use with SPOT_IMAGESENSORTYPE
IMAGESENSORTYPE_CCDINTERLINE = 0x0011 # Conventional interline CCD
IMAGESENSORTYPE_CCDFULLFRAME = 0x0021 # Conventional full-frame CCD
IMAGESENSORTYPE_CCDFRAMETRANSFER = 0x0031 # Conventional frame-transfer CCD
IMAGESENSORTYPE_CCDINTERLINEEM = 0x0111 # Electron-Multiplication interline CCD
IMAGESENSORTYPE_CCDFRAMETRANSFEREM = 0x0131 # Electron-Multiplication frame-transfer CCD
IMAGESENSORTYPE_CMOSROLLINGSHUTTER = 0x0042 # CMOS rolling shutter
IMAGESENSORTYPE_CMOSGLOBALSHUTTER = 0x0012 # CMOS global shutter

# Color Values Used with SpotGetLiveImages
COLORRED = 1
COLORGREEN = 2
COLORBLUE = 3
COLORCLEAR = 10
COLORRGB = 0
COLORRG = 21 # Red-Green
COLORRB = 22 # Red-Blue
COLORGB = 23 # Green-Blue
COLORNONE = 99

# Rotate Values Used with SpotGetLiveImages
ROTATENONE = 0
ROTATELEFT = 1
ROTATERIGHT = 2

# Color Enhancement Rendering Intent Values for Use with SPOT_COLORRENDERINGINTENT
COLORRENDERINGINTENT_RELATIVECOLORIMETRIC = 1
COLORRENDERINGINTENT_ABSOLUTECOLORIMETRIC = 2
COLORRENDERINGINTENT_PERCEPTUAL = 3
COLORRENDERINGINTENT_SATURATION = 4

# Image Types for Use with SPOT_IMAGETYPE
IMAGEBRIGHTFLD = 1
IMAGEDARKFLD = 2

# External Trigger Types for Use with SPOT_EXTERNALTRIGGERMODE
TRIGMODENONE = 0 # No trigger
TRIGMODEEDGE = 1 # Edge Trigger
TRIGMODEBULB = 2 # Bulb Trigger

# Bus Bandwidth Levels for Use with SPOT_BUSBANDWIDTH
HIGHBW = 1
MEDIUMBW = 2
LOWBW = 3

# External Trigger Active States for Use with SPOT_EXTERNALTRIGGERACTIVESTATE
TRIGACTIVESTATE_LOW = 0
TRIGACTIVESTATE_HIGH = 1

# TTL Output Active States for Use with SPOT_TTLOUTPUTACTIVESTATE
TTLACTIVESTATE_LOW = 0
TTLACTIVESTATE_HIGH = 1

# Values for Use with SpotGetSequentialImages
INTERVALSHORTASPOSSIBLE = (-1)
INFINITEIMAGES = (0x7fffffff)

# Mosaic Pattern Types for Use with SPOT_MOSAICPATTERN
MOSAICBAYERGRBG = 1 # Bayer pattern - Even lines: GRG.. Odd lines: BGB...  (zero-based)
MOSAICBAYERRGGB = 2 # Bayer pattern - Even lines: RGR.. Odd lines: GBG...
MOSAICBAYERBGGR = 3 # Bayer pattern - Even lines: BGB.. Odd lines: RGR...
MOSAICBAYERGBRG = 4 # Bayer pattern - Even lines: GBG.. Odd lines: RGR...

# 24 BPP Image Formats for Use with SPOT_24BPPIMAGEBUFFERFORMAT
#24BPPIMAGEBUFFERFORMATBGR = 1 # Blue, Green, Red (3 bytes per pixel with padding) (standard Window BITMAP)
#24BPPIMAGEBUFFERFORMATRGB = 2 # Red, Green, Blue (3 bytes per pixel with padding)
#24BPPIMAGEBUFFERFORMATARGB = 3 # Alpha, Red, Green, Blue (4 bytes per pixel)
#24BPPIMAGEBUFFERFORMATABGR = 4 # Alpha, Blue, Green, Red (4 bytes per pixel)
#24BPPIMAGEBUFFERFORMATRGBA = 5 # Red, Green, Blue, Alpha (4 bytes per pixel)
#24BPPIMAGEBUFFERFORMATBGRA = 6 # Blue, Green, Red, Alpha (4 bytes per pixel)

# Gain Port Attribute Flags for Use with SPOT_PORTnGAINATTRIBUTES
GAINATTR_COMPUTABLE = 0x01 # The actual gain can be computed with SpotGetActualGainValue() or SpotGetActualLiveGainValue()
GAINATTR_SAMEASPORT0 = 0x02 # This gain port is the same as port 0, except that a range is provided (instead of a discrete value list)
GAINATTR_ELECTRONMULT = 0x04 # Electron multiplication gain
GAINATTR_GATING = 0x08 # Gating gain

# Shutter Modes for Use with SPOT_SHUTTERMODE
SHUTTERMODE_NORMAL = 0
SHUTTERMODE_OPEN = 1
SHUTTERMODE_CLOSED = 2

# Sensor Clear Modes for Use with SPOT_SENSORCLEARMODE and SPOT_SENSORCLEARMODES
SENSORCLEARMODE_CONTINUOUS = 0x01 # Continuously clear sensor
SENSORCLEARMODE_PREEMPTABLE = 0x02 # Allow exposures to pre-emp sensor clearing
SENSORCLEARMODE_NEVER = 0x04 # Never clear sensor

# Sensor Response Modes for use with SPOT_SENSORRESPONSEMODE
SENSORRESPMODE_IR = 0x01 # Enhanced IR response
SENSORRESPMODE_DYNAMICRANGE = 0x02 # Enhanced dynamic range
SENSORRESPMODE_SENSITIVITY = 0x04 # Enhanced sensitivity
SENSORRESPMODE_ANTIBLOOMING = 0x08 # Enhanced anti-blooming
SENSORRESPMODE_GLOWSUPPRESSION = 0x10 # Suppression of sensor glow

# Control Flags for Use with SpotUpdateFirmware
UPDATEFWCONTROL_FORCEUPDATECAMERA = 1 # Load camera firmware even if older than current
UPDATEFWCONTROL_FORCEUPDATEINTFCARD = 2 # Load interface card firmware even if older than current

# Result Flags for Use with SpotUpdateFirmware
UPDATEFWRESULT_POWEROFFDEV = 1 # Power off the device before using
UPDATEFWRESULT_POWEROFFCOMPUTER = 2 # Power off the computer before using the camera
UPDATEFWRESULT_REBOOTCOMPUTER = 4 # Reboot the computer before using the camera

# Message Types for Use in SPOT_MESSAGE_STRUCT
MESSAGETYPE_INFO = 1
MESSAGETYPE_WARNING = 2
MESSAGETYPE_ERROR = 3

# Parameters for use with SpotSetValue() and SpotGetValue()
AUTOEXPOSE = 100 # BOOL
BRIGHTNESSADJ = 101 # float
AUTOGAINLIMIT = 102 # short
BINSIZE = 103 # short
IMAGERECT = 104 # SPOT_RECT structure
EXPOSURE2 = 105 # SPOT_EXPOSURE_STRUCT2
EXPOSURE = 106 # SPOT_EXPOSURE_STRUCT
COLORENABLE = 108 # SPOT_COLOR_ENABLE_STRUCT
COLORORDER = 109 # char * (eg. "RGB", etc)
WHITEBALANCE = 110 # SPOT_WHITE_BAL_STRUCT
IMAGETYPE = 111 # short (SPOT_IMAGEBRIGHTFLD or SPOT_IMAGEDARKFLD)
CORRECTCHIPDEFECTS = 112 # BOOL
BITDEPTH = 113 # short
MESSAGEENABLE = 114 # BOOL
WHITEBALANCEX1000 = 115 # SPOT_WHITE_BAL_INT_STRUCT
BRIGHTNESSADJX1000 = 116 # long
LIVEBRIGHTNESSADJ = 118 # float
LIVEBRIGHTNESSADJX1000 = 119 # long
LIVEAUTOGAINLIMIT = 200 # short
SUBTRACTBLACKLEVEL = 201 # BOOL
MONITORFILTERPOS = 202 # BOOL
COLORENABLE2 = 203 # SPOT_COLOR_ENABLE_STRUCT2
DRIVERDEVICENUMBER = 204 # short
ENABLETTLOUTPUT = 205 # BOOL
TTLOUTPUTDELAYMS = 206 # short (value in ms)
LIVEGAMMAADJ = 207 # float
LIVEGAMMAADJX1000 = 208 # long
LIVEEXPOSURE = 210 # SPOT_EXPOSURE_STRUCT2
MINEXPOSUREMSEC = 211 # short
RETURNRAWMOSAICDATA = 212 # BOOL
LIVEACCELERATIONLEVEL = 213 # short
ENHANCECOLORS = 214 # BOOL
FLATFLDCORRECT = 215 # NULL-terminated file name string
NOISEFILTERTHRESPCT = 216 # short
LIVEAUTOBRIGHTNESS = 217 # BOOL
LIVEMAXEXPOSUREMSEC = 220 # long
EXPOSUREINCREMENT = 221 # long
EXTERNALTRIGGERMODE = 222 # short (SPOT_TRIGMODENONE, SPOT_TRIGMODEEDGE, or SPOT_TRIGMODEBULB)
MAXEXPOSUREMSEC = 223 # long
WHITEBALCOMPRECT = 224 # SPOT_RECT structure
BIASFRMSUBTRACT = 225 # NULL-terminated file name string
DEVICEUID = 226 # SPOT_DEVICE_UID union
BUSBANDWIDTH = 227 # short (SPOT_HIGHBW, SPOT_MEDIUMBW, or SPOT_LOWBW)
EXPOSURECOMPRECT = 228 # SPOT_RECT structure
EXTERNALTRIGGERACTIVESTATE = 229 # short (SPOT_TRIGACTIVESTATE_LOW or SPOT_TRIGACTIVESTATE_HIGH)
EXTERNALTRIGGERDELAY = 230 # long (value in microseconds)
REGULATETEMPERATURE = 231 # BOOL
REGULATEDTEMPERATURE = 232 # short (degrees C * 100)
HORIZREADOUTFREQUENCY = 233 # long (value in kHz)
TTLOUTPUTACTIVESTATE = 234 # short (SPOT_TTLACTIVESTATE_LOW or SPOT_TTLACTIVESTATE_HIGH)
TTLOUTPUTDELAY = 235 # long (value in microseconds)
BKGDIMAGESUBTRACT = 236 # NULL-terminated file name string
GAINPORTNUMBER = 237 # short (0=port 0, 1=port 1, etc.)
COLORRENDERINGINTENT = 238 # short (one of the SPOT_COLORRENDERINGINTENT_xxx values)
LIVEENHANCECOLORS = 239 # BOOL
PIXELRESOLUTIONLEVEL = 240 # short (0=normal, 1+=higher, -1-=lower)
INPUTCOLORPROFILE = 241 # NULL-terminated file name string
OUTPUTCOLORPROFILE = 242 # NULL-terminated file name string
COLORBINSIZE = 243 # short
SENSORCLEARMODE = 244 # DWORD
COOLINGLEVEL = 245 # short
FANSPEED = 246 # short
FANEXPOSURESPEED = 247 # short (fan speed to use during exposure, -1 to disable option)
FANEXPOSUREDELAYMS = 248 # short (value in ms)
PREAMPGAINVAL = 249 # float
VERTSHIFTPERIOD = 250 # long  (value in ns)
VERTCLOCKVOLTAGEBOOST = 251 # short
READOUTCIRCUIT = 252 # short
NUMBERSKIPLINES = 253 # short
SHUTTERMODE = 254 # short (SPOT_SHUTTERMODE_NORMAL, SPOT_SHUTTERMODE_OPEN, or SPOT_SHUTTERMODE_CLOSED)
ENABLEPOWERSTATECONTROL = 260 # BOOL
FORCESINGLECHANLIVEMODE = 261 # BOOL
LIVEIMAGESCALING = 262 # SPOT_LIVE_IMAGE_SCALING_STRUCT (or NULL-pointer to disable)
LIVEHISTOGRAM = 263 # SPOT_LIVE_HISTOGRAM_STRUCT (or NULL-pointer to disable)
SENSORRESPONSEMODE = 264 # DWORD
SEQIMAGEDISKCACHEPATH = 265 # NULL-terminated directory name string
SEQIMAGEEXPDURS = 266 # array of DWORDs (1st val is count)
LIVESUBTRACTBLACKLEVEL = 267 # BOOL
LIVEPIXELRESOLUTIONLEVEL = 268 # short (0=normal, 1+=higher, -1-=lower)
COOLERMODEONEXIT = 269 # short (0=off, 1=on)
WAITFORSTATUSCHANGES = 501 # BOOL
IMAGEORIENTATION = 701 # short (1=top-first, -1=bottom-first)
IMAGEBUFFERFORMAT = 702 # short
NUMBERBYTESPERIMAGEROW = 703 # long

# Parameters for use with SpotGetValue()
BRIGHTNESSADJLIMITS = 120 # array of two floats
BINSIZELIMITS = 121 # array of two shorts - Use SPOT_BINSIZES instead
MAXIMAGERECTSIZE = 122 # array of two shorts (ie. max width, max height)
GAINVALS8 = 123 # array of shorts (1st val is count)
GAINVALS16 = 129 # array of shorts (1st val is count)
BITDEPTHS = 124 # array of shorts (1st val is count)
BRIGHTNESSADJLIMITSX1000 = 125 # array of two longs
EXPOSURELIMITS = 126 # array of two longs (min, max in msec)
EXPOSURELIMITS2 = 127 # array of two DWORDs (min, max exposure)
LIVEGAINVALS = 128 # array of shorts (1st val is count)
MAXLIVEACCELERATIONLEVEL = 130 # short
MAXWHITEBALANCERATIO = 131 # float
MAXWHITEBALANCERATIOX1000 = 132 # long
MINEXPOSUREINCREMENT = 133 # long (value in nanoseconds)
EXPOSURECONVFACTOR = 134 # float
EXPOSURECONVFACTORX1000 = 135 # long
MOSAICPATTERN = 136 # short (one of the SPOT_MOSAICxxx values)
EXTERNALTRIGGERDELAYLIMITS = 137 # array of two longs (min, max values in microseconds)
REGULATEDTEMPERATURELIMITS = 138 # array of two shorts (degrees C * 10)
HORIZREADOUTFREQUENCIES = 139 # array of longs (1st val is count)
TTLOUTPUTDELAYLIMITS = 140 # array of two longs (min, max values in microseconds)
EXPOSURERESOLUTION = 141 # long (value in nanoseconds)
MAXGAINPORTNUMBER = 144 # short
PORT0GAINVALS8 = GAINVALS8 # array of shorts (1st val is count)
PORT0GAINVALS16 = GAINVALS16 # array of shorts (1st val is count)
PORT0LIVEGAINVALS = LIVEGAINVALS # array of shorts (1st val is count)
PORT1GAINVALLIMITS = 145 # array of two longs (min, max port 1 gain values)
PORT1LIVEGAINVALLIMITS = 146 # array of two longs (min, max port 1 gain values)
PORT2GAINVALLIMITS = 147 # array of two longs (min, max port 2 gain values)
PORT2LIVEGAINVALLIMITS = 148 # array of two longs (min, max port 2 gain values)
PORT3GAINVALLIMITS = 149 # array of two longs (min, max port 3 gain values)
PORT3LIVEGAINVALLIMITS = 150 # array of two longs (min, max port 3 gain values)
BINSIZES = 151 # array of shorts (1st val is count)
MAXPIXELRESOLUTIONLEVEL = 152 # short
ACQUIREDIMAGESIZE = 153 # array of two shorts (ie. width, height)
ACQUIREDLIVEIMAGESIZE = 154 # array of two shorts (ie. width, height)
MINIMAGERECTSIZE = 155 # array of two shorts (ie. min width, min height)
COLORBINSIZES = 156 # array of shorts (1st val is count)
LIVEAUTOBRIGHTNESSADJ = 218 # float
LIVEAUTOBRIGHTNESSADJX1000 = 219 # long
PIXELSIZE = 401 # array of two longs (x, y sizes in nm)
COOLINGLEVELS = 403 # array of two shorts (min, max)
FANSPEEDS = 404 # array of two shorts (min, max)
NUMBERREADOUTCIRCUITS = 405 # short
PREAMPGAINVALS = 406 # array of floats (1st val is count)
VERTSHIFTPERIODS = 407 # array of longs (1st val is count)
MAXVERTCLOCKVOLTAGEBOOST = 408 # short
PORT0GAINATTRIBUTES = 411 # DWORD
PORT1GAINATTRIBUTES = 412 # DWORD
PORT2GAINATTRIBUTES = 413 # DWORD
PORT3GAINATTRIBUTES = 414 # DWORD
READOUTCIRCUITDESCR = 415 # NULL-terminated description string
IMAGESENSORMODELDESCR = 416 # NULL-terminated description string
IMAGESENSORTYPE = 417 # DWORD
MINFASTSEQIMAGEEXPDUR = 418 # DWORD (value in SPOT_EXPOSUREINCREMENT units)
MAXNUMBERSKIPLINES = 421 # short
SENSORRESPONSEMODES = 422 # array of DWORDs (1st val is count)
SENSORCLEARMODES = 423 # array of DWORDs (1st val is count)
MINPIXELRESOLUTIONLEVEL = 424 # short
MAXNUMBERSEQIMAGEEXPDURS = 425 # short
PIXELRESOLUTIONIMGSIZEFACTORS = 426 # array of floats (SPOT_MAXPIXELRESOLUTIONLEVEL-SPOT_MINPIXELRESOLUTIONLEVEL+1 elements)

# Flags for use with SpotGetCameraAttributes()
ATTR_COLOR = 0x00000001 # camera can return color images
ATTR_SLIDER = 0x00000002 # camera has a color filter slider
ATTR_LIVEMODE = 0x00000004 # camera can run live mode
ATTR_MOSAIC = 0x00000008 # camera has a Bayer pattern color mosaic CCD chip
ATTR_EDGETRIGGER = 0x00000010 # camera has an edge-type external trigger
ATTR_BULBTRIGGER = 0x00000020 # camera has a bulb-type external trigger
ATTR_CLEARFILTER = 0x00000040 # camera has a color filter with a clear state
ATTR_1394 = 0x00000080 # camera is an IEEE-1394/FireWire device
ATTR_COLORFILTER = 0x00000100 # camera has a color filter (color images require multiple shots)
ATTR_TEMPERATUREREADOUT = 0x00000200 # camera can read the sensor temperature
ATTR_TEMPERATUREREGULATION = 0x00000400 # camera can regulate the sensor temperature
ATTR_TRIGGERACTIVESTATE = 0x00000800 # camera can set trigger input active state
ATTR_DUALAMPLIFIER = 0x00001000 # camera has separate amplifier circuits for live mode and capture
ATTR_ACCURATETTLDELAYTIMING = 0x00002000 # camera can accurately time TTL output and trigger delays (to microseconds)
ATTR_SLIDERPOSITIONDETECTION = 0x00004000 # camera can detect the color filter slider position
ATTR_AUTOEXPOSURE = 0x00008000 # camera can compute exposure
ATTR_TTLOUTPUT = 0x00010000 # camera has a TTL output
ATTR_SENSORSHIFTING = 0x00020000 # camera can shift the position of the image sensor for higher resolution
ATTR_FILTERWHEEL = 0x00040000 # camera has a mechanical filter wheel
ATTR_BLACKLEVELSUBTRACT = 0x00080000 # camera can do black-level subtraction
ATTR_CHIPDEFECTCORRECTION = 0x00100000 # camera can do chip defect correction
ATTR_INTERNALSHUTTER = 0x00200000 # camera has an internal mechanical shutter
ATTR_EXPOSURESHUTTER = 0x00400000 # camera's internal shutter can be used for exposure
ATTR_TTLOUTPUTDURINGEXPOSURE = 0x00800000 # camera can activate TTL output during exposure
ATTR_SINGLECHANLIVEMODE = 0x01000000 # camera can use a single readout channel in live mode
ATTR_MULTICHANLIVEMODE = 0x02000000 # camera can use mutiple parallel readout channels in live mode
ATTR_FIRMWAREUPDATE = 0x04000000 # camera's firmware can be updated through the SpotCam API
ATTR_LIVEHISTOGRAM = 0x08000000 # camera can provide histogram information and do stretching in live mode

# Interface Types for use with SpotFindDevices()
INTFTYPE_PCI = 2 # PCI card
INTFTYPE_1394 = 3 # 1394 (FireWire) camera
INTFTYPE_USB = 4 # USB camera

# Device Types for use with SpotFindDevices()
DEVTYPE_RTCARD = 3 # SPOT RT card
DEVTYPE_RTINSIGHTCARD = DEVTYPE_RTCARD
DEVTYPE_INSIGHTCARD = 4 # SPOT Insight card
DEVTYPE_RTSE18CARD = 6 # SPOT RT-SE18 card
DEVTYPE_RT2CARD = 7 # SPOT RT2 card
DEVTYPE_BOOSTCARD = 8 # SPOT Boost card
DEVTYPE_1394CAMERA = 32 # SPOT 1394 camera
DEVTYPE_USBCAMERA = 41 # SPOT USB camera

# Status Values
STATUSIDLE = 0 # Doing nothing (operation completed)
STATUSDRVNOTINIT = 1 # Driver not initialized
STATUSEXPOSINGRED = 2 # Exposing in Red -
STATUSEXPOSINGGREEN = 3 # Exposing in Green -
STATUSEXPOSINGBLUE = 4 # Exposing in Blue -
STATUSIMAGEREADRED = 5 # Downloading Red image -
STATUSIMAGEREADGREEN = 6 # Downloading Green image -
STATUSIMAGEREADBLUE = 7 # Downloading Blue image -
STATUSCOMPEXP = 8 # Computing exposure
STATUSCOMPWHITEBAL = 9 # Computing white balance
STATUSGETIMAGE = 10 # Getting an image
STATUSLIVEIMAGEREADY = 11 # Live image is available in buffer
STATUSEXPOSINGCLEAR = 12 # Exposing in Clear -
STATUSEXPOSING = 13 # Exposing (filter off or no filter) -
STATUSIMAGEREADCLEAR = 14 # Downloading monchrome image (clear filter)
STATUSIMAGEREAD = 15 # Downloading monchrome image (no filter)
STATUSSEQIMAGEWAITING = 16 # Waiting to acquire the next sequential image
STATUSSEQIMAGEREADY = 17 # A sequential image is available for
STATUSIMAGEPROCESSING = 18 # Processing an acquired image
STATUSWAITINGFORTRIGGER = 19 # Waiting for a trigger
STATUSWAITINGFORBLOCKLIGHT = 20 # The user should block all light to the camera
STATUSWAITINGFORMOVETOBKGD = 21 # The user should move the specimen out of the path
STATUSTTLOUTPUTDELAY = 22 # Waiting for the specified TTL output delay to elapse
STATUSEXTERNALTRIGGERDELAY = 23 # Waiting for the specified extrenal trigger delay to elapse
STATUSWAITINGFORCOLORFILTER = 24 # Waiting for the color filter to change
STATUSGETLIVEIMAGES = 25 # Starting live image acquisition mode
STATUSFANDELAY = 26 # Waiting for specified delay after changing fan speed
STATUSFIRMWAREUPDATING = 27 # Updating firmware for a device

STATUSRUNNING = 500 # The process is running (only applicable when SPOT_WAITFORSTATUSCHANGES is TRUE)
STATUSABORTED = 100 # Last operation was aborted
STATUSERROR = 101 # Last operation ended in an error -

# Device Notification Event Types
DEVEVENTTYPE_DEVADDED = 1 # A new device has been added - lInfo = 0
DEVEVENTTYPE_DEVREMOVED = 2 # A device has been removed - lInfo = 0

# Old #defines included for backward-compatibility
DEVTYPE_INSIGHT1394 = DEVTYPE_1394CAMERA
ERRNOINTFCARDSFOUND = ERRNODEVICESFOUND
EXPOSUREADJ = BRIGHTNESSADJ
EXPOSUREADJX1000 = BRIGHTNESSADJX1000
EXPOSUREADJLIMITS = BRIGHTNESSADJLIMITS
EXPOSUREADJLIMITSX1000 = BRIGHTNESSADJLIMITSX1000
LIVEGAINADJ = LIVEBRIGHTNESSADJ
LIVEGAINADJX1000 = LIVEBRIGHTNESSADJX1000
EXTERNALSHUTTERENABLE = ENABLETTLOUTPUT
GAINVALS = GAINVALS8
FLUORESCENCECOLORS = 117 # No longer supported
EXTERNALSHUTTERLAG = TTLOUTPUTDELAYMS
STATUSSHUTTEROPENRED = STATUSEXPOSINGRED
STATUSSHUTTEROPENGREEN = STATUSEXPOSINGGREEN
STATUSSHUTTEROPENBLUE = STATUSEXPOSINGBLUE
STATUSSHUTTEROPENCLEAR = STATUSEXPOSINGCLEAR
STATUSSHUTTEROPEN = STATUSEXPOSING
GAINVALS12 = GAINVALS16
PORT0GAINVALS12 = PORT0GAINVALS16
CLEARMODECAMDEFAULT = 0
ERRVXDOPEN = 111 # no longer supported
ERRWINRTLOAD = 112 # no longer supported
ERRWINRTUNLOAD = 113 # no longer supported
ERRNOCAMERAINFOFILE = 116 # no longer supported
CLEARMODE = SENSORCLEARMODE
CLEARMODES = 402
CLEARMODEALWAYSAFTERREAD = SENSORCLEARMODE_CONTINUOUS
CLEARMODEPREEMPTABLE = SENSORCLEARMODE_PREEMPTABLE

