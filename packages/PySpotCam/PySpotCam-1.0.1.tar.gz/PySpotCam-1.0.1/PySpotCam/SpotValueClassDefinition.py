import numpy as np
import SpotCamFunction

from ctypes import *

class ValueType(object):
    """ Base type for the conversion between ctypes and python"""
    pass

class CTypeValue(ValueType):
    def _ctype_to_python(self, val):
        return val.value
    def _python_to_ctype(self, value):
        return self._ctype(value)

class StructureSpotValue(ValueType):
    def _ctype_to_python(self, val):
        return val
    def _python_to_ctype(self,value):
        if isinstance(value, self._ctype): return value
        if isinstance(value, dict):
            out = (self._ctype)()
            for key,val in value.iteritems():
                setattr(out, key,val)
            return val
        raise ValueError('Invalid input for %s'%type(self).__name__)
    def __str__(self):
        "%s ctype structure. Input is either a %s ctype structure or a dictionnary"%(self._ctype, self._ctype)


class EnumSpotValue(ValueType):
    """Conversion for enum type

    Require an _enum_class attribute
    """
    def _ctype_to_python(self, val):
        return self._enum_class(val.value)
    def _python_to_ctype(self, value):
        try:
            value = self._enum_class(value)
        except:
            pass
        if value == self._enum_class(int(value)):
            return (self._ctype)(int(value))
        raise ValueError('Invalid input for %s'%type(self).__name__)
    def __str__(self):
        "Input/Output is \n %s"%self._enum_class            

class NamedTupleSpotValue(ValueType):
    """Conversion for namedtuple

    Require an _tuple_class attribute
    """
    def _ctype_to_python(self, val):
        return self._tuple_class(*(val[:]))
    def _python_to_ctype(self, value):
        if isinstance(value, dict):
            value = self._tuple_class(**value)
        return (self._ctype)(*value)
    def __str__(self):
        "Input/Output is \n %s"%self._tuple_class

class ArraySpotValue(ValueType):
    """Conversion for array

    Require a _dtype attribute. Works only to get value
    """
    def _ctype_to_python(self, val):
        length = val[0]
        return np.array(val[1:length+1], dtype = self._dtype)










class SpotFunctionMetaclass(type):
    def __new__(cls, name, bases, dct):
        if not dct.has_key('__doc__'):
            dct['__doc__'] = ""
        doc = dct['__doc__']
        doc = doc.replace('\n','').replace('  ',' ')
        doc +='\n'
        dct['__doc__'] = doc
        if EnumSpotValue in bases:
            if not dct.has_key('_enum_class'): 
                raise Exception('EnumSpotValue instance should have a _enum_class attribute defined')
            dct['__doc__'] += "\nProperty value is an Enum: %s"%dct['_enum_class']
        if NamedTupleSpotValue in bases:
            if not dct.has_key('_tuple_class'):
                raise Exception('NamedTupleSpotValue instance should have a _tuple_class attribute defined')
            dct['__doc__'] += "\nProperty value is a namedtuple: %s"%dct['_tuple_class'].__doc__
        if ArraySpotValue in bases:
            if not dct.has_key('_dtype'):
                raise Exception('ArraySpotValue instance should have a _dtype attribute defined')
            dct['__doc__'] += "\nProperty value is a numpy array of type %s."%dct['_dtype'].__name__
        if CTypeValue in bases:
            if not dct.has_key('_ctype'):
                raise Exception('CTypeValue instance should have a _c_type attribute defined')            
            dct['__doc__'] += "\nProperty value is a %s"%type(dct['_ctype']().value).__name__
        if StructureSpotValue in bases:
            if not dct.has_key('_ctype'):
                raise Exception('StructureSpotValue instance should have a _c_type attribute defined')            
            dct['__doc__'] += "\nProperty value is a structure or union : %s%s"%(dct['_ctype'].__name__,dct['_ctype']._fields_)
        try:
            if GetSetSpotValue in bases:
                dct['__doc__'] = dct['__doc__'].replace('Property','In/out Property. Property')
            elif GetSpotValue in bases:
                dct['__doc__'] = dct['__doc__'].replace('Property','Output Property. Property')    
            else:
                pass
        except NameError:
            pass
        return super(SpotFunctionMetaclass, cls).__new__(cls, name, bases, dct)

class SpotFunction(object):
    __metaclass__= SpotFunctionMetaclass
    def __get__(self, obj, objtype=None):
        if obj is None : return self
        raise AttributeError, "unreadable attribute"

    def __set__(self, obj, value):
        raise AttributeError, "can't set attribute"

    def __delete__(self, obj):
        raise AttributeError, "can't delete attribute"

class GetSpotValue(SpotFunction):
    """Property used to retrieve the values of the various parameters and camera values"""
    def get(self):
        pValue = (self._ctype)()
        SpotCamFunction.GetValue(self._nParam, byref(pValue))
        return self._ctype_to_python(pValue)
    def __get__(self, inst, own):
        if inst is None : return self
        return self.get()

class SetSpotValue(SpotFunction):
    """Property used to set the values of the various parameters and camera values"""
    def set(self, value):
        pValue = self._python_to_ctype(value)
        SpotCamFunction.SetValue(self._nParam, byref(pValue))
    def __set__(self, inst, val):
        self.set(val)

class GetSetSpotValue(GetSpotValue, SetSpotValue):
    """Property used to set or retrive the values of the various parameters and camera values"""
    pass







