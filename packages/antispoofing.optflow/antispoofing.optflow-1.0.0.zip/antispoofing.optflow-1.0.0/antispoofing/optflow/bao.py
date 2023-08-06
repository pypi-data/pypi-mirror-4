#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 12 Sep 2011 16:43:14 CEST 

"""Implements the spoofing classifier as proposed by W. Bao et al in the paper
entitled "A Liveness Detection Method for Face Recognition Based on Optical 
Flow Field.
"""

import bob
import math
import numpy

def get_a1a2(region):
  """Returns a tuple (a1,a2) representing the flow arithmetic averages over 
  the horizontal and vertical axis respectively if the support region is cut 
  in half, vertically.
  """

  m_2 = int(math.ceil(region.shape[2] / 2.0)) #x direction

  left = region[:,:,:m_2]
  right = region[:,:,m_2:]
  U_left = left[0,:,:].mean()
  V_left = left[1,:,:].mean()
  U_right = right[0,:,:].mean()
  V_right = right[1,:,:].mean()

  if not m_2: 
    a1 = 0.
    a2 = 0.
  else: 
    a1 = (U_right - U_left) / m_2
    a2 = (V_right - V_left) / m_2

  return a1, a2

def get_b1b2(region):
  """Returns a tuple (b1,b2) representing the flow arithmetic averages over 
  the horizontal and vertical axis respectively if the support region is cut 
  in half, horizontally.
  """

  n_2 = int(math.ceil(region.shape[1] / 2.0)) #y direction

  upper = region[:,:n_2,:]
  lower = region[:,n_2:,:]
  U_upper = upper[0,:,:].mean()
  V_upper = upper[1,:,:].mean()
  U_lower = lower[0,:,:].mean()
  V_lower = lower[1,:,:].mean()

  if not n_2:
    b1 = 0.
    b2 = 0.
  else:
    b1 = (U_upper - U_lower) / n_2
    b2 = (V_upper - V_lower) / n_2

  return b1, b2

def get_c1c2(region, a1, a2, b1, b2):
  """Returns the tuple (c1,2) taking into consideration the other flows"""

  n_2 = math.ceil(region.shape[1] / 2.0) #y direction
  m_2 = math.ceil(region.shape[2] / 2.0) #x direction

  U_avg = region[0,:,:].mean()
  V_avg = region[1,:,:].mean()

  return (U_avg - (a1*n_2) - (b1*m_2), V_avg - (a2*n_2) - (b2*m_2))

def featurePerFrame(uv, bb, border):
  """Returns the difference degree calculation "D" as indicated on the paper,
  for a certain flow field, a face bounding box and a border to be drawn around
  such a bounding box that is 'border' pixels wide.

  Keyword parameters:

    uv
      flow field for a single frame as a bob array with dimenstions
      2 x height x width

    bb
      face location for a single frame

    border
      number of pixels to the define the region of interest from the bounding
      box.

  Returns Bao's "Difference Degree" D as defined in the paper. Returns zero if
  the bounding box is invalid
  """

  if bb is None or not bb.is_valid(): return 0.

  y_low   = bb.y - border
  if y_low < 0: y_low = 0
  y_up    = bb.y + bb.height + border
  if y_up > uv.shape[1]: y_up = uv.shape[1]
  x_left  = bb.x - border
  if x_left < 0: x_left = 0
  x_right = bb.x + bb.width + border
  if x_right > uv.shape[2]: x_right = uv.shape[2]

  region = uv[:,y_low:y_up,x_left:x_right]

  a1, a2 = get_a1a2(region)
  b1, b2 = get_b1b2(region)
  c1, c2 = get_c1c2(region, a1, a2, b1, b2)

  denominator = numpy.sqrt(region[0,:,:]**2 + region[1,:,:]**2).sum()

  seq_i = numpy.empty_like(region[0,:,:])
  for k in range(region.shape[2]): seq_i[:,k] = k+1
  seq_j = numpy.empty_like(region[0,:,:])
  for k in range(region.shape[1]): seq_j[k,:] = k+1

  numerator = numpy.sqrt( (a1*seq_i + b1*seq_j + c1 - region[0,:,:])**2 + \
      (a2*seq_i + b2*seq_j + c2 - region[1,:,:])**2 ).sum()

  if not denominator: return 0.
  return numerator / denominator

def computeFeature(flowField, faceLocs, border):
  """Gets scores for all flows and taking into consideration all face locations
  found on the video stream

  Keyword parameters:

    flowField
      flow field for the entire video, as a bob array with dinemensions
      numFramesx2xheightxwidth

    faceLocs
      face location for all frames of input video, as a python iterable

    border
      number of pixels to the define the region of interest from the bounding
      box.

  Returns a bob array containing the feature computed for all frames of input
  video. If a face is not detected, returns 0 for that frame.  
  """

  f = []
  for i in range(flowField.shape[0]):
    f.append(featurePerFrame(flowField[i,:,:,:], faceLocs[i], border))

  return numpy.array(f)
