# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 11:10:34 2015

@author: polauf
"""
from collections import OrderedDict
from .basic import BaseDescriptor,BaseCallbackDescriptor,BorgDescriptor


class DMeta(type):
    
    @classmethod
    def __prepare__(cls,name,bases):
        return OrderedDict()

    def __new__(cls, name, bases, ns):
		#Borg namespace
        ns['_borgDescriptors']={}
        ns['_descriptorOrder']=[]

		#link descriptors from baseclasses if it's start with _ do not copy
        for b  in bases:
            if '_descriptorOrder' in b.__dict__:
                for n in b.__dict__['_descriptorOrder']:
                    attr=b.__dict__[n]
                    if isinstance(attr, BaseDescriptor) and not n.startswith('_') and n not in ns:
                        ns[n]=attr

        #add name in namespace for descriptors (ordered)           
        for n, attr in ns.items():
            if isinstance(attr, BaseDescriptor):
                attr.name = n
                ns['_descriptorOrder'].append(n)
        ns=dict(ns)
        return type.__new__(cls, name, bases, ns)

        
class DClass(metaclass=DMeta):
    

    
    def __new__(cls,*args,callbacksEnabled=True,**kw):
        inst=super().__new__(cls)   
        inst.__dict__['_descriptors']={}
        
		#any function is in dict?
        allchange=None
        if '_any_changed' in cls.__dict__:
            allchange=True
        
		#instance init for desriptors 
        for name in cls. _descriptorOrder:
            attr=cls.__dict__[name]
            if isinstance(attr,BaseDescriptor) and not (isinstance(attr,BorgDescriptor) and name in cls._borgDescriptors):
                attr.instanceInit(inst)
                
	    	#add static callbacks and anychange
            if isinstance(attr, BaseCallbackDescriptor):
                call='_%s_changed'%(attr.name)
                if call in cls.__dict__:
                    attr.addCallback(inst,getattr(inst,call))
                if allchange is not None:
                    attr.addCallback(inst,getattr(inst,'_any_changed'))
                    
        return inst
    
    def DaddCallback(self,*descriptors,callback=None):
        for descriptor in descriptors:
            if isinstance(self.__class__.__dict__[descriptor],BaseCallbackDescriptor):
                self.__class__.__dict__[descriptor].addCallback(self,callback)
            else:
                raise AttributeError("Descriptor %s %s has no ability of callback."%(
                                    self.__class__.__dict__[descriptor].name,self.__class__.__dict__[descriptor]))
                                
    def DdelCallback(self,*descriptors,callback=None):
        for descriptor in descriptors:
            if not isinstance(self.__class__.__dict__[descriptor],BaseCallbackDescriptor):
                raise AttributeError("Descriptor %s %s has no ability of callback."%(
                                    self.__class__.__dict__[descriptor].name,self.__class__.__dict__[descriptor]))
                               
            self.__class__.__dict__[descriptor].delCallback(self,callback)
    
    
    def DenableCallback(self,*descriptors,enabled=True):
        for descriptor in descriptors:
            if not isinstance(self.__class__.__dict__[descriptor],BaseCallbackDescriptor):
                raise AttributeError("Descriptor %s %s has no ability of callback."%(
                                    self.__class__.__dict__[descriptor].name,self.__class__.__dict__[descriptor]))
                                
            self.__class__.__dict__[descriptor].enableCallback(self,enabled)      
    
    def Dhelp(self,*descriptors):
        h=[]
        for descriptor in descriptors:
            h.append(self.__class__.__dict__[descriptor].help())
        return '\n'.join(h)
        
        
    def Descriptors(self,*descriptors):
        if descriptors[0]=='*':
            for name in  self.__class__. _descriptorOrder:
                attr=self.__class__.__dict__[name]
                if isinstance(attr,BaseDescriptor):
                    yield name,attr
        else:
            for name in descriptors:
                attr=self.__class__.__dict__[name]
                if isinstance(attr,BaseDescriptor):
                    yield name,attr
                    
    def Descriptor(self,name):
        attr=self.__class__.__dict__[name]
        if isinstance(attr,BaseDescriptor):
           return attr        

        