# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 13:03:16 2015

@author: polauf
"""

import os
from .basic import CallUnicode,InvalidDescriptor,DescriptorError

class Path(CallUnicode):
    
    def __init__(self,path,create=False,**propeties):
        self.create=create
        super().__init__(path,**propeties)
    
    
    def validate(self,path):
        if path is not None:
            path=os.path.abspath(path)
            if not os.path.exists(path) and not self.create:
                raise InvalidDescriptor('Path "%s" not exist at descriptor "%s"'%(
                                        path.decode('utf-8'),self.name))
            elif self.create and self.name is not None:
                try:
                    os.makedirs(path)
                    return path
                except PermissionError as e:
                    raise DescriptorError('Path "%s" Encoured error: [%s] %s.'%(path.decode('utf-8'),e.errno,e.strerror))
            else:
                return path
            
                                    
    def instanceInit(self,instance):
        super().instanceInit(instance)
        self.validate(self.value)
                                    
                                    
class File(Path):
    
    def validate(self,path):
        if path is not None:
            path=os.path.abspath(path)
            try:
                os.utime(path, None)
                return path
            except:
                if self.create and self.name is not None:
                    open(path, 'a').close()
                    return path
                else:
                    raise InvalidDescriptor('Path "%s" not exist at descriptor "%s"'%(
                                        path.decode('utf-8'),self.name))       