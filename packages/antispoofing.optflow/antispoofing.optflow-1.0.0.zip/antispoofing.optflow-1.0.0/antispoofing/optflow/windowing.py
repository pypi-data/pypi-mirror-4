#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 01 Mar 2013 13:07:55 CET 

"""Methods for loading data and window with overlap at the same time.
"""

import numpy
import scipy.stats

def load(obj, inputdir, window_size, overlap):
  """Loads the data from the filename given, applying the windowing operation
  if necessary.
  """

  data = obj.load(inputdir, '.hdf5')
  if window_size is not None:
    data = numpy.nan_to_num(data)
    N = len(data)
    start_range = range(0, N-window_size+1, window_size-overlap)
    end_range = range(window_size, N+1, window_size-overlap)
    indices = zip(start_range, end_range)
    retval = numpy.ndarray((len(indices),), dtype='float64')
    for k, (start, end) in enumerate(indices):
      retval[k] = scipy.stats.nanmean(data[start:end])
    return retval
  return data.flat
