"""
The wfc3tools module contains a function ``wf32d`` that calls the WF32D executable.
Use this function to facilitate batch runs or for the TEAL interface.


The wf32d primary functions include:
  * dark current subtraction
  * flat-fielding
  * photometric keyword calculations
  
Only those steps with a switch value of PERFORM in the input files will be executed, after which the switch
will be set to COMPLETE in the corresponding output files.

Examples
--------

    In Python without TEAL:

    >>> from wfc3tools import wf32d
    >>> calwf3.wf32d(filename)

    In Python with TEAL:

    >>> from stsci.tools import teal
    >>> from wfc3tools import wf32d
    >>> teal.teal('wf32d')

    In Pyraf:

    >>> import wfc3tools
    >>> epar wf32d

"""
# STDLIB
import os.path
import subprocess

#STSCI
from stsci.tools import parseinput
try:
    from stsci.tools import teal
except:
    teal = None
    
__taskname__ = "wf32d"
__version__ = "1.0"
__vdate__ = "03-Jan-2013"

def wf32d(input, output="", dqicorr="PERFORM", darkcorr="PERFORM",flatcorr="PERFORM",
        shadcorr="PERFORM", photcorr="PERFORM", verbose=False, quiet=True ):
    """
    
    Run the ``wf32d.e`` executable as from the shell. For more information on CALWF3
    see the WFC3 Data Handbook at http://www.stsci.edu/hst/wfc3/documents/handbooks/currentDHB/
    

    Parameters:
    
        input : str
            Name of input files

                * a single filename (``iaa012wdq_raw.fits``)
                * a Python list of filenames
                * a partial filename with wildcards (``\*raw.fits``)
                * filename of an ASN table (``\*asn.fits``)
                * an at-file (``@input``) 

        output: str
            Name of the output FITS file.

        dqicorr: str, "PERFORM/OMIT", optional
            Update the dq array from bad pixel table

        darkcorr: str, "PERFORM/OMIT", optional
            Subtract the dark image

        flatcorr: str, "PERFORM/OMIT", optional
            Multiply by the flatfield image

        shadcorr: str, "PERFORM/OMIT", optional
            Correct for shutter shading (CCD)

        photcorr: str, "PERFORM/OMIT", optional
            Update photometry keywords in the header

        verbose: bool, optional
            Print verbose time stamps?

        quiet: bool, optional
            Print messages only to trailer file?
        
  
    """
    call_list = ['wf32d.e']

    infiles, dummpy_out= parseinput.parseinput(input)
    call_list.append(','.join(infiles))
    
    if verbose:
        call_list.append('-v -t')

 
    if debug:
        call_list.append('-d')
        
    if (darkcorr == "PERFORM"):
        call_list.append('-dark')
    
    if (dqicorr == "PERFORM"):
        call_list.append('-dqi')
        
    if (flatcorr == "PERFORM"):
        call_list.append('-flat')
        
    if (shadcorr == "PERFORM"):
        call_list.append('-shad')
        
    if (photcorr == "PERFORM"):
        call_list.append('-phot')

    subprocess.call(call_list)


def help(file=None):
    helpstr = getHelpAsString(docstring=True)
    if file is None:
        print helpstr
    else:
        if os.path.exists(file): os.remove(file)
        f = open(file,mode='w')
        f.write(helpstr)
        f.close()
    

def getHelpAsString(docstring=False):
    """
    Returns documentation on the 'wf32d' function. Required by TEAL.

    return useful help from a file in the script directory called
    __taskname__.help

    """

    install_dir = os.path.dirname(__file__)
    htmlfile = os.path.join(install_dir, 'htmlhelp', __taskname__ + '.html')
    helpfile = os.path.join(install_dir, __taskname__ + '.help')
    if docstring or (not docstring and not os.path.exists(htmlfile)):
        helpString = ' '.join([__taskname__, 'Version', __version__,
                               ' updated on ', __vdate__]) + '\n\n'
        if os.path.exists(helpfile):
            helpString += teal.getHelpFileAsString(__taskname__, __file__)
    else:
        helpString = 'file://' + htmlfile

    return helpString


wf32d.__doc__ = getHelpAsString(docstring=True)


def run(configobj=None):
    """
    TEAL interface for the ``wf32d`` function.

    """
    wf32d(configobj['input'],
           output=configobj['output'],
           dqicorr=configobj['dqicorr'],
           darkcorr=configobj['darkcorr'],
           flatcorr=configobj['flatcorr'],
           shadcorr=configobj['shadcorr'],
           photcorr=configobj['photcorr'],
           quiet=configobj['quiet'],
           verbose=configobj['verbose'],
           debug=configobj['debug'])

