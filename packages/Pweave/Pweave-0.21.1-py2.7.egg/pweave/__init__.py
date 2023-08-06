# Python module Pweave
# Matti Pastell 2010-2013
# http://mpastell.com/pweave

from pweb import *

__version__ = '0.21.1'


def pweave(file, doctype = 'rst', plot = True,
           docmode = False, cache = False,
           figdir = 'figures', cachedir = 'cache',
           figformat = None, returnglobals = True, listformats = False):
    """
    Processes a Pweave document and writes output to a file

    :param file: ``string`` input file
    :param doctype: ``string`` document format: 'sphinx', 'rst', 'pandoc' or 'tex'
    :param plot: ``bool`` use matplotlib (or Sho with Ironpython) 
    :param docmode: ``bool`` use documentation mode, chunk code and results will be loaded from cache and inline code will be hidden
    :param cache: ``bool`` Cache results to disk for documentation mode
    :param figdir: ``string`` directory path for figures
    :param cachedir: ``string`` directory path for cached results used in documentation mode
    :param figformat: ``string`` format for saved figures (e.g. '.png'), if None then the default for each format is used
    :param returnglobals: ``bool`` if True the namespace of the executed document is added to callers global dictionary. Then it is possible to work interactively with the data while writing the document. IronPython needs to be started with -X:Frames or this won't work.
    :param listformats: ``bool`` List available formats and exit
    """

    if listformats:
        PwebFormats.listformats()
        return

    

    assert file != "" is not None, "No input specified"


    doc = Pweb(file)
    doc.setformat(doctype)
    if sys.platform == 'cli':
        Pweb.usesho = plot
        Pweb.usematplotlib = False
    else:
        Pweb.usematplotlib = plot
    
    Pweb.figdir = figdir
    Pweb.cachedir = cachedir
    doc.documentationmode = docmode
    doc.storeresults = cache

    if figformat is not None:
        doc.formatdict['figfmt'] = figformat
        doc.formatdict['savedformats'] = [figformat]

    #Returning globals
    try:
        doc.weave()
        if returnglobals:
        #Get the calling scope and return results to its globals
        #this way you can modify the weaved variables from repl
            _returnglobals()
    except Exception as inst:
        sys.stderr.write('%s\n%s\n' % (type(inst), inst.args))
        #Return varibles used this far if there is an exception
        if returnglobals:
           _returnglobals()

def _returnglobals():
    """Inspect stack to get the scope of the terminal/script calling pweave function"""
    if hasattr(sys,'_getframe'):
        caller = inspect.stack()[2][0]
        caller.f_globals.update(Pweb.globals)
    if not hasattr(sys,'_getframe'):
        print('%s\n%s\n' % ("Can't return globals" ,"Start Ironpython with ipy -X:Frames if you wan't this to work"))

def ptangle(file):
    """Tangles a noweb file i.e. extracts code from code chunks to a .py file
    
    :param file: ``string`` the pweave document containing the code
    """
    doc = Pweb(file)
    doc.tangle()

def stitch(file, format = "md"):
    """Capture resuls and code from python code"""
    f = open(file, 'r')
    code = f.read()
    f.close()
    header = '<HTML><HEAD><link rel="stylesheet" href="pygments.css"/></HEAD><BODY>\n'
    footer = '\n</BODY></HTML>'
    document = header + "<<fig=True>>=\n" + code + "@\n" + footer
    doc = Pweb(format = "html")
    doc.parse(string = document, basename = "file")
    #doc.run()
    #doc.format()
    doc.weave()

def spin(file, format = "md"):
    pass
