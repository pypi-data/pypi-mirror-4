from ctypes import *
import numpy as np

import SpotValue
import SpotCamFunction
import SpotCamEnum
import SpotValueClassDefinition

class static_property(object):
    def __init__(self, static_method):
        self.m = static_method
        self.__doc__ = static_method.__get__(self).__doc__

    def __get__(self, obj, typ):
        if obj is None : return self
        return self.m.__get__(self)()

    def __set__(self, obj, value):
        raise AttributeError, "can't set attribute"

    def __delete__(self, obj):
        raise AttributeError, "can't delete attribute"


class SpotMetaClass(type):
    def __new__(cls, name, bases, dct):
        for key,value in dct.iteritems():
            if isinstance(value, type) and issubclass(value, SpotValueClassDefinition.SpotFunction):
                dct[key] = value() 
        return super(SpotMetaClass, cls).__new__(cls, name, bases, dct)
    
class SpotClass(object):
    """Main class of the PySpotCam modules

    
    - All the function defined in the SpotCam API are static method of this class
    - Functions that get a value without parameters are implemented as property
    - The parameters and camera values (SpotGetValue and SpotSetValue) are implemented as property
    """
#    __metaclass__ = SpotMetaClass
    # Add the class defined in SpotValue module
    for elm in set(dir(SpotValue))-set(dir(SpotValueClassDefinition)):
        attr = getattr(SpotValue, elm)
        if isinstance(attr, type) and issubclass(attr, SpotValueClassDefinition.SpotFunction):
            exec('{elm} = SpotValue.{elm}()'.format(elm = elm))

    _list_simple_method=["ClearStatus",
        'ComputeExposure',
        'ComputeExposure2',
        'ComputeExposureConversionFactor',
        'ComputeExposureConversionFactorX1000',
        'ComputeWhiteBalance',
        'ComputeWhiteBalanceX1000', 
        'DumpCameraMemory',
        'Exit',
        'FindDevices',
        'GetActualGainValue',
        'GetActualLiveGainValue',
        'GetActualGainValueX1000',
        'GetActualLiveGainValueX1000',
        'GetBackgroundImage',
        'GetBackgroundImageCompatibilityInformation',
        'GetBiasFrame',
        'GetBiasFrameCompatibilityInformation',
        'GetCameraAttributes',
        'GetCameraErrorCode',
        'GetExposureTimestamp',
        'GetFlatfield',
        'GetFlatfield2',
        'GetFlatfieldCompatibilityInformation',
        'GetSensorCurrentTemperature',
        'GetSensorExposureTemperature',
        'GetValueSize',
        'GetVersionInfo',
        'GetVersionInfo2',
        'QueryCameraPresent',
        'QueryColorFilterPosition',
        'QueryStatus',
        'SetAbortFlag',
        'SetBusyCallback',
        'SetCallback',
        'SetDeviceNotificationCallback',
        'SetTTLOutputState',
        'UpdateFirmware',
        'WaitForStatusChange']

    for fname in _list_simple_method:
        exec('{fname} = staticmethod(SpotCamFunction.{fname})'.format(fname = fname))

    def SetExposure(self, gain=None, time=None):
        if gain or time:
            exposure = self.Exposure
            if gain is not None : exposure.ngain = gain
            if time is not None : exposure.sub_field.lExpMSec = time
            self.Exposure = exposure  

    @staticmethod
    def Init():
        SpotCamFunction.Init()


    @staticmethod
    def Exit():
        SpotCamFunction.Exit()
        
    def __init__(self):
        self.Init()


    @staticmethod
    def GetImage():
        """Get an image and returns a numpy array"""
        size = SpotClass.AcquiredImageSize.get()
        bit_depth = SpotClass.BitDepth.get()
        size_per_px = 1 if  bit_depth <=8 else 2
        image = c_buffer(size.width*size.height*size_per_px)
        SpotCamFunction.GetImage(0,False,0,pointer(image), None, None, None)
        return np.frombuffer(image, dtype=np.uint8 if bit_depth <=8 else np.uint16).reshape((size.width,size.height))

    @staticmethod
    def Abort():
        """Abort camera operation"""
        return SpotCamFunction.QueryStatus(abort=True)


    CameraAttributes = static_property(GetCameraAttributes)
    CameraErrorCode = static_property(GetCameraErrorCode)
    ExposureTimestamp = static_property(GetExposureTimestamp)
    SensorCurrentTemperature = static_property(GetSensorCurrentTemperature)
    SensorExposureTemperature = static_property(GetSensorExposureTemperature)
    VersionInfo = static_property(GetVersionInfo)
    VersionInfo2 = static_property(GetVersionInfo2)
    CameraPresent = static_property(QueryCameraPresent)
    ColorFilterPosition = static_property(QueryColorFilterPosition)
    Status = static_property(QueryStatus)

    del attr, fname, elm

