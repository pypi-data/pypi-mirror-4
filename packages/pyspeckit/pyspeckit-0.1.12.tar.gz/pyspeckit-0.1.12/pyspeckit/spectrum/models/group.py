"""
============
Group Fitter
============

Given a group of lines with fixed wavelengths / frequencies, fit them all with
independent peaks and widths.

"""
import model
import numpy 
from inherited_gaussian import gaussian

def group_fitter(multisingle='multi'):
    """
    Generator for Gaussian fitter class
    """

    raise NotImplementedError('Line group fitting is not implemented yet')

    myclass =  model.SpectralModel(gaussian, 3,
            parnames=['amplitude','shift','width'], 
            parlimited=[(False,False),(False,False),(True,False)], 
            parlimits=[(0,0), (0,0), (0,0)],
            shortvarnames=('A',r'\Delta x',r'\sigma'),
            multisingle=multisingle,
            )
    myclass.__name__ = "gaussian"
    
    return myclass
