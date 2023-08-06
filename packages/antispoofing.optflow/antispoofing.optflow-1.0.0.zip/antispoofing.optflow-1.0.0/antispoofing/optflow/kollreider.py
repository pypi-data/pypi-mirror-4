#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Thu 15 Sep 07:46:56 2011

"""Implements auxiliar helper functions for the liveness detection method
described by Kollreider et al in "Non-intrusive liveness detection by face
images", Image and Vision Computing, 2007. 
"""

import bob
import numpy

class Anthropometry19x19:
  """A helper to convert KeyLemon (MCT face localization) bounding boxes to
  eye coordinates"""

  # Some constants we need for the job
  PUPIL_SE = (33.4+31.4)/2 #mm pupil-facial middle distance, p.275
  PUPIL_SE_SD = 2.0 #larger for males
  PUPIL_OS = (23.3+23.0)/2 #mm pupil-eyebrow distance, p.280
  PUPIL_OS_SD = 3.3 #mm larger for males
  N_STO = (76.6+69.4)/2.0 #mm from eye top to mouth, p.255
  N_STO_SD = 4.0 #larger for males
  CH_CH = (54.5+50.2)/2.0 #mm mouth width, p.303 
  CH_CH_SD = 3.5 #larger for females
  EX_EX = (91.2+87.8)/2.0 #mm outside eye corners (left and right), p.272
  EX_EX_SD = 3.2 #larger for females
  EN_EN = (33.3+31.8)/2.0 #mm inside eye corners (left and right), p.272
  EN_EN_SD = 2.7 #larger for males

  # Parameters for the KeyLemon model, taken from Torch3vision2.1 following
  # Sébastien's advice (c.f. mail on eye and mouth positions given bounding box
  # exchanged around the 21st./february/2011)
  MODEL_WIDTH = 19. #pixels, normalized model width
  D_EYES = 10. #pixels, normalized pixel distance between pupils
  Y_UPPER = 5. #pixels, normalized distance between head-top and eye-pupils

  def __init__(self, bbox):
    """Starts a new object with a bounding box"""
    self.bb = bbox
    if bbox is not None and self.bb.is_valid():
      self.ratio = self.bb.width / self.MODEL_WIDTH
      self.anthropo_ratio = (self.D_EYES*self.ratio)/(2*self.PUPIL_SE)
    else:
      from . import BoundingBox
      self.bb = BoundingBox(0,0,0,0)

  def eye_centers(self):
    """Returns the eye centers coordinates"""

    if not self.bb.is_valid(): return ((None, None), (None, None))

    Rx = (self.ratio * (self.D_EYES + self.MODEL_WIDTH) / 2) + self.bb.x
    Lx = Rx - (self.D_EYES * self.ratio)
    y = self.bb.y + (self.ratio * self.Y_UPPER)
    return ((round(Lx), round(y)), (round(Rx), round(y)))

  def face_center(self):
    """Returns the mid distance between eye brows and mouth top"""

    if not self.bb.is_valid(): return (None, None)

    x = (self.ratio * (self.D_EYES + self.MODEL_WIDTH) / 2.) + self.bb.x
    x -= (self.D_EYES * self.ratio) / 2.
    y = self.bb.y + (self.ratio * self.Y_UPPER)
    y += (self.ratio * self.D_EYES) / 4.
    return (round(x), round(y))

  def ear_centers(self):
    """Returns the ear centers left, right"""

    if not self.bb.is_valid(): return ((None, None), (None, None))

    Rx = self.bb.x + self.bb.width #+ (self.ratio * self.D_EYES) / 5.0
    Lx = self.bb.x #- (self.ratio * self.D_EYES) / 5.0
    y = self.bb.y + (self.ratio * self.Y_UPPER)
    y += (self.ratio * self.D_EYES) / 2.
    return ((round(Lx), round(y)), (round(Rx), round(y)))

  def mouth_bbox(self):
    """Returns the mouth bounding box (UNTESTED!) """

    from . import BoundingBox

    if not self.bb.is_valid(): BoundingBox(0, 0, 0, 0)

    Mx = self.bb.x + (self.bb.width/2.)
    Eye_y = self.bb.y + (self.ratio * self.Y_UPPER)
    My = Eye_y + ((self.N_STO-(self.PUPIL_OS/2.)) * self.anthropo_ratio)
    Mwidth = (self.CH_CH * self.anthropo_ratio)
    Mheight = 30. * self.anthropo_ratio #guessed
    return BoundingBox(round(Mx), round(My), round(Mwidth), round(Mheight))

  def eye_area(self):
    """Returns a bounding box to the eyes area"""

    from . import BoundingBox
    
    if not self.bb.is_valid(): BoundingBox(0, 0, 0, 0)

    Eye_y = self.bb.y + (self.ratio * self.Y_UPPER)
    Eye_x = self.bb.x + (self.bb.width / 2.) # eyes center
    Box_width = (self.EX_EX + 8.*self.EX_EX_SD) * self.anthropo_ratio
    Box_height = (self.PUPIL_OS + self.PUPIL_OS_SD) * 1.2 * self.anthropo_ratio
    Box_x = Eye_x - (Box_width/2.)
    Box_y = Eye_y - (Box_height/2.)
    return BoundingBox(round(Box_x), round(Box_y), round(Box_width), round(Box_height))

def get_central_window_average(flow, ratio, x, y):
  """Returns the central window sum in a square window taking into consideration
  the window size ratio compared to a 19x19 model).
  """
  ws = ratio * 8
  
  x_left = int(round(x - ws/2))
  if x_left < 0: x_left = 0
  x_right = int(round(x + ws/2))
  if x_right > flow.shape[1]: x_right = flow.shape[1]
  y_up = int(round(y - ws/2))
  if y_up < 0: y_up = 0
  y_bot = int(round(y + ws/2))
  if y_bot > flow.shape[0]: y_bot = flow.shape[0]

  region = flow[y_up:y_bot,x_left:x_right]

  S = 0
  counter = 0
  threshold = abs(region).max() / 2.0

  for x in range(region.shape[1]):
    for y in range(region.shape[0]):
      if abs(region[y,x]) > threshold: 
        S += region[y,x]
        counter += 1

  if not counter: return 0.
  return S/counter
  
def get_ear_window_average(flow, ratio, x, y):
  """Returns the ear window sum in a rectangular window taking into
  consideration the window size ratio compared to a 19x19 model).
  """
  ws = ratio * 8
  
  x_left = int(round(x - ws/4))
  if x_left < 0: x_left = 0
  x_right = int(round(x + ws/4))
  if x_right > flow.shape[1]: x_right = flow.shape[1]
  y_up = int(round(y - ws/2))
  if y_up < 0: y_up = 0
  y_bot = int(round(y + ws/2))
  if y_bot > flow.shape[0]: y_bot = flow.shape[0]

  region = flow[y_up:y_bot,x_left:x_right]

  S = 0
  counter = 0
  threshold = abs(region).max() / 2.0

  for x in range(region.shape[1]):
    for y in range(region.shape[0]):
      if abs(region[y,x]) > threshold: 
        S += region[y,x]
        counter += 1

  if not counter: return 0.
  return S/counter
  
def featurePerFrame(uv, bb, tau):
  """Returns the liveness score for a single frame.

  Keyword parameters:

    uv
      flow field for a single frame as a numpy array with dimenstions
      2 x height x width

    bb
      face location for a single frame

    tau
      the threshold "tau" to use for the liveness score calculation as
      indicated on the top-left column of page 8 in the paper.

  Returns Kollreider's liveness score L as defined in the paper. Returns zero if
  the bounding box is invalid
  """

  if bb is None or not bb.is_valid(): return 0. #assume it is an attack

  # Gets an estimation of the face and ear centers from the bouding box
  anthropo = Anthropometry19x19(bb)
  cx, cy = anthropo.face_center()
  cx = int(cx)
  cy = int(cy)
  (lx, ly), (rx, ry) = anthropo.ear_centers()
  lx = int(lx)
  ly = int(ly)
  rx = int(rx)
  ry = int(ry)

  # Decide if we are interested on the horizontal or vertical movement
  # This is doing |sim_h| > |sim_v|?
  if abs(uv[0,cy,cx]) > abs(uv[1,cy,cx]): use_flow = 0
  else: use_flow = 1

  part1 = get_central_window_average(uv[use_flow,:,:], anthropo.ratio, cx, cy)
  part2 = get_ear_window_average(uv[use_flow,:,:], anthropo.ratio, rx, ry)
  if not part2: cr = 0.0
  else: cr = part1/part2
  part3 = get_ear_window_average(uv[use_flow,:,:], anthropo.ratio, lx, ly)
  if not part3: cl = 0.0
  else: cl = part1/part3

  # Calculates the final liveness score "L" 
  return 0.25 * (float(abs(cr) > tau) + float(abs(cl) > tau) + \
      float(cr < 0) + float(cl < 0))

def computeFeature(flowField, faceLocs, tau):
  """Gets scores for all flows and taking into consideration all face locations
  found on the video stream

  Keyword parameters:

    flowField
      flow field for the entire video, as a numpy array with dinemensions
      numFrames x 2 x height x width

    faceLocs
      face location for all frames of input video, as a python iterable

    tau
      the threshold "tau" to use for the liveness score calculation as
      indicated on the top-left column of page 8 in the paper.

  Returns a numpy.ndarray containing the feature computed for all frames of
  input video. If a face is not detected, returns 0 for that frame.
  """

  f = []
  for i in range(flowField.shape[0]):
    f.append(featurePerFrame(flowField[i,:,:,:], faceLocs[i], tau))

  return numpy.array(f)
