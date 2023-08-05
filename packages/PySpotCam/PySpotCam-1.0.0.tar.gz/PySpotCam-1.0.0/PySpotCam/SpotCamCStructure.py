import ctypes
from ctypes import *

BOOL = ctypes.c_bool
float = ctypes.c_float
int = ctypes.c_int
char = ctypes.c_char
BYTE = ctypes.c_byte
long = ctypes.c_long
word = ctypes.c_ulong
dword = ctypes.c_long
short = ctypes.c_short
WORD = ctypes.c_ushort
DWORD = ctypes.c_ulong
QWORD = ctypes.c_int64



class StrucUnionRepr(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        valeurs = ["\t%s = %s"%(name, str(getattr(self, name)).replace('\t','\t\t')) for (name, valtype) in self._fields_]
        return "%s(\n%s)"%(class_name, ',\n'.join(valeurs))
    
class Structure(Structure, StrucUnionRepr):
    pass

class Union(Union, StrucUnionRepr):
    pass

struct = Structure
union = Union

class RECT(struct):
	_fields_=[("left",int),
        ("top",int),
        ("right",int),
        ("bottom",int)]

class SUB_EXPOSURE_STRUCT(union):
	_fields_=[("lExpMSec",long),
        ("lClearExpMSec",long),
        ("lRedExpMSec",long)]

class EXPOSURE_STRUCT(struct):
	_fields_=[("sub_field" , SUB_EXPOSURE_STRUCT),
        ("lGreenExpMSec",long),
        ("lBlueExpMSec",long),
        ("nGain",short)]

class SUB_EXPOSURE_STRUCT2(union):
	_fields_=[("dwClearExpDur",DWORD),
        ("dwExpDur",DWORD)]

class EXPOSURE_STRUCT2(struct):
	_fields_=[("dwRedExpDur",DWORD),
        ("dwGreenExpDur",DWORD),
        ("dwBlueExpDur",DWORD),
        ("sub_field" , SUB_EXPOSURE_STRUCT2),
        ("nGain",short)]

class COLOR_ENABLE_STRUCT(struct):
	_fields_=[("bEnableRed",BOOL),
        ("bEnableGreen",BOOL),
        ("bEnableBlue",BOOL)]

class COLOR_ENABLE_STRUCT2(struct):
	_fields_=[("bEnableRed",BOOL),
        ("bEnableGreen",BOOL),
        ("bEnableBlue",BOOL),
        ("bEnableClear",BOOL)]

class WHITE_BAL_STRUCT(struct):
	_fields_=[("nReserved",short),
        ("fRedVal",float),
        ("fGreenVal",float),
        ("fBlueVal",float)]

class WHITE_BAL_INT_STRUCT(struct):
	_fields_=[("lRedVal",long),
        ("lGreenVal",long),
        ("lBlueVal",long)]

class VERSION_STRUCT(struct):
	_fields_=[("szProductName",char*255),
        ("szCopyright",char*255),
        ("wVerMajor",WORD),
        ("wVerMinor",WORD),
        ("wVerUpdate",WORD),
        ("szCameraSerialNum",char*31)]

class SUB_VERSION_STRUCT2(union):
	_fields_=[("szCameraRevNum",char*11),
        ("szCameraHardwareRevNum",char*11)]

class VERSION_STRUCT2(struct):
	_fields_=[("szProductName",char*255),
        ("szCopyright",char*101),
        ("szCameraFirmwareRevNum",char*11),
        ("szCardHardwareRevNum",char*11),
        ("szCardFirmwareRevNum",char*11),
        ("Reserved",char*119),
        ("wVerBugFix",WORD),
        ("wVerMajor",WORD),
        ("wVerMinor",WORD),
        ("wVerUpdate",WORD),
        ("byReserved",BYTE),
        ("szCameraSerialNum",char*21),
        ("szCameraModelNum",char*11),
        ("sub_field" , SUB_VERSION_STRUCT2)]

class PCI_CARD_STRUCT(struct):
	_fields_=[("dwBus",DWORD),
        ("dwSlot",DWORD),
        ("dwFunction",DWORD)]

class SPOT_1394_CAMERA_STRUCT(struct):
	_fields_=[("n1394NodeNumber",int),
        ("n1394BusNumber",int),
        ("Reserved",BYTE*12)]

class SUB_DEVICE_UID(struct):
	_fields_=[("dwLowPart",DWORD),
        ("dwHighPart",DWORD)]

class DEVICE_UID(union):
	_fields_=[("sub_field" , SUB_DEVICE_UID),
        ("qwQuadPart",QWORD)]

class SUB_DEVICE_STRUCT(union):
	_fields_=[("stPCICard",PCI_CARD_STRUCT),
        ("st1394Camera",SPOT_1394_CAMERA_STRUCT),
        ("Reserved",BYTE*28)]

class DEVICE_STRUCT(struct):
	_fields_=[("nDeviceType",int),
        ("nInterfaceType",int),
        ("sub_field" , SUB_DEVICE_STRUCT),
        ("dwAttributes",DWORD),
        ("szDescription",char*54),
        ("DeviceUID",DEVICE_UID)]

class TIMESTAMP_STRUCT(struct):
	_fields_=[("wYear",WORD),
        ("wMonth",WORD),
        ("wDay",WORD),
        ("wHour",WORD),
        ("wMinute",WORD),
        ("wSecond",WORD),
        ("dwMicrosecond",DWORD)]

class BIAS_FRAME_COMPATIBILITY_INFO_STRUCT(struct):
	_fields_=[("szCameraSerialNum",char*21),
        ("nBitDepth",int),
        ("nBinSize",int),
        ("stImageRect",RECT),
        ("anGains",int*50),
        ("nReadoutCircuit",int),
        ("nGainPort",int),
        ("fPreAmpGain",float),
        ("nTemperature",int),
        ("nPixelResolutionLevel",int),
        ("Reserved",BYTE*80)]

class FLATFIELD_COMPATIBILITY_INFO_STRUCT(struct):
	_fields_=[("szCameraSerialNum",char*21),
        ("nBinSize",int),
        ("bHasRed",BOOL),
        ("bHasGreen",BOOL),
        ("bHasBlue",BOOL),
        ("bHasClear",BOOL),
        ("nPixelResolutionLevel",int),
        ("Reserved",BYTE*100)]

class BKGD_IMAGE_COMPATIBILITY_INFO_STRUCT(struct):
	_fields_=[("szCameraSerialNum",char*21),
        ("nBitDepth",int),
        ("nBinSize",int),
        ("stImageRect",RECT),
        ("bHasRed",BOOL),
        ("bHasGreen",BOOL),
        ("bHasBlue",BOOL),
        ("bHasClear",BOOL),
        ("nPixelResolutionLevel",int),
        ("nReadoutCircuit",int),
        ("nGainPort",int),
        ("fPreAmpGain",float),
        ("nTemperature",int),
        ("Reserved",BYTE*84)]

class LIVE_IMAGE_SCALING_STRUCT(struct):
	_fields_=[("bAutoScale",BOOL),
        ("fBlackOverflowPct",float),
        ("fWhiteOverflowPct",float),
        ("stSampleRect",RECT),
        ("nBlackPoint",int),
        ("nWhitePoint",int),
        ("nScale",int),
        ("Reserved",BYTE*96)]

class MESSAGE_STRUCT(struct):
	_fields_=[("nMessageType",int),
        ("nReserved",int),
        ("szMessage",char*256),
        ("nValue",int),
        ("Reserved",BYTE*50)]



class SPOT_VERSION_STRUCT(struct):
    _fields_ = [("szProductName", char*255),
                ("szCopyright", char*255),
                ("wVerMajor", WORD),
                ("wVerMinor", WORD),
                ("wVerUpdate", WORD),
                ("szCameraSerialNum", char*31) 
                ]

class SPOT_VERSION_STRUCT2(struct):
    _fields_ = [('szProductName', char*255),
                ('szCopyright', char*101),
                ('szCameraFirmwareRevNum', char*11),
                ('szCardHardwareRevNum', char*11),
                ('szCardFirmwareRevNum', char*11),
                ('Reserved', char*119),
                ('wVerBugFix', WORD),
                ("wVerMajor", WORD),
                ("wVerMinor", WORD),
                ("wVerUpdate", WORD),
                ('byReserved', BYTE),
                ("szCameraSerialNum", char*21),                
                ("szCameraModelNum", char*11),
                ('szCameraRevNum', char*11)]
#typedef struct
#{
#   char szProductName[255];
#   char szCopyright[101];
#   char szCameraFirmwareRevNum[11];
#   char szCardHardwareRevNum[11];
#   char szCardFirmwareRevNum[11];
#   char Reserved[119];
#   WORD wVerBugFix;
#   WORD wVerMajor;  // Driver version
#   WORD wVerMinor;
#   WORD wVerUpdate;
#   BYTE byReserved;
#   char szCameraSerialNum[21];
#   char szCameraModelNum[11];
#   union
#   {
#      char szCameraRevNum[11];
#      char szCameraHardwareRevNum[11];
#   };
#} SPOT_VERSION_STRUCT2;


##### CALLBACK ######

#typedef VOID (WINAPI *SPOTCALLBACK)(int iStatus, long lInfo, DWORD dwUserData);
SPOTCALLBACK = ctypes.CFUNCTYPE(None, int, long, DWORD)
#typedef VOID (WINAPI *SPOTDEVNOTIFYCALLBACK)(int iEventType, long lInfo, DEVICE_UID *pDeviceUID, DWORD dwUserData);
SPOTDEVNOTIFYCALLBACK = ctypes.CFUNCTYPE(None, int, long, POINTER(DEVICE_UID), DWORD)
#typedef BOOL (WINAPI *SPOTBUSYCALLBACK)(DWORD dwUserData);  // Return true to abort operation
SPOTBUSYCALLBACK= ctypes.CFUNCTYPE(BOOL, DWORD)



