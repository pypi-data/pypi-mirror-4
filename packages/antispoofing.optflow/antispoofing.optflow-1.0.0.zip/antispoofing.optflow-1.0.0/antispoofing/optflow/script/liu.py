#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 21 Feb 16:58:33 2013 CET

"""Estimates the (dense) Optical Flow field using Ce Liu's framework.

This program will dump a single output HDF5 file that contains a 4D
double-precision array. Each array is composed of two planes. Each plane
matches the size of the image or video input. The first plane corresponds to
the output of the flow estimation along the horizontal axis, i.e. the
horizontal velocities, also known as Vx or U in many papers. The second plane
corresponds to the vertical velocities, also know as Vy or V.
"""

import os, sys
import argparse
import bob
import antispoofing.utils.db
import xbob.optflow.liu

def add_options(parser, alpha, ratio, min_width, outer, inner, iterations, 
    method, variant):

  if variant.lower() == 'cg':
    parser.add_argument('-g', '--gray-scale', dest='gray', default=False, action='store_true', help="Gray-scales input data before feeding it to the flow estimation. This uses Bob's gray scale conversion instead of the Liu's built-in conversion and may lead to slightly different results.")
  else:
    parser.set_defaults(gray=True)

  parser.add_argument('-a', '--alpha', dest='alpha', default=alpha, type=float, metavar='FLOAT', help="Regularization weight (defaults to %(default)s)")

  parser.add_argument('-r', '--ratio', dest='ratio', default=ratio, type=float, metavar='FLOAT', help="Downsample ratio (defaults to %(default)s)")

  parser.add_argument('-m', '--min-width', dest='min_width', 
      default=min_width, type=int, metavar='N', help="Width of the coarsest level (defaults to %(default)s)")

  parser.add_argument('-o', '--outer-fp-iterations', metavar='N', dest='outer', default=outer, type=int, help="The number of outer fixed-point iterations (defaults to %(default)s)")

  parser.add_argument('-i', '--inner-fp-iterations', metavar='N', dest='inner', default=inner, type=int, help="The number of inner fixed-point iterations (defaults to %(default)s)")

  parser.add_argument('-x', '--iterations', metavar='N', dest='iterations', default=iterations, type=int, help="The number of %s (error-minimization) iterations (defaults to %%(default)s)" % variant)

  parser.set_defaults(flow=method)
  parser.set_defaults(variant=variant)

def main():
  
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUTDIR = os.path.join(basedir, 'database')
  OUTPUTDIR = os.path.join(basedir, 'flows')

  parser.add_argument('-v', '--verbose', default=False, action='store_true',
      help="Increases the output verbosity level")

  from ..version import __version__
  name = os.path.basename(os.path.splitext(sys.argv[0])[0])
  parser.add_argument('-V', '--version', action='version',
      version='Optical Flow Estimation Tool v%s (%s)' % (__version__, name))

  # The next option just returns the total number of cases we will be running
  # It can be used to set jman --array option. To avoid user confusion, this
  # option is suppressed # from the --help menu
  parser.add_argument('--grid-count', dest='grid_count', action='store_true',
      default=False, help=argparse.SUPPRESS)

  # secret option to limit the number of video frames to run for (test option)
  parser.add_argument('--video-frames', dest='frames', type=int, help=argparse.SUPPRESS)

  # Add options for the CG method (old version from Liu, which is attested)
  add_options(parser, 0.02, 0.75, 30, 20, 1, 50, xbob.optflow.liu.cg_flow, 'CG')

  parser.add_argument('inputdir', metavar='DATABASEDIR', type=str, default=INPUTDIR,
      nargs='?', help='Base directory containing the videos to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('outputdir', metavar='OUTPUTDIR', type=str, default=OUTPUTDIR,
      nargs='?', help='Base output directory for every file created by this procedure defaults to "%(default)s")')

  # Adds database support using the common infrastructure
  # N.B.: Only databases with 'video' support
  antispoofing.utils.db.Database.create_parser(parser, 'video')

  args = parser.parse_args()

  # Creates an instance of the database
  db = args.cls(args)

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

  counter = 0
  for obj in process:
    counter += 1
 
    filename = obj.videofile(args.inputdir)

    # start the work here...
    flows = []
    if args.frames:

      if args.verbose:
        sys.stdout.write('Loading only %d frames from `%s\'...' % \
            (args.frames, filename))
        sys.stdout.flush()
        sys.stdout.write('Ok\n')
        sys.stdout.flush()

      input = bob.io.VideoReader(filename)[:args.frames]

    else:

      if args.verbose:
        sys.stdout.write('Loading all frames from `%s\'...' % filename)
        sys.stdout.flush()

      input = bob.io.load(filename)

    if args.verbose:
      sys.stdout.write('Ok\n')
      sys.stdout.flush()

    if args.verbose:
      sys.stdout.write('Converting %d frames to double...' % len(input))
      sys.stdout.flush()

    input = [k.astype('float64')/255. for k in input]

    if args.verbose:
      sys.stdout.write('Ok\n')
      sys.stdout.flush()

    if args.gray:
      
      if args.verbose:
        sys.stdout.write('Converting %d frames to grayscale...' % len(input))
        sys.stdout.flush()
     
      input = [bob.ip.rgb_to_gray(k) for k in input]
    
      if args.verbose:
        sys.stdout.write('Ok\n')
        sys.stdout.flush()

    if args.verbose:
      sys.stdout.write("Processing %d frames [%d/%d]" % \
          (len(input), counter, len(process)))

      sys.stdout.flush()

    for index, (i1, i2) in enumerate(zip(input[:-1], input[1:])):
      if args.verbose:
        sys.stdout.write('.')
        sys.stdout.flush()
      flows.append(args.flow(i1, i2, args.alpha, args.ratio, args.min_width,
        args.outer, args.inner, args.iterations)[0:2])

    if args.verbose:
      sys.stdout.write('Ok\n')
      sys.stdout.flush()

    output = obj.make_path(args.outputdir, '.hdf5')
    outputdir = os.path.dirname(output)

    # creates output directory if not already there
    if not os.path.exists(outputdir):
      try:
        if args.verbose:
          sys.stdout.write('Creating directory `%s\'...' % outputdir)
          sys.stdout.flush()
        os.makedirs(outputdir)
        if args.verbose:
          sys.stdout.write('Ok\n')
          sys.stdout.flush()
      except OSError as exc:
        import errno
        if exc.errno == errno.EEXIST: pass
        else: raise

    if args.verbose:
      sys.stdout.write('Saving flows to `%s\'...' % output)
      sys.stdout.flush()
    
    out = bob.io.HDF5File(output, 'w')
    out.set('uv', flows)
    out.set_attribute('method', args.variant, 'uv')
    out.set_attribute('alpha', args.alpha, 'uv')
    out.set_attribute('ratio', args.ratio, 'uv')
    out.set_attribute('min_width', args.min_width, 'uv')
    out.set_attribute('n_outer_fp_iterations', args.outer, 'uv')
    out.set_attribute('n_inner_fp_iterations', args.inner, 'uv')
    out.set_attribute('n_iterations', args.iterations, 'uv')

    if args.verbose:
      sys.stdout.write('Ok\n')
      sys.stdout.flush()

  return 0

if __name__ == "__main__":
  main()
