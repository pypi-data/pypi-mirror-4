#!/usr/bin/python
# -*- coding: utf-8 -*-

__DOC__="""
_XDecoratorWrapper.py

  DecoratorClass used to parse **Kargs and handle Warning and exception thru Missing Attribute by adding
  @_XDecoratorWrapper.Kargs2AttrPreException and creatinf a function having this decorator being called:
  @_XDecoratorWrapper.ObjectClassRaiser( ObjectAttributeHolder , ExceptionClass )


### see the example:

### This example assuming having following module being available  :
### ------------------------------------------------
### from optparse import OptionParser
### import sets
### from sets import Set
### 
### ------------------------------------------------

Generic Exception class model:

We need 2 Class to store attribute:

class ObjectGenericWarningHolder( object ):

  def __init__( self ):
    print "Add Current Object Attribute %s" % self.__class__.__name__

class ObjectGenericAttrHolder( object ):

  def __init__( self ):
    print "Add Current Object Attribute %s" % self.__class__.__name__


We Need a Generic Exception class like this one.


class ExceptionGenericAttrMissing( Exception ):
  
  msg                             ='__GENERIC_EXCEPTION_MESSAGES__'
  AttrCurrentExceptionHandled     = None
  HadDecoderTypeList              = False 

  def __Init__Attr( self , value ):
    self.AttrCurrentExceptionHandled = value
    DictListTemplateKey="%sList" % ( value )
    IsListTemplateKey="Had%sList" % ( value )
    if hasattr( self, IsListTemplateKey  ):
      if getattr( self, IsListTemplateKey ) == True:
        Exception.__init__( self, self.MsgDict[DictListTemplateKey] % ( self.AttrCurrentExceptionHandled ,
                                                                        getattr( self, DictListTemplateKey ) ) )
      else:
        Exception.__init__( self, self.MsgDict[self.AttrCurrentExceptionHandled]  % ( self.AttrCurrentExceptionHandled ) )
    

  @_XDecoratorWrapper.Kargs2Attr( ObjectWarningHolder )
  def __init__( self, **Kargs ):
    if hasattr( self, 'ListAttrFuncAccess' ):
      print "Available message for following Attr:[ %s ]" % ( self.ListAttrFuncAccess ) 
    self.RaisedExceptionByAttr = False
    for ExceptionByAttr in self.ListAttrFuncAccess:
      if hasattr( self, ExceptionByAttr ):
        self.RaisedExceptionByAttr = True
        getattr( self, "__Init__Attr")( ExceptionByAttr )


Main class:

class GenericTest( object ):

  MsgDict = {
    'AppsName'        :'Internal Value AppsName not used, You should at least Specified an AppsName Value.',
    'ActionHelper'    :'Internal Value ActionHelper not used, You should at least Specified an ActionHelper Value.',
    'HelperSwitch'    :'Internal Value HelperSwitch not used, You should at least Specified an HelperSwitch Value.',
  }  

  OptionListDiscovery=list()
  TempOptionList=list()
  ErrorHandler = iterpipes.CalledProcessError

  ListAttrFuncAccess        = [ 'AppsName', 'ActionHelper', 'HelperSwitch' ]
  parser = OptionParser()

  def __start_cmdline_parser__( self ):
    
    self.parser.add_option("-A", "--AppsName",
                      dest="StrAppsName",
                      help="Add AppsName in your Class")
    self.parser.add_option("-J", "--ActionHelper",
                      dest="StrActionHelper",
                      help="Add ActionHelper in your Class")
    self.parser.add_option("-S", "--HelperSwitch",
                      dest="StrHelperSwitch",
                      help="Add HelperSwitch in your Class ")


  @_XDecoratorWrapper.Kargs2AttrPreException( ObjectIterAppsFilter )
  def __init__( self , **Kargs ):
    self.__start_cmdline_parser__()
    (self.options, self.args ) = self.parser.parse_args() 
    self.ErrorRaiser( )
### ...


  @_XDecoratorWrapper.ObjectClassRaiser( ObjectGenericAttrHolder , ExceptionGenericAttrMissing )
  def ErrorRaiser( self ):
    print "Inspecting Missing Attribute."



### Some Instantiation statement:

if __name__.__eq__( '__main__' ):
  _XDecoratorWrapper.ErrorClassReceivedAttrListName = 'ListAttrFuncAccess'
  ExceptionGenericAttrMissing.ListAttrFuncAccess    = ItertAppsFilter.ListAttrFuncAccess
  ExceptionGenericAttrMissing.MsgDict               = ItertAppsFilter.MsgDict

And We have Correct basic model of Attribute filtering thru the **kargs and will raise any Warning or exception
upon definition of your class inside the Object Raiser inside _XDecoratorWrapper :
--------
@_XDecoratorWrapper.ObjectClassRaiser( __ANY_EXCEPTION_OR_WARNING_OBJECT__ , ExceptionGenericAttrMissing )
def ErrorRaiser( self ):
 pass 
--------
"""

import sys,   os,       re,   cStringIO
import time,  datetime

import iterpipes
try:
  from iterpipes import cmd, bincmd, linecmd, run, call, check_call, cmdformat, compose
except ImportError:
  #print "Warning cmdformat not compatible or can not be loaded properly .\nLoading cmd, bincmd, linecmd, run, call, check_call, compose.\n"
  from iterpipes import cmd, bincmd, linecmd, run, call, check_call, compose
  
try:
  getcontext().prec = 36
except NameError:
  import decimal
  from decimal import *
  getcontext().prec = 36

try:
  ThisSetTest=Set(['1','2','3'])
except NameError:
  import sets
  from sets import Set
  #print "Warning Decorator Error Raiser need some default import like sets and sets.Set.\nTest simply failed. importing manually"


class _XDecoratorWrapper( ):

  DisplayKargs2AttrItemAdded      = False
  DictAttrRefferal                = 'DictAttrAdd'
  DictAttrRefferalType            = list
  DictAttrRefferalAdd             = 'append'
  ErrorClassReceivedAttrList      = None
  ErrorClassReceivedAttrListName  = None
  

  @staticmethod
  def Kargs2AttrPreException( ClassTinyDecl ):
    ### Warning, should not use this one inside an Class Exception as long you did
    ### not define any Attr - receiver topoly or it will depend of some other 
    ### holder. Previous one Decorator -> Kargs2Attr is the plain initial one
    ### which is feeding the Initial object of Attribute value and will not
    ### create a list inside the ErrorObject for a later uses of it by
    ### creating a Set([ master list option]).difference( Set([current option parsed from Instance
    ### declaration ]) ) .
    ### Assumming Kargs2AttrPreException and ObjectClassRaiser are communicative.
    
    """
    This Decorator Will:
     Read the *args key but do not consume it or affect any variable at this times . 
     Reaf **kwargs key and add it to current Object-class ClassTinyDecl under current
     name readed from **kwargs key name. 
            
    """
    def decorator( func ):
        def inner( *args ,**kwargs):
          ### Create A List with all Attr Added
          AttrContainer=getattr( AttributeGenerationDecor, 'DictAttrRefferalType' )( )
          setattr( ClassTinyDecl,
                   AttributeGenerationDecor.DictAttrRefferal ,
                   AttrContainer  )
          for ItemName in kwargs.keys():
            if AttributeGenerationDecor.DisplayKargs2AttrItemAdded == True :
              print "Processing Key, value : < %s, \"%s\" >" % ( ItemName, kwargs[ItemName] )
            setattr( ClassTinyDecl,
                     ItemName ,
                     kwargs[ItemName] )
            getattr( getattr( ClassTinyDecl,
                              AttributeGenerationDecor.DictAttrRefferal ),
                     AttributeGenerationDecor.DictAttrRefferalAdd )( ItemName )
          func( *args ,**kwargs )
        return inner
    return decorator
  
  
  @staticmethod
  def Kargs2Attr( ClassTinyDecl ):
    """
    This Decorator Will:
     Read the *args key but do not consume it or affect any variable at this times . 
     Reaf **kwargs key and add it to current Object-class ClassTinyDecl under current
     name readed from **kwargs key name. 
            
    """
    def decorator( func ):
        def inner( *args ,**kwargs ):
          for ItemName in kwargs.keys():
            if AttributeGenerationDecor.DisplayKargs2AttrItemAdded == True :
              print "Processing Key %s, Value: %s" % ( ItemName, kwargs[ItemName] )
            setattr( ClassTinyDecl, ItemName , kwargs[ItemName] )
          func( *args ,**kwargs )
        return inner
    return decorator

  @staticmethod
  def LoopClassFunc( TransportClass, MainClass, FuncList ):
    """
    This Decorator Will:
     Read the *args key but do not consume it or affect any variable at this times . 
     Reaf **kwargs key and add it to current Object-class ClassTinyDecl under current
     name readed from **kwargs key name. 
            
    """
    def decorator( func ):
        def inner( ):
          for FuncNameExec in getattr( TransportClass, FuncList ):
            getattr( eval( MainClass ) , FuncNameExec )( )
          func( )
        return inner
    return decorator

  @staticmethod
  def ObjectClassRaiser( ClassTinyDecl, ErrorClass ):
    """
    This Decorator Will:
     Read the *args key but do not consume it or affect any variable at this times . 
     Reaf **kwargs key and add it to current Object-class ClassTinyDecl under current
     name readed from **kwargs key name. 
            
    """
    def decorator( func ):
        def inner( *args ):
          func( *args )
          AttrSetListParsed=Set( getattr( ClassTinyDecl, AttributeGenerationDecor.DictAttrRefferal )  )
          AttrSetMainList=Set( getattr( ErrorClass, AttributeGenerationDecor.ErrorClassReceivedAttrListName ) )
          MissingAttrSet=AttrSetMainList.difference( AttrSetListParsed )
          try:
            AttrRaiseName = MissingAttrSet.pop()
            raise ErrorClass( AttrRaiseName )
          except KeyError:
            pass
         
        return inner
    return decorator


class ObjectGenericWarningHolder( object ):

  def __init__( self ):
    print "Add Current Object Attribute %s" % self.__class__.__name__

class ObjectGenericAttrHolder( object ):

  def __init__( self ):
    print "Add Current Object Attribute %s" % self.__class__.__name__


class ExceptionGenericAttrMissing( Exception ):
  
  msg                             ='__GENERIC_EXCEPTION_MESSAGES__'
  AttrCurrentExceptionHandled     = None
  HadDecoderTypeList              = False 

  def __Init__Attr( self , value ):
    self.AttrCurrentExceptionHandled = value
    DictListTemplateKey="%sList" % ( value )
    IsListTemplateKey="Had%sList" % ( value )
    if hasattr( self, IsListTemplateKey  ):
      if getattr( self, IsListTemplateKey ) == True:
        Exception.__init__( self, self.MsgDict[DictListTemplateKey] % ( self.AttrCurrentExceptionHandled ,
                                                                        getattr( self, DictListTemplateKey ) ) )
      else:
        Exception.__init__( self, self.MsgDict[self.AttrCurrentExceptionHandled]  % ( self.AttrCurrentExceptionHandled ) )
    

  @_XDecoratorWrapper.Kargs2Attr( ObjectGenericWarningHolder )
  def __init__( self, **Kargs ):
    if hasattr( self, 'ListAttrFuncAccess' ):
      print "Available message for following Attr:[ %s ]" % ( self.ListAttrFuncAccess ) 
    self.RaisedExceptionByAttr = False
    for ExceptionByAttr in self.ListAttrFuncAccess:
      if hasattr( self, ExceptionByAttr ):
        self.RaisedExceptionByAttr = True
        getattr( self, "__Init__Attr")( ExceptionByAttr )


