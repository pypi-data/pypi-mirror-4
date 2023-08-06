#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 23 Jan 2013 09:20:14 CET 

"""Trains and executes LDA on the Fisher Iris Flower Dataset
"""

import bob
import numpy
import matplotlib.pyplot as mpl

def train(data):
  """Trains a new LinearMachine given the input data
  
  Keyword parametes:

    data
      The data set, a python dictionary with the data for each class properly
      labelled by a string. The values of each entry of the dictionary
      correspond to a numpy.ndarray of floats with features in columns. Every
      row corresponds to a single example.

  Returns a new bob.machine.LinearMachine, trained with using Fisher's LDA
  algorithm.
  """
  
  print "Training your LDA machine..."
  trainer = bob.trainer.FisherLDATrainer()
  machine, unused_eigen_values = trainer.train(data.values())
  print "Training done."
  return machine

def project(data, machine):
  """Projects the given data through the LinearMachine
  
  Keyword parametes:

    data
      The data set, a python dictionary with the data for each class properly
      labelled by a string. The values of each entry of the dictionary
      correspond to a numpy.ndarray of floats with features in columns. Every
      row corresponds to a single example.

  Returns a new dictionary, similar to the input one, in which the values of
  each entry are numpy.ndarray's with N-1 columns representing the LDA
  components for every example in the input data matrix. Examples, like for the
  input data, are organized in rows. LDA components are organized by their
  equivalent eigen value in decreasing order.
  """

  print "Passing the data through the machine..."
  output = {}
  for key in data:
    output[key] = machine.forward(data[key])
  print "Data projected."
  return output

def plot(data, dbname):
  """Saves a png histogram of the first LDA component for all classes in data

  Keyword parametes:

    data
      The data set, a python dictionary with the data for each class properly
      labelled by a string. The values of each entry of the dictionary
      correspond to a numpy.ndarray of floats with features in columns. Every
      row corresponds to a single example.
  """

  print "Plotting..."
  colors = ['green', 'blue', 'red']
  use_color = 0
  for key, value in data.iteritems():
    mpl.hist(value[:,0], bins=8, color=colors[use_color],
        label=key.capitalize(), alpha=0.5)

    # Rotate through colors
    use_color += 1
    if use_color >= len(colors): use_color = 0

  # Plot "perfectioning"
  mpl.legend()
  mpl.grid(True)
  mpl.axis([-3,+3,0,20])
  mpl.title("%s / 1st. LDA component" % dbname.capitalize())
  mpl.xlabel("LDA[0]")
  mpl.ylabel("Count")

  mpl.savefig('%s.png' % dbname)
  print "Saved your plot at %s.png... Bye!" % dbname

def main():

  data = bob.db.iris.data()
  machine = train(data)
  output = project(data, machine)
  plot(output, 'iris')
