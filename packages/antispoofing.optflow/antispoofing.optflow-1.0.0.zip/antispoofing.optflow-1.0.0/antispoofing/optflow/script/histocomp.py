#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Chakka Murali Mohan<murali.chakka@idiap.ch>
# Monday, 19 Sept 2011 
# Added support for border parameter
# Friday 18 Nov 2011

"""Calculates the histogram distance (using Chi-square) between face and
background region histograms (with variable offset and variable number of bins)
of the flow field.
"""

import os, sys
import argparse
import math
import numpy
import antispoofing.utils.db
import antispoofing.utils.faceloc
from .. import histocomp

def main():

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  DBDIR = os.path.join(basedir, 'database')
  INPUTDIR = os.path.join(basedir, 'flows')
  OUTPUTDIR = os.path.join(basedir, 'histocmp')
  
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-v', '--verbose', default=False, action='store_true',
      help="Increases the output verbosity level")

  from ..version import __version__
  name = os.path.basename(os.path.splitext(sys.argv[0])[0])
  parser.add_argument('-V', '--version', action='version',
      version='Optical Flow Histogram Comparison v%s (%s)' % (__version__, name))

  # The next option just returns the total number of cases we will be running
  # It can be used to set jman --array option. To avoid user confusion, this
  # option is suppressed # from the --help menu
  parser.add_argument('--grid-count', dest='grid_count', action='store_true',
      default=False, help=argparse.SUPPRESS)

  parser.add_argument('-m', '--ff', '--minimum-face-size', 
      dest='min_face_size', metavar='PIXELS', type=int, default=0,
      help='Minimum face size to be considered when pre-processing and extrapolating detections (defaults to %(default)s)')
  parser.add_argument('-n', '--number-of-bins', metavar='INT>0', type=int, dest='bins', default=2, help='This gives the number of bins need be used while computing flow field histogram of RoI. (defaults to \'%(default)s\')')
  parser.add_argument('-o', '--offset', metavar='INT>=0', type=int, dest='offset', default=0, help='This offset value is taken for bin partisions while computing the flow field histogram of RoI. The value should be in degrees. (defaults to \'%(default)s\')')
  parser.add_argument('-b', '--border-size', metavar='INT>=0', type=int, dest='border', default=None, help='Number of extra pixels to define the region of interest from the bounding box (defaults to \'%(default)s\').')

  parser.add_argument('dbdir', metavar='DATABASEDIR', type=str, default=DBDIR,
      nargs='?', help='Base directory containing the face-locations to be used by this procedure (defaults to "%(default)s")')

  parser.add_argument('inputdir', metavar='INPUTDIR', type=str, default=INPUTDIR,
      nargs='?', help='Base directory containing the pre-calculated flows to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('outputdir', metavar='OUTPUTDIR', type=str, default=OUTPUTDIR,
      nargs='?', help='Base output directory for every file created by this procedure defaults to "%(default)s")')

  # Adds database support using the common infrastructure
  # N.B.: Only databases with 'video' support
  antispoofing.utils.db.Database.create_parser(parser, 'video')

  args = parser.parse_args()

  # Creates an instance of the database
  db = args.cls(args)

  if args.verbose:
    sys.stdout.write("Querying database...")
    sys.stdout.flush()

  real, attack = db.get_all_data()
  process = real + attack

  if args.grid_count:
    print len(process)
    sys.exit(0)
 
  if args.bins <= 1:
    parser.error('Number of bins must be atleast two')

  if args.offset < 0:
    parser.error('offset must be greater than or equal to zero')
  args.offset = args.offset * math.pi / 180

  # if we are on a grid environment, just find what I have to process.
  if os.environ.has_key('SGE_TASK_ID'):
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(process):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(process))
    process = [process[pos]]

  if args.verbose:
    sys.stdout.write("Ok\n")
    sys.stdout.flush()

  counter = 0
  
  for obj in process:
    
    counter += 1

    filename = obj.make_path(args.inputdir, '.hdf5')
    input = obj.load(args.inputdir, '.hdf5')
    facefile = obj.facefile(args.dbdir)
    locations = antispoofing.utils.faceloc.preprocess_detections(facefile,
        len(input), facesize_filter=args.min_face_size)

    if args.verbose:
      sys.stdout.write("Processing file %s (%d frames) [%d/%d]..." % (filename,
        len(input), counter, len(process)))
      sys.stdout.flush()

    olderr_state = numpy.seterr(all='ignore')
    data = histocomp.computeFeature(input, locations, args.bins, args.offset,
        args.border)
    numpy.seterr(**olderr_state)
    obj.save(data, args.outputdir, '.hdf5')

    if args.verbose:
      sys.stdout.write('Ok\n')
      sys.stdout.flush()

  return 0

if __name__ == "__main__":
  sys.exit(main())
