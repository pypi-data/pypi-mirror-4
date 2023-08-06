import sys
from optparse import OptionParser
import os
import pweave


def weave():

    if len(sys.argv)==1:
        print "This is Pweave %s, enter Pweave -h for help" % pweave.__version__
        sys.exit()

# Command line options
    parser = OptionParser(usage="Pweave[options] sourcefile", version="Pweave " + pweave.__version__)
    parser.add_option("-f", "--format", dest="format", default='rst',
                      help="The output format. Available formats: " + pweave.PwebFormats.shortformats() + ". See http://mpastell.com/pweave/formats.html")
    parser.add_option("-m", "--matplotlib", dest="mplotlib", default='true',
                      help="Do you want to use matplotlib (or Sho with Ironpython) True (default) or False")
    parser.add_option("-d","--documentation-mode", dest="docmode",
                  action = "store_true" ,default=False,
                      help="Use documentation mode, chunk code and results will be loaded from cache and inline code will be hidden")
    parser.add_option("-c","--cache-results", dest="cache",
                  action = "store_true", default=False,
                      help="Cache results to disk for documentation mode")
    parser.add_option("--figure-directory", dest="figdir", default = 'figures',
                      help="Directory path for matplolib graphics: Default 'figures'")
    parser.add_option("--cache-directory", dest="cachedir", default = 'cache',
                      help="Directory path for cached results used in documentation mode: Default 'cache'")
    parser.add_option("-g","--figure-format", dest="figfmt",
                      help="Figure format for matplotlib graphics: Defaults to 'png' for rst and Sphinx html documents and 'pdf' for tex")

    (options, args) = parser.parse_args()
    infile = args[0]
    mplotlib = (options.mplotlib.lower() == 'true')

    if options.figfmt is not None:
        figfmt = ('.%s' % options.figfmt)
    else:
        figfmt = None


    pweave.pweave(infile, doctype = options.format, plot = mplotlib,
           docmode = options.docmode, cache = options.cache, figdir = options.figdir,
           cachedir = options.cachedir, figformat = figfmt)

def tangle():
    if len(sys.argv)==1:
        print "This is Ptangle %s" % pweave.__version__
        print "Usage: Ptangle file"
        sys.exit()

    pweave.ptangle(sys.argv[1])
