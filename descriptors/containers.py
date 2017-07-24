# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 10:53:03 2015

@author: polauf
"""

from .utils import ContainerTypes,SequenceTypes
from operator import setitem,delitem,add

append=lambda container,value:container.append(value)
    
clear =lambda container:container.clear()
    
update = lambda s,new:s.update(new)

difference_update = lambda s: s.difference_update(s)

symmetric_difference_update = lambda s: s.symmetric_difference_update(s)

discard = lambda s: s.discard(s)

intersection_update = lambda s: s.intersection_update(s)

remove = lambda s: s.remove(s)

def pop(d,item):
    return d.pop(item)


def resolveIndex(index,iner):
    if iner is not None:
        i=iner+(index,)
    else:
        i=(index,)
    return i

def replaceDefaultContainer(container,descriptor,instance,iner=None):
        if isinstance(container,dict):
            container=_CallDict(container,descriptor,instance,iner)
        elif isinstance(container,list):
            container=_CallList(container,descriptor,instance,iner)
        elif isinstance(container,tuple):
            container=_CallTuple(container,descriptor,instance,iner)
        elif isinstance(container,set):
            container=_CallSet(container,descriptor,instance,iner)
        elif isinstance(container,frozenset):
            container=_CallFrozenSet(container,descriptor,instance,iner)
        return container
    
def initReplaceDefaultContainers(items,descriptor,instance,iner=None):
    if isinstance(items,dict):
        d={}
        for k,v in items.items():
            if isinstance(v,ContainerTypes):
                i=resolveIndex(k,iner)
                d[k]=replaceDefaultContainer(v,descriptor,instance,i)
            else:
                d[k]=v
    elif isinstance(items,SequenceTypes):
        d=[]
        for i,c in enumerate(items):
            if isinstance(c,ContainerTypes):
                index=resolveIndex(i,iner)
                d.append(replaceDefaultContainer(c,descriptor,instance,index))
            else:
                d.append(c)
    else:
        d=items
    return d
    
def replaceDefaultContainers(items,descriptor,instance,iner=None):
    return replaceDefaultContainer(initReplaceDefaultContainers(items,descriptor,instance,iner),descriptor,instance,iner)


class _CallTuple(tuple):
    
    def __new__(cls,items,descriptor,instance,iner=None):
        items=initReplaceDefaultContainers(items,descriptor,instance,iner)
        return tuple.__new__(cls,items) 
        
class _CallSet(set):
    def __new__(cls,items,descriptor,instance,iner=None):
        items=initReplaceDefaultContainers(items,descriptor,instance,iner)
        i=set.__new__(cls,items)
        i.descriptor=descriptor
        i.instance=instance
        i.iner=iner
        return i
        
    def __init__(self,items,descriptor,instance,iner=None):
        set.__init__(self,items)
        
    def clear(self):
        set.clear(self)
        self.descriptor.containerChanged(self.instance,clear,(self.iner,))

    def update(self,items):
        set.update(self,items)
        self.descriptor.containerChanged(self.instance,update,(self.iner,items))

    def difference_update(self,items):
        set.difference_update(self,items)
        self.descriptor.containerChanged(self.instance,difference_update,(self.iner,items))

    def discard(self,item):
        set.discard(self,item)
        self.descriptor.containerChanged(self.instance,discard,(self.iner,item))

    def intersection_update(self,items):
        set.intersection_update(self,items)
        self.descriptor.containerChanged(self.instance,intersection_update,(self.iner,items))
   
    def symmetric_difference_update(self,items):
        set.symmetric_difference_update(self,items)
        self.descriptor.containerChanged(self.instance,symmetric_difference_update,(self.iner,items))

    def remove(self,item):
        set.remove(self,item)
        self.descriptor.containerChanged(self.instance,remove,(self.iner,item))

    def pop(self,item):
        i=set.pop(self,item)
        self.descriptor.containerChanged(self.instance,pop,(self.iner,item))
        return i
        
class _CallFrozenSet(frozenset):
    def __new__(cls,items,descriptor,instance,iner=None):
        items=initReplaceDefaultContainers(items,descriptor,instance,iner)
        return frozenset.__new__(cls,items)   

class _CallList(list):
    
    def __init__(self,items,descriptor,instance,iner=None):
        items=initReplaceDefaultContainers(items,descriptor,instance,iner)
        list.__init__(self,items)
        self.descriptor=descriptor
        self.instance=instance
        self.iner=iner

    def __setitem__(self,index,value):
        iner=resolveIndex(index,self.iner)
        v=replaceDefaultContainers(value,self.descriptor,self.instance,iner)
        list.__setitem__(self,index,v)
        self.descriptor.containerChanged(self.instance,setitem,(iner,value))

    def __delitem__(self,index):
        list.__delitem__(self,index)
        iner=resolveIndex(index,self.iner)
        self.descriptor.containerChanged(self.instance,delitem,iner)

    def append(self,value):
        iner=resolveIndex(len(self),self.iner)
        v=replaceDefaultContainers(value,self.descriptor,self.instance,iner)
        list.append(self,v) 
        self.descriptor.containerChanged(self.instance,append,(self.iner,value))

    def __add__(self,other):
        o=replaceDefaultContainers(other,self.descriptor,self.instance,self.iner)
        list.__add__(self,o)
        self.descriptor.containerChanged(self.instance,add,(self.iner,other))
        
    def clear(self):
        list.clear(self)
        self.descriptor.containerChanged(self.instance,clear,(None,))

    def pop(self,key):
        iner=resolveIndex(-1,self.iner)
        list.pop(self,key)
        self.descriptor.containerChanged(self.instance,pop,(iner,))
        
class _CallDict(dict):
    
    def __init__(self,items,descriptor,instance,iner=None):
        items=initReplaceDefaultContainers(items,descriptor,instance,iner)
        dict.__init__(self,items)
        self.descriptor=descriptor
        self.instance=instance
        self.iner=iner

    def __setitem__(self,key,value):
        k=resolveIndex(key,self.iner)
        v=replaceDefaultContainers(value,self.descriptor,k,self.instance)
        dict.__setitem__(self,key,v)
        self.descriptor.containerChanged(self.instance,setitem,(k,value))

    def __delitem__(self,key):
        dict.__delitem__(self,key)
        key=resolveIndex(key,self.iner)
        self.descriptor.containerChanged(self.instance,delitem,(key,))

    def update(self,values):
        v=replaceDefaultContainers(values,self.descriptor,None,self.instance)
        dict.update(self,v)
        self.descriptor.containerChanged(self.instance,update,(self.iner,values))

    def __add__(self,other):
        o=replaceDefaultContainers(other,self.descriptor,None,self.instance)
        dict.__add__(self,o)
        self.descriptor.containerChanged(self.instance,add,(self.iner,other))
        
    def clear(self):
        dict.clear(self)
        self.descriptor.containerChanged(self.instance,clear,(self.iner,))

    def pop(self,item):
        dict.pop(self,item)
        self.descriptor.containerChanged(self.instance,pop,(self.iner,))
        
class CallNamedTuple:
    
    def __init__(self,names):
        self._values=names
        
        
callbackSequenceTypes={'List':_CallList,'Tuple':_CallTuple,'Dict':_CallDict,'Set':_CallSet,'FrozenSet':_CallFrozenSet}