#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python DSL
# Copyright 2012 Grigory Petrov
# See LICENSE for details.

from pd_impl import pd


class Tag( pd.Item ) :


  def build( self, n_offset = 0 ) :
    print( " " * n_offset + "<{0}>".format( self.dname ) )
    for oChild in self.dchildren :
      oChild.build( n_offset + 2 )
    print( " " * n_offset + "</{0}>".format( self.dname ) )

