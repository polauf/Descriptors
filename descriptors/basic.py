# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 10:49:55 2015

@author: polauf
"""
from .containers import callbackSequenceTypes,_CallDict
from .utils import SequenceTypes,basicTypes,basicSequenceTypes
from .exceptions import DescriptorError,InvalidDescriptor



class BaseDescriptor:
    "Base class of all descriptors"
    _path=lambda self,instance,name: instance.__dict__['_descriptors'][name]
    
    def __init__(self,default=None,**properties):
        self.name=None
        self.value=default
        self.properties=properties
        
    
    
    def __get__(self,instance,type=None):            
        return self._path(instance,self.name)['value']
            
            
    def __set__(self,instance,value):
        self._path(instance,self.name)['value']=value
        
    def instanceInit(self,instance):
        instance.__dict__['_descriptors'][self.name]={'properties':self.properties}
                                            
    def help(self):
        if 'help' in self.properties:
            return 'Descriptor %s: %s (%s)'%(self.name,self.properties['help'],self.__doc__)
        else:
            return 'Descriptor %s: <%s> (%s)'%(self.name,self.__class__.__name__,self.__doc__)
                                            
class BorgDescriptor(BaseDescriptor):
    """
    Shared value descriptor by all instances
    """
    
    _path=lambda self,instance,name: instance.__class__.__dict__['_borgDescriptors'][name]
         
    def instanceInit(self,instance):
        instance.__class__.__dict__['_borgDescriptors'][self.name]={'properties':self.properties}
        super().instanceInit(instance)
                    
                    
class ValidDescriptor(BaseDescriptor):
    "Descriptor have validate functio, it should return validated value or raise IvalidDescriptorError"
    
    def __init__(self,default=None,**properties):
        BaseDescriptor.__init__(self,default,**properties)
        self.value=self.validate(self.value)
    
            
    def validate(self,value):
            return value
        
    def __set__(self,instance,value):
        self._path(instance,self.name)['value']=self.validate(value)
        
    def instanceInit(self,instance):
        super().instanceInit(instance)
        self._path(instance,self.name)['value']=self.validate(self.value)
        
        
class Enum(ValidDescriptor):

    def __init__(self,default=None,values=(),**properties):
        self.values=tuple(values)
        BaseDescriptor.__init__(self,default,**properties)
    
    def validate(self,value):
        if (value not in self.values) or isinstance(value,SequenceTypes):
            raise InvalidDescriptor('Invalid value "%s" in Descriptor %s %s. Possible values are: %s.'%(
                                    value,self.name,type(self),self.values))
        else:
            return value


                                    
class CaselessEnum(Enum):
    
    
    def __init__(self,default=None,values=(),**properties):
        self.values=tuple(a.lower() if isinstance(a,str) else a for a in values)
        BaseDescriptor.__init__(self,default,**properties)
    
    def validate(self,value):
        v = value.lower() if isinstance(value,str) else value
        Enum.validate(self,v)
        return value
        
      
                                    
                                    
class ValidKlassDescriptor(ValidDescriptor):
    _klass=type
    
    def validate(self,value):
        if not isinstance(value,self._klass):
            raise InvalidDescriptor("Can't assign %s %s to \"%s\", use type %s."%(
                                    value,type(value),self.name,self._klass))
        return value
        
class ValidCastedKlassDescriptor(ValidKlassDescriptor):
    
    def validate(self,value):
        if not isinstance(value,self._klass):
            value=self._klass(value)
        return value
        


class ValidKlassMinMaxDescriptor(ValidKlassDescriptor):
    
    def __init__(self,default=None,min=0,max=255,**properties):
        properties['max']=self._klass(max)
        properties['min']=self._klass(min)
        super().__init__(default,**properties)
    
    def validate(self,value):
        if (not isinstance(value,self._klass)) or (value<self.properties['min']) or (value>self.properties['max']):
            raise InvalidDescriptor("Can't assign %s %s to \"%s\", use type %s in bounderies <%s,%s>."%(
                                    value,type(value),self.name,self._klass,self.properties['min'],self.properties['max']))
        return value
        


class ValidCastedKlassMinMaxDescriptor(ValidKlassMinMaxDescriptor):
    
    def validate(self,value):
        v=value
        if not isinstance(value,self._klass):
            value=self._klass(value)        
        if (value<self._min) or (value>self._max):
            raise InvalidDescriptor("Can't assign %s %s to \"%s\", the bounderies are <%s,%s>."%(
                                    v,type(v),self.name,self.properties['min'],self.properties['max']))
        return value

class BaseCallbackDescriptor(BaseDescriptor):
    

    def addCallback(self,instance,callback):
        if callable(callback):
            self._path(instance,self.name)['callbacks'].add(callback)
        else:
            raise DescriptorError("Can't assign callback to \"%s\", %s %s is not callable"%(
                                    self.name,callback,type(callback)))
                                    
    def delCallback(self,instance,callback):
        self._path(instance,self.name)['callbacks'].remove(callback)
        
    def enableCallback(self,instance,value):
        self._path(instance,self.name)['callbacksEnabled']=bool(value)
        
    def instanceInit(self,instance):
        BaseDescriptor.instanceInit(self,instance)
        self._path(instance,self.name)['callbacks']=set()
        self._path(instance,self.name)['callbacksEnabled']=True

class CallbackDescriptor(BaseCallbackDescriptor): 

    def instanceInit(self,instance):
        super().instanceInit(instance)
        self._path(instance,self.name)['value']=self.value
        
    def __set__(self,instance,value):
        old=self._path(instance,self.name)['value']
        super().__set__(instance,value)
        if self._path(instance,self.name)['callbacksEnabled']:
            for c in self._path(instance,self.name)['callbacks']:
                c(self.name,old,value)
#END
                
#GENERATE useful combiantions
class Any(BaseDescriptor):

    def instanceInit(self,instance):
        super().instanceInit(instance)
        self._path(instance,self.name)['value']=self.value
        
CallAny=CallbackDescriptor

class SequenceDescriptor(BaseDescriptor):  
    
    def instanceInit(self,instance):
        super().instanceInit(instance)
        if self.value is not None:
            self._path(instance,self.name)['value']=self._klass(self.value)
        else:
            self._path(instance,self.name)['value']=self._klass()
        
        

class CallSequenceDescriptor(BaseCallbackDescriptor,SequenceDescriptor):
    _klass=None
    
    def instanceInit(self,instance):
        BaseCallbackDescriptor.instanceInit(self,instance)
        self.value=self._klass(self.value,self,instance)
        self._path(instance,self.name)['value']=self.value
        
    
    def __set__(self,instance,value):
        old=self._path(instance,self.name)['value']
        self._path(instance,self.name)['value']=self._klass(value,self,instance)
        if self._path(instance,self.name)['callbacksEnabled']:
            for c in self._path(instance,self.name)['callbacks']:
                c(self.name,old,value)
        
        
    def containerChanged(self,instance,operator,change):
        if self._path(instance,self.name)['callbacksEnabled']:
            for c in self._path(instance,self.name)['callbacks']:
                c(self.name,operator,change)  
                
                
for name,klass in basicTypes.items():
    locals()[name]=type(name,(ValidKlassDescriptor,),{'_klass':klass})
    locals()['B'+name]=type('B'+name,(BorgDescriptor,ValidKlassDescriptor),{'_klass':klass})
    locals()['C'+name]=type('C'+name,(ValidCastedKlassDescriptor,),{'_klass':klass})
    locals()['BC'+name]=type('BC'+name,(BorgDescriptor,ValidCastedKlassDescriptor),{'_klass':klass})
    locals()['M'+name]=type('M'+name,(ValidKlassMinMaxDescriptor,),{'_klass':klass})
    locals()['BM'+name]=type('B'+name,(BorgDescriptor,ValidKlassMinMaxDescriptor),{'_klass':klass})
    locals()['CM'+name]=type('CM'+name,(ValidCastedKlassMinMaxDescriptor,),{'_klass':klass})
    locals()['BCM'+name]=type('B'+name,(BorgDescriptor,ValidCastedKlassMinMaxDescriptor),{'_klass':klass})
    locals()['Call'+name]=type('Call'+name,(CallbackDescriptor,ValidKlassDescriptor),{'_klass':klass})
    locals()['CallC'+name]=type('CallC'+name,(CallbackDescriptor,ValidCastedKlassDescriptor),{'_klass':klass}) 
    locals()['CallM'+name]=type('CallM'+name,(CallbackDescriptor,ValidKlassMinMaxDescriptor),{'_klass':klass})       
    locals()['CallCM'+name]=type('CallCM'+name,(CallbackDescriptor,ValidCastedKlassMinMaxDescriptor),{'_klass':klass})       
    locals()['CallB'+name]=type('CallB'+name,(BorgDescriptor,CallbackDescriptor,ValidKlassDescriptor),{'_klass':klass})
    locals()['CallBC'+name]=type('CallBC'+name,(BorgDescriptor,CallbackDescriptor,ValidCastedKlassDescriptor),{'_klass':klass}) 
    locals()['CallBM'+name]=type('CallBM'+name,(BorgDescriptor,CallbackDescriptor,ValidKlassMinMaxDescriptor),{'_klass':klass})       
    locals()['CallBCM'+name]=type('CallBCM'+name,(BorgDescriptor,CallbackDescriptor,ValidCastedKlassMinMaxDescriptor),{'_klass':klass})       

class Char(ValidKlassDescriptor):
    
    def validate(self,value):
        if not isinstance(value, (str,bytes)) or len(value)!=1:
            raise InvalidDescriptor("Can't assign %s %s to \"%s\", use type %s with length 1."%(
                                    value,type(value),self.name,str))
        return value[0]

class CallChar(Char,CallbackDescriptor): pass
class BChar(BorgDescriptor,Char): pass
class CallBChar(BChar,CallbackDescriptor): pass
    
class CallEnum(CallbackDescriptor,Enum):pass
class CallCaselessEnum(CallbackDescriptor,CaselessEnum): pass
class BEnum(Enum,BorgDescriptor):pass
class CallBEnum(BEnum,CallbackDescriptor):pass
class BCaselessEnum(CaselessEnum,BorgDescriptor): pass
class CallBCaselessEnum(BCaselessEnum,CallbackDescriptor): pass
    
    
for name,klass in basicSequenceTypes.items():
    locals()[name]=type(name,(SequenceDescriptor,),{'_klass':klass})
    locals()['B'+name]=type('B'+name,(BorgDescriptor,SequenceDescriptor),{'_klass':klass})

for name,klass in callbackSequenceTypes.items():
    locals()['Call'+name]=type('Call'+name,(CallSequenceDescriptor,),{'_klass':klass})
    locals()['CallB'+name]=type('CallB'+name,(BorgDescriptor,CallSequenceDescriptor,),{'_klass':klass})

                
                
                

                
                

