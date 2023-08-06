#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Embedded DSL implementation.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import threading
import re


##x |__enter__| that can be used with any class.
def enter( self ) :
  ##  Save current value of |pd.o| so |__exit__()| can restore it. This
  ##  is required to correctly handle hierarchical DSL construction.
  self.__dict__[ '__pyedsl_context' ] = pd.o
  pd.o = self
  return self


##x |__enter__| that can be used with any class.
def exit( self, * l_args ) :
  pd.o = self.__dict__[ '__pyedsl_context' ]
  if isinstance( self, Item ) :
    if self._Item__oPyedslParent is not None :
      ##  User defined adder.
      if hasattr( self._Item__oPyedslParent, 'dadd' ) :
        self._Item__oPyedslParent.dadd( self )
      ##  Build-in adder that maintain tree for lookup.
      self._Item__oPyedslParent._Item__pyedslAdd( self )


class Item( object ) :


  def __init__( self,
    ##i DSL item name. Used to lookup child item from parent item.
    s_name = None,
    ##i DSL item parent:
    ##  . |None| to define top level DSL item.
    ##  . 'auto' to implicitly use `current` parent stored in
    ##    thread-local |pd.o|. This allows to write nested |with|
    ##    statements without explicitly defining parents for each item.
    ##  . |pd.Item| subclass to continue DSL construction from existing
    ##    parent. Allows to define top level item as standalone class and
    ##    construct child DSL hierarchy in constructor.
    o_parent = 'auto'
  ) :
    if isinstance( o_parent, basestring ) and 'auto' == o_parent :
      assert pd.o is not None, "Auto parent top level item."
      self.__oPyedslParent = pd.o
    else :
      assert o_parent is None or isinstance( o_parent, Item ), "Wrong parent."
      self.__oPyedslParent = o_parent
    if s_name is not None :
      assert isinstance( s_name, basestring )
      self.__sName = s_name
    else :
      self.__sName = self.__class__.__name__.lower()
    self.__lChildren = []

  def __enter__( self ) :
    return enter( self )

  def __exit__( self, * l_args ) :
    return exit( self, * l_args )


  @property
  ##x Shortage from "Dsl Parent". Not named "parent" since it will conflict
  ##  with |Tkinter| "parent" method.
  def dparent( self ) :
    return self.__oPyedslParent


  ##x Shortage from "Dsl Name". Not named "name" since it will conflict
  ##  with something for sure.
  @property
  def dname( self ) :
    return self.__sName


  ##x Shortage from "Dsl Children". Not named "children" since it will
  ##  conflict with something for sure.
  ##  Used in cases like building XML where gathering results from DSL
  ##  starts at root.
  @property
  def dchildren( self ) :
    return self.__lChildren


  ##x Search children for item with {i name} and evalute to it or |None|.
  def o( self, s_name ) :
    for oChild in self.__lChildren :
      if oChild.dname == s_name :
        return oChild
    for oChild in self.__lChildren :
      oItem = oChild.o( s_name )
      if oItem is not None :
        return oItem
    return None


  ##x "DSL Add", name to prevent conflicts.
  def __pyedslAdd( self, o_child ) :
    self.__lChildren.append( o_child )


class RegexpMatch( object ) :


  def __init__( self, o_match ) :
    self.__oMatch = o_match


  @property
  def string( self ) :
    return self.__oMatch.string


  @property
  def first( self ) :
    lGroups = self.__oMatch.groups()
    if len( lGroups ) :
      return lGroups[ 0 ]
    else :
      return None


  def __getitem__( self, s_key ) :
    if isinstance( s_key, int ) :
      return self.__oMatch.groups()( s_key )
    if isinstance( s_key, basestring ) :
      return self.__oMatch.groupdict()( s_key )
    assert False, "Unknown key type."


class Pd( object ) :


  def __init__( self ) :
    self.Item = Item
    self.__oTls = threading.local()


  ##  Shortcut to access regexp search result properties.
  def search( self, s_pattern, s_subject ) :
    oMatch = re.search( s_pattern, s_subject )
    if oMatch is not None :
      self.__oTls.match = RegexpMatch( oMatch )
      return self.__oTls.match
    return None


  ##  Wraps any object so it can be used inside 'with' and reference
  ##  to it will be available as |pd.o|.
  def wrap( self, o_target ) :
    o_target.__class__.__enter__ = enter
    o_target.__class__.__exit__ = exit
    return o_target


  ##! |pd.o| holds current DSL item that is thread local and is auto
  ##  maintained  via |with| statements:
  ##  | with pu.Wnd() :
  ##  |   # 'with' sets pu.o to 'Wnd' instance for current thread.
  ##  |   with pu.Button() :
  ##  |     # Current pu.o is used as parent. 'with' sets pu.o for
  ##  |     # 'Button' instance.
  ##  |     pu.o.setText( "button" )
  ##  |   # pu.o is restored to 'Wnd' by leaving 'with' statement.
  ##  |   pu.o.setCaption( "window" )
  @property
  def o( self ) :
    if hasattr( self.__oTls, 'o' ) :
      return self.__oTls.o
    else :
      return None


  @o.setter
  def o( self, o_value ) :
    self.__oTls.o = o_value

  @property
  def match( self ) :
    if hasattr( self.__oTls, 'match' ) :
      return self.__oTls.match
    else :
      return None


pd = Pd()

