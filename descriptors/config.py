# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:52:50 2015

@author: polauf
"""
import json,csv,os
from collections import OrderedDict
from inspect import getfile

from .basicClasses import DClass
from .basic import Unicode,BorgDescriptor
from .utils import parseFile,joinFile


class Configurable(DClass):
    
    #Default configfile name (same as file but .json)    
    configFile=Unicode('')
    name=Unicode('')
    
    config=OrderedDict()
    
    def __new__(cls,*args,**kw):
        try:
            cls.__dict__['configFile'].value=getfile(cls).split('.')[0]+'.json'
        except TypeError:
            cls.__dict__['configFile'].value=os.path.join(os.getcwd(),cls.__name__+'.json')
        return super().__new__(cls,*args,**kw)
    
    def load(self,file=None):
        if  file is not None:
            self.configFile=joinFile(*parseFile(file))
        elif not os.path.isfile(self.configFile):
            return False            
        path,name,ext=parseFile(self.configFile)
        if ext=='.json':
            try:
                self.config=json.load(open(self.configFile,'r'))[self.name or self.__class__.__name__]
            except (KeyError,ValueError,FileNotFoundError):
                pass
        if ext=='.csv':
            with open(self.configFile,'r') as fh:
                self.config=json.loads(fh.readline())
        self.loadConfig()
        return True
            
    def toConfig(self):
        self.config=OrderedDict()
        for name in self.__class__._descriptorOrder:
            attr=self.__class__.__dict__[name]
            if 'config' in attr.properties:
                self.config[name]=getattr(self,name)        
            
    def save(self,file=None):
        self.toConfig()
        if file is None:
            file=self.configFile
        ext=parseFile(file)[2]
        if '.json'==ext:
            try:
                prev=json.load(open(self.configFile,'r'))
            except (ValueError,FileNotFoundError):
                prev={}
            prev.update({self.name or self.__class__.__name__:self.config})
            json.dump(prev,open(file,'w'),indent=4)
        return True            
        
            
    def loadConfig(self,d=None):
        if d is None: d=self.config
        for name,attr in self.Descriptors('*'):
            if 'config' in attr.properties and name in d and 'loaded' not in attr.properties:
                setattr(self,name,d[name])
                if isinstance(attr,BorgDescriptor):
                    attr.properties['loaded']=True
        
    