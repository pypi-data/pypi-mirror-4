
#
#       convenience.py
#
#       Copyright 2010 alex arsenovic <arsenovic@virginia.edu>
#       Copyright 2010 lihan chen
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later versionpy.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

'''

.. currentmodule:: skrf.convenience
========================================
convenience (:mod:`skrf.convenience`)
========================================

Holds pre-initialized objects's and functions that are general
conveniences.


Plotting 
------------
.. autosummary::
   :toctree: generated/

   save_all_figs
   add_markers_to_lines
   legend_off
   func_on_all_figs
   
IO
----
.. autosummary::
   :toctree: generated/
    
    hfss_touchstone_2_media
    hfss_touchstone_2_gamma_z0

General 
------------
.. autosummary::
   :toctree: generated/

   now_string
   find_nearest
   find_nearest_index



Pre-initialized Objects
--------------------------

:class:`~skrf.frequency.Frequency` Objects
==============================================
These are predefined :class:`~skrf.frequency.Frequency` objects
that correspond to standard waveguide bands. This information is taken
from the VDI Application Note 1002 [#]_ . The naming convenction is
f_wr# where '#' is the band number.


=======================  ===============================================
Object Name              Description
=======================  ===============================================
f_wr10                   WR-10, 75-110 GHz
f_wr3                    WR-3, 220-325 GHz
f_wr2p2                  WR-2.2, 330-500 GHz
f_wr1p5                  WR-1.5, 500-750 GHz
f_wr1                    WR-1, 750-1100 GHz
=======================  ===============================================


:class:`~skrf.media.media.Media` Objects
==============================================
These are predefined :class:`~skrf.media.media.Media` objects
that represent Standardized transmission line media's. This information

Rectangular Waveguide Media's
++++++++++++++++++++++++++++++++++

:class:`~skrf.media.rectangularWaveguide.RectangularWaveguide`
Objects for standard bands.

=======================  ===============================================
Object Name              Description
=======================  ===============================================
wr10                     WR-10, 75-110 GHz
wr3                      WR-3, 220-325 GHz
wr2p2                    WR-2.2, 330-500 GHz
wr1p5                    WR-1.5, 500-750 GHz
wr1                      WR-1, 750-1100 GHz
=======================  ===============================================

Shorthand Names 
----------------

Below is a list of shorthand object names which can be use to save some 
typing. These names are defined in the main __init__ module. but listing
them here makes more sense. 


============ ================
Shorthand    Full Object Name   
============ ================
F            :class:`~skrf.frequency.Frequency`
N            :class:`~skrf.network.Network`
NS           :class:`~skrf.networkSet.NetworkSet`
M            :class:`~skrf.media.media.Media`
C            :class:`~skrf.calibration.calibration.Calibration`
============ ================

The following are shorthand names for commonly used, but unfortunately
longwinded functions.

============ ================
Shorthand    Full Object Name   
============ ================
lat          :func:`~skrf.network.load_all_touchstones`
saf          :func:`~skrf.convenience.save_all_figs`
============ ================
 



References
-------------
.. [#] VDI Application Note:  VDI Waveguide Band Designations (VDI-1002) http://vadiodes.com/VDI/pdf/waveguidechart200908.pdf
'''


from network import *
from frequency import Frequency
from media import RectangularWaveguide, Media
import mathFunctions as mf

import warnings
import os
import pylab as plb
import numpy as npy
from scipy.constants import mil
from datetime import datetime


# pre-initialized classes

#frequency bands
f_wr10  = Frequency(75,110,201, 'ghz')
f_wr3   = Frequency(220,325,201, 'ghz')
f_wr2p2 = Frequency(330,500,201, 'ghz')
f_wr1p5 = Frequency(500,750,201, 'ghz')
f_wr1   = Frequency(750,1100,201, 'ghz')

# rectangular waveguides
wr10    = RectangularWaveguide(Frequency(75,110,201, 'ghz'), 100*mil,z0=50)
wr3     = RectangularWaveguide(Frequency(220,325,201, 'ghz'), 30*mil,z0=50)
wr2p2   = RectangularWaveguide(Frequency(330,500,201, 'ghz'), 22*mil,z0=50)
wr1p5   = RectangularWaveguide(Frequency(500,750,201, 'ghz'), 15*mil,z0=50)
wr1     = RectangularWaveguide(Frequency(750,1100,201, 'ghz'), 10*mil,z0=50)



## Functions
# Ploting
def save_all_figs(dir = './', format=['eps','pdf','png']):
    '''
    Save all open Figures to disk.

    Parameters
    ------------
    dir : string
            path to save figures into
    format : list of strings
            the types of formats to save figures as. The elements of this
            list are passed to :matplotlib:`savefig`. This is a list so that
            you can save each figure in multiple formats.
    '''
    if dir[-1] != '/':
        dir = dir + '/'
    for fignum in plb.get_fignums():
        fileName = plb.figure(fignum).get_axes()[0].get_title()
        if fileName == '':
            fileName = 'unamedPlot'
        for fmt in format:
            plb.savefig(dir+fileName+'.'+fmt, format=fmt)
            print (dir+fileName+'.'+fmt)

def add_markers_to_lines(ax=None,marker_list=['o','D','s','+','x'], markevery=10):
    '''
    adds markers to existing lings on a plot 
    
    this is convinient if you have already have a plot made, but then 
    need to add markers afterwards, so that it can be interpreted in 
    black and white. The markevery argument makes the markers less 
    frequent than the data, which is generally what you want. 
    
    Parameters
    -----------
    ax : matplotlib.Axes
        axis which to add markers to, defaults to gca()
    marker_list : list of marker characters
        see matplotlib.plot help for possible marker characters
    markevery : int
        markevery number of points with a marker.
    
    '''
    if ax is None:
        ax=plb.gca()
    lines = ax.get_lines()
    if len(lines) > len (marker_list ):
        marker_list *= 3
    [k[0].set_marker(k[1]) for k in zip(lines, marker_list)]
    [line.set_markevery(markevery) for line in lines]

def legend_off(ax=None):
    '''
    turn off the legend for a given axes. 
    
    if no axes is given then it will use current axes.
    
    Parameters
    -----------
    ax : matplotlib.Axes object
        axes to operate on 
    '''
    if ax is None:
        plb.gca().legend_.set_visible(0)
    else:
        ax.legend_.set_visible(0)

def plot_complex(z,*args, **kwargs):
    '''
    plots a complex array or list in real vs imaginary.
    '''
    plb.plot(npy.array(z).real,npy.array(z).imag, *args, **kwargs)


def func_on_all_figs(func, *args, **kwargs):
    '''
    runs a function after making all open figures current. 
    
    useful if you need to change the properties of many open figures 
    at once, like turn off the grid. 
    
    Parameters
    ----------
    func : function
        function to call
    \*args, \*\*kwargs : pased to func
    
    Examples
    ----------
    >>> rf.func_on_all_figs(grid,alpha=.3)
    '''
    for fig_n in plb.get_fignums():
        fig = plb.figure(fig_n)
        for ax_n in fig.axes:
            fig.add_axes(ax_n) # trick to make axes current
            func(*args, **kwargs)
            plb.draw()

# other
def now_string():
    '''
    returns a unique sortable string, representing the current time
    
    nice for generating date-time stamps to be used in file-names 
    
    '''
    return datetime.now().__str__().replace('-','.').replace(':','.').replace(' ','.')

def find_nearest(array,value):
    '''
    find nearest value in array.
    
    taken from  http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array

    Parameters
    ----------
    array :  numpy.ndarray
        array we are searching for a value in 
    value : element of the array
        value to search for 
    
    Returns
    --------
    found_value : an element of the array 
        the value that is numerically closest to `value`
    
    '''
    idx=(npy.abs(array-value)).argmin()
    return array[idx]

def find_nearest_index(array,value):
    '''
    find nearest value in array.
    
    Parameters
    ----------
    array :  numpy.ndarray
        array we are searching for a value in 
    value : element of the array
        value to search for 
    
    Returns
    --------
    found_index : int 
        the index at which the  numerically closest element to `value`
        was found at
    
    
    taken from  http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array

    '''
    return (npy.abs(array-value)).argmin()


def hfss_touchstone_2_gamma_z0(filename):
    '''
    Extracts Z0 and Gamma comments from touchstone file
    
    Takes a HFSS-style touchstone file with Gamma and Z0 comments and 
    extracts a triplet of arrays being: (frequency, Gamma, Z0)
    
    Parameters
    ------------
    filename : string 
        the HFSS-style touchstone file
    
    
    Returns
    --------
    f : numpy.ndarray
        frequency vector (in Hz)
    gamma : complex numpy.ndarray
        complex  propagation constant
    z0 : numpy.ndarray
        complex port impedance
    
    Examples
    ----------
    >>> f,gamm,z0 = rf.hfss_touchstone_2_gamma_z0('line.s2p')
    '''
    ntwk = Network(filename)
    f= open(filename)
    gamma, z0 = [],[]
    
    def line2ComplexVector(s):
        return mf.scalar2Complex(\
            npy.array(\
                [k for k in s.strip().split(' ') if k != ''][ntwk.nports*-2:],\
                dtype='float'
                )
            )
            
    for line in f:
        if '! Gamma' in line:
            gamma.append(line2ComplexVector(line))
        if '! Port Impedance' in line:
            z0.append(line2ComplexVector(line))
    
    if len (z0) ==0:
        raise(ValueError('Touchstone does not contain valid gamma, port impedance comments'))
        
    return ntwk.frequency.f, npy.array(gamma), npy.array(z0)

def hfss_touchstone_2_media(filename, f_unit='ghz'):
    '''
    Creates a :class:`~skrf.media.media.Media` object from a a HFSS-style touchstone file with Gamma and Z0 comments 
    
    Parameters
    ------------
    filename : string 
        the HFSS-style touchstone file
    f_unit : ['hz','khz','mhz','ghz']
        passed to f_unit parameters of Frequency constructor
    
    Returns
    --------
    my_media : skrf.media.Media object
        the transmission line model defined by the gamma, and z0 
        comments in the HFSS file.
    
    Examples
    ----------
    >>> port1_media, port2_media = rf.hfss_touchstone_2_media('line.s2p')
    
    See Also
    ---------
    hfss_touchstone_2_gamma_z0 : returns gamma, and z0 
    '''
    f, gamma, z0 = hfss_touchstone_2_gamma_z0(filename)
    
    freq = Frequency.from_f(f)
    freq.unit = f_unit
    
    
    media_list = []
    
    for port_n in range(gamma.shape[1]):
        media_list.append(\
            Media(
                frequency = freq, 
                propagation_constant =  gamma[:, port_n],
                characteristic_impedance = z0[:, port_n]
                )
            )
        
        
    return media_list 

## file conversion
def statistical_2_touchstone(file_name, new_file_name=None,\
        header_string='# GHz S RI R 50.0'):
    '''
    Cvonverts Statistical file to a touchstone file. 
    
    Converts the file format used by Statistical and other Dylan Williams
    software to standard touchstone format.

    Parameters
    ------------
    file_name : string
            name of file to convert
    new_file_name : string
            name of new file to write out (including extension)
    header_string : string
            touchstone header written to first beginning of file

    '''
    if new_file_name is None:
        new_file_name = 'tmp-'+file_name
        remove_tmp_file = True

    old_file = file(file_name,'r')
    new_file = open(new_file_name,'w')
    new_file.write('%s\n'%header_string)
    for line in old_file:
        new_file.write(line)
    new_file.close()
    old_file.close()

    if remove_tmp_file is True:
        os.rename(new_file_name,file_name)


## script templates
script_templates = {}
script_templates['cal_gen_ideals'] = \
'''
from pylab import *
from scipy.constants import *
import skrf as rf

################################# INPUT ################################
media_type = 'RectangularWaveguide'
media_kwargs ={'a':10*mil}
f_unit = 'thz'

measured_dir = '.'
measured_names =['short', 'delay short', 'match']
ideals = [\
    ['short',
        {'name':'short'} ],
    ['delay_short',
        {'name':'delay short', 'd': 106*micron } ],
    ['match',
        {'name':'match'} ],
    ]

########################################################################


measured_dict = rf.load_all_touchstones(measured_dir,f_unit=f_unit)
frequency = measured_dict.values()[0].frequency
media = rf.__getattribute__(media_type)(frequency, **media_kwargs)

cal = rf.Calibration(
    ideals = [ media.__getattribute__(k[0])(**k[1]) for k in ideals[:] ],
    measured = [ measured_dict[k] for k in measured_names ]
    )
'''
script_templates['cal'] = \
'''
from pylab import *
from scipy.constants import *
import skrf as rf

################################# INPUT ################################
measured_dir = ''
ideals_dir = ''
ideals_names = ['','','']
measured_names = ['','','']
f_unit = 'ghz'
########################################################################


measured_dict = rf.load_all_touchstones(measured_dir,f_unit=f_unit)
ideals_dict = rf.load_all_touchstones(measured_dir,f_unit=f_unit)
frequency = measured_dict.values()[0].frequency
[ideals_dict[k].resample(frequency.npoints) for k in ideals_dict]

cal = rf.Calibration(
    ideals = [ideals_dict[k] for k in ideals_names],
    measured = [measured_dict[k] for k in measured_names],
    )
'''

def script_template(template_name, file_name='skrf_script.py', \
        overwrite=False, *args, **kwargs):
    '''
    creates skrf scripts based on templates

    Parameters
    -----------
    template_name : string ['cal', 'cal_gen_ideals']
            name of template to use
    file_name : string
            name of script file to write
    overwrite : Boolean
            if file_name exists should it be overwritten
    \*args, \*\*kwargs : arguments and keyword arguments
            passed to open()
    '''
    if template_name not in script_templates.keys():
        raise(ValueError('\'%s\' not valid template_name'%template_name))

    if os.path.isfile(file_name) and overwrite is False:
        warnings.warn('%s exists, and `overwrite` is False, abort. '\
                %file_name)
    else:
        script_file = open(file_name, 'w')
        script_file.write(script_templates[template_name])
        script_file.close()


