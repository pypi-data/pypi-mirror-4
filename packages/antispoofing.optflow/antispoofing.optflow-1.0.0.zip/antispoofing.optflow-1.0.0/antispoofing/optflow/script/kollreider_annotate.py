#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 14 Sep 2011 14:25:04 CEST 

"""Annotates a movie sequence with the regions calculated by expanding the
face-detection bounding boxes. The annotations corresponds to the regions in
the face used by the anti-spoofing method described at "Non-intrusive liveness
detection by face images", 2009, by Kollreider K. et al, in Image and Vision
Computing 27 (2009), pp 233-244."""

import os, sys
import argparse
import math
import bob
import antispoofing.utils.db
import antispoofing.utils.faceloc
from .. import kolldraw

def main():

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  DBDIR = os.path.join(basedir, 'database')
  OUTPUTDIR = os.path.join(basedir, 'histocmp')
  
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-v', '--verbose', default=False, action='store_true',
      help="Increases the output verbosity level")

  from ..version import __version__
  name = os.path.basename(os.path.splitext(sys.argv[0])[0])
  parser.add_argument('-V', '--version', action='version',
      version='Kollreider Region Annotation tool v%s (%s)' % (__version__, name))

  # The next option just returns the total number of cases we will be running
  # It can be used to set jman --array option. To avoid user confusion, this
  # option is suppressed # from the --help menu
  parser.add_argument('--grid-count', dest='grid_count', action='store_true',
      default=False, help=argparse.SUPPRESS)

  parser.add_argument('-m', '--ff', '--minimum-face-size', 
      dest='min_face_size', metavar='PIXELS', type=int, default=0,
      help='Minimum face size to be considered when pre-processing and extrapolating detections (defaults to %(default)s)')

  parser.add_argument('dbdir', metavar='DATABASEDIR', type=str, default=DBDIR,
      nargs='?', help='Base directory containing the face-locations to be used by this procedure (defaults to "%(default)s")')

  parser.add_argument('outputdir', metavar='OUTPUTDIR', type=str, 
      default=OUTPUTDIR, nargs='?', help='Base output directory for every file created by this procedure defaults to "%(default)s")')

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

    input = bob.io.load(obj.videofile(args.dbdir))
    facefile = obj.facefile(args.dbdir)
    locations = antispoofing.utils.faceloc.preprocess_detections(facefile,
        len(input), facesize_filter=args.min_face_size)

    if args.verbose:
      sys.stdout.write("Processing file `%s' (%d frames) [%d/%d]" %
          (obj.videofile(args.dbdir), len(input), counter, len(process)))
      sys.stdout.flush()

    data = []
    for k, frame in enumerate(input):
      kolldraw.draw_frame(frame, locations[k])
      data.append(frame)
      if args.verbose: 
        sys.stdout.write(".")
        sys.stdout.flush()

    if args.verbose:
      sys.stdout.write('Ok\n')
      sys.stdout.flush()

    output = obj.make_path(args.outputdir, '.avi')
    if args.verbose:
      sys.stdout.write("Writing file `%s'..." % output)
      sys.stdout.flush()

    obj.save(data, args.outputdir, '.avi')

    if args.verbose:
      sys.stdout.write('Ok\n')
      sys.stdout.flush()

  return 0

if __name__ == "__main__":
  sys.exit(main())
