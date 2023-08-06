#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 23 Jan 2013 09:20:14 CET 

"""Trains and executes LDA on the Wine Dataset
"""

from .iris import train, project, plot
import xbob.db.wine

def main():

  data = xbob.db.wine.data()
  machine = train(data)
  output = project(data, machine)
  plot(output, 'wine')
