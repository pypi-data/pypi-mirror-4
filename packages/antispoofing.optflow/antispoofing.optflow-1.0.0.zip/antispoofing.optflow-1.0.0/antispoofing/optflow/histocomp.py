#!/usr/bin/env python
# @2011
# Murali Mohan Chakka, trainee
# Andre Anjos <andre.anjos@idiap.ch>

"""Functionality to extract features (chi2stat) from computed optical flow field
"""

import bob
import numpy
import math

def chi2Stat(S, M):
  """Evaluates the Chi-square statistics between two histograms
  
  This computes chi square statistics as written in the paper Ahonen et al.,
  named "Face Recognition with local binary patterns", 2004 page 472
  """

  r = numpy.divide((S - M)**2, S+M)
  return numpy.nan_to_num(r).sum()

def histogramsPerFrame(uv, bb, bins, offset, border):
  """Histograms of face and background using the OF field

  This function calculate the histograms at face and background for a single
  optical flow frame
     
  Keyword parameters:

    uv
      3D flow field for a single frame as a bob array with shape
      (2, height, width).

    bb
      Face location for a single frame

    bins
      Number of bins required to compute histogram for RoI

    offset
      Offset to the histogram bins (in radians)

    border
      Specifies the border (background) around the detected face region. If
      'None' uses the full background.

  Returns chi2stat computed between face and background. Iff invalid face
  location, returns 0.5
  """

  if bb is None or not bb.is_valid():
    return (numpy.ones((bins,), 'float64') / bins, numpy.ones((bins,), 'float64') / bins)
  
  th = numpy.arctan2(uv[1,:,:], uv[0,:,:])
  t = th - offset
  th = numpy.where(t < -math.pi, t+(2*math.pi), t)
  if border is None:
    A = bob.ip.histogram(th, -math.pi, math.pi, bins)
  else:
    y_low   = bb.y - border
    if y_low < 0: y_low = 0
    y_up    = bb.y + bb.height + border
    if y_up > uv.shape[1]: y_up = uv.shape[1]
    x_left  = bb.x - border
    if x_left < 0: x_left = 0
    x_right = bb.x + bb.width + border
    if x_right > uv.shape[2]: x_right = uv.shape[2]

    A = bob.ip.histogram(th[y_low:y_up, x_left:x_right], -math.pi, math.pi, bins)
  B = bob.ip.histogram(th[bb.y:(bb.y+bb.height), bb.x:(bb.x+bb.width)], -math.pi, math.pi, bins)
  A = A.astype('float64')
  B = B.astype('float64')
  A -= B
  A /= A.sum()
  B /= B.sum()

  return (A, B) #face, background
  
def featurePerFrame(uv, bb, bins, offset, border):
  """This function calculates the histogram distances between face and
     background for a single optical flow frame
     
  Parameters:

    uv
      Flow field for a single frame as a bob array with shape
      (2, height, width).
 
    bb 
      Face location for a single frame

    bins
      Number of bins required to compute histogram for RoI

    offset
      Offset to the histogram bins (in radians)

    border
      Specifies the border (background) around the detected face region.
      If 'None' thakes the full background.

  Returns chi2stat computed between face and background. Iff invalid face
  location, returns 0.5
  """

  if bb is None or not bb.is_valid(): return numpy.nan

  face, background = histogramsPerFrame(uv, bb, bins, offset, border)

  return chi2Stat(face, background)
  
def computeFeature(flowField, faceLocs, bins, offset, border=None):
  """This function calculates the histogram distances between face and
     background for a given input video.
     
  Parameters:

    flowField
      Flow field for the entire video, as a bob array with dinemensions
      numFramesx2xheightxwidth

    faceLocs
      Face location for all frames of input video, as a python iterable

    bins
      Number of bins required to compute histogram for RoI

    offset
      Offset to the histogram bins (in radians)

    border
      Specifies the border (background) around the detected face region.
      If not specifies, it takes the full background.

  Returns a bob array containing the feature computed for all frames of input
  video
  """

  lc = flowField.shape[0]
  f = []
  for i in range(lc):
    f.append(featurePerFrame(flowField[i,:,:,:], faceLocs[i], 
      bins, offset, border))
  
  return numpy.array(f, 'float64')
