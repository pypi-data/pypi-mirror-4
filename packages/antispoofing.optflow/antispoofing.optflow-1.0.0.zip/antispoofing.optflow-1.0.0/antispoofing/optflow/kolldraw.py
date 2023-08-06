#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Thu 15 Sep 07:46:56 2011

"""Implements auxiliar helper functions for the liveness detection method
described by Kollreider et al in "Non-intrusive liveness detection by face
images", Image and Vision Computing, 2007. 
"""

import bob
from . import kollreider

def draw_central_window(image, ratio, x, y):
  """Draws what our Kollreider implementation would get from the face center.
  """
  ws = ratio * 8
  
  x_left = int(round(x - ws/2))
  if x_left < 0: x_left = 0
  x_right = int(round(x + ws/2))
  if x_right > image.shape[2]: x_right = image.shape[2]
  y_up = int(round(y - ws/2))
  if y_up < 0: y_up = 0
  y_bot = int(round(y + ws/2))
  if y_bot > image.shape[1]: y_bot = image.shape[1]

  bob.ip.draw_box(image, x_left, y_up, x_right-x_left, y_bot-y_up,
      (255,255,0))
  bob.ip.draw_box(image, x_left-1, y_up-1, x_right-x_left+2, y_bot-y_up+2,
      (255,255,0))
  bob.ip.draw_box(image, x_left-2, y_up-2, x_right-x_left+4, y_bot-y_up+4,
      (255,255,0))

def draw_ear_window(image, ratio, x, y):
  """Draws what our Kollreider implementation would get from the ears
  center."""

  ws = ratio * 8
  
  x_left = int(round(x - ws/4))
  if x_left < 0: x_left = 0
  x_right = int(round(x + ws/4))
  if x_right > image.shape[2]: x_right = image.shape[2]
  y_up = int(round(y - ws/2))
  if y_up < 0: y_up = 0
  y_bot = int(round(y + ws/2))
  if y_bot > image.shape[1]: y_up = image.shape[1]

  bob.ip.draw_box(image, x_left, y_up, x_right-x_left, y_bot-y_up,
      (255,255,0))
  bob.ip.draw_box(image, x_left-1, y_up-1, x_right-x_left+2, y_bot-y_up+2,
      (255,255,0))
  bob.ip.draw_box(image, x_left-2, y_up-2, x_right-x_left+4, y_bot-y_up+4,
      (255,255,0))

def draw_frame(frame, bb):
  """Draws the bounding boxes for the face center and ears on a give frame,
  given a certain bounding box.
  """

  if bb is None or not bb.is_valid(): return 

  # Gets an estimation of the face and ear centers from the bouding box
  anthropo = kollreider.Anthropometry19x19(bb)
  cx, cy = anthropo.face_center()
  cx = int(cx)
  cy = int(cy)
  (lx, ly), (rx, ry) = anthropo.ear_centers()
  lx = int(lx)
  ly = int(ly)
  rx = int(rx)
  ry = int(ry)

  draw_central_window(frame, anthropo.ratio, cx, cy)
  draw_ear_window(frame, anthropo.ratio, lx, ly)
  draw_ear_window(frame, anthropo.ratio, rx, ry)

def draw_movie(movie, faceLocs):
  """Runs draw_frame() on all frames of the input movie. Returns a set of frame
  already processed and annotated"""

  retval = []
  for k, frame in enumerate(movie):
    draw_frame(frame, faceLocs[k])
    retval.append(frame)

  return retval
