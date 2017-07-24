# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 10:51:59 2015

@author: polauf
"""
import os
SequenceTypes = (list, tuple, set, frozenset)
ContainerTypes= SequenceTypes + (dict,)

basicTypes={'Bool':bool,'Int':int,'Float':float,'Unicode':str,'Bytes':bytes}
basicSequenceTypes={'List':list,'Dict':dict,'Tuple':tuple,'FrozenSet':frozenset,'Set':set}



def parseFile(file):
    path,name=os.path.split(os.path.abspath(file))
    name,ext=os.path.splitext(name)
    return path,name,ext
    
def joinFile(*pathNameExt):
    if len(pathNameExt)==3:
        return os.path.join(pathNameExt[0],pathNameExt[1])+pathNameExt[2]
    elif len(pathNameExt)==2:
        return pathNameExt[0]+pathNameExt[1]
        