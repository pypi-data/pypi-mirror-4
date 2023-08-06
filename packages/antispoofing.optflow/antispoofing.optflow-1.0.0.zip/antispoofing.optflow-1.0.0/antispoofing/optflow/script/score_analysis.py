#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 05 Dec 2011 15:25:08 CET 

"""Analyzes a given input directory considering a standard directory for the
database from which the scores were generated from. This script outputs
both EER and HTER figures for a set of scores based on a given protocol
(using a frame-based analysis).
"""

import os
import sys
import bob
import numpy
import argparse
import antispoofing.utils.db
from ..windowing import load as wload

def print_perf(real_dev_objs, attack_dev_objs,
    real_test_objs, attack_test_objs,
    inputdir, window_size, overlap, mhter):
  """Gets the two performance numbers a given score set"""

  real_dev = numpy.hstack([wload(k, inputdir, window_size, overlap) for k in real_dev_objs])
  attack_dev = numpy.hstack([wload(k, inputdir, window_size, overlap) for k in attack_dev_objs])
  real_test = numpy.hstack([wload(k, inputdir, window_size, overlap) for k in real_test_objs])
  attack_test = numpy.hstack([wload(k, inputdir, window_size, overlap) for k in attack_test_objs])
 
  if not mhter:
    thres = bob.measure.eer_threshold(attack_dev, real_dev)
    string = 'EER'
  else:
    thres = bob.measure.min_hter_threshold(attack_dev, real_dev)
    string = 'Min.HTER'

  dev_far, dev_frr = bob.measure.farfrr(attack_dev, real_dev, thres)
  test_far, test_frr = bob.measure.farfrr(attack_test, real_test, thres)

  print "Thres. at %s of development set: %.4e" % (string, thres)
  print "[EER @devel] FAR: %.2f%% (%d / %d) | FRR: %.2f%% (%d / %d) | HTER: %.2f%%" % \
      (100*dev_far, int(round(dev_far*attack_dev.size)), attack_dev.size,  
       100*dev_frr, int(round(dev_frr*real_dev.size)), real_dev.size,
       50*(dev_far+dev_frr))
  print "[HTER @test] FAR: %.2f%% (%d / %d) | FRR: %.2f%% (%d / %d) | HTER: %.2f%%" % \
      (100*test_far, int(round(test_far*attack_test.size)), attack_test.size,
       100*test_frr, int(round(test_frr*real_test.size)), real_test.size,
       50*(test_far+test_frr))

def main():
  """Main method"""
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUTDIR = os.path.join(basedir, 'scores')

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('inputdir', metavar='INPUTDIR', type=str,
      default=INPUTDIR, nargs='?', help='Base directory containing the pre-calculated flows to be treated by this procedure (defaults to "%(default)s")')

  parser.add_argument('--mhter', dest='mhter', action='store_true',
      default=False, help='If set, uses the Min. HTER as minimization criteria for finding the detection threshold on the development set instead of the EER.')

  parser.add_argument('-w', '--window-size', dest="window_size",
      metavar='INT>1', type=int, help="determines the window size to be used when clustering frame-difference observations - if not set, don't cluster windows.")
  
  parser.add_argument('-o', '--overlap', dest="overlap", type=int,
      help="determines the window overlapping; this number has to be between 0 (no overlapping) and 'window-size'-1")

  parser.add_argument('-b', '--breakdown', dest="breakdown", default=False,
      action='store_true', help="if set, we also perform break-down analysis on the database of your choice, using all possible test filters defined in the database")

  # Adds database support using the common infrastructure
  # N.B.: Only databases with 'video' support
  antispoofing.utils.db.Database.create_parser(parser, 'video')

  args = parser.parse_args()

  # checks window size and overlap
  if args.window_size is not None:
    if args.window_size <= 1:
      parser.error("window-size has to be greater than one")
    if args.overlap is None:
      args.overlap = args.window_size-1

  if args.overlap is not None:
    if args.window_size is None:
      parser.error("overlap can only be set if window-size is also set")
    if args.overlap >= args.window_size or args.overlap < 0:
      parser.error("overlap has to be smaller than window-size and greater or equal zero")

  # Creates an instance of the database
  db = args.cls(args)

  real_dev, attack_dev = db.get_devel_data()
  real_test, attack_test = db.get_test_data()

  print "Database: %s, version %s" % (db.name(), db.version())
  print "Input data: %s" % args.inputdir
  if args.window_size:
    print "Window size: %d (overlap = %d)" % (args.window_size, args.overlap)

  print "\n[Complete set error analysis]"
  print_perf(real_dev, attack_dev, real_test, attack_test, args.inputdir, args.window_size, args.overlap, args.mhter)

  if args.breakdown:

    for f in db.get_test_filters():
      print "\n[%s break-down analysis]" % f.capitalize()
      data = db.get_filtered_test_data(f)
      for key, (real_filtered, attack_filtered) in data.iteritems():
        print "\n%s:" % key.capitalize()
        print_perf(real_dev, attack_dev, real_filtered, attack_filtered, args.inputdir, args.window_size, args.overlap, args.mhter)
 
if __name__ == '__main__':
  main()
