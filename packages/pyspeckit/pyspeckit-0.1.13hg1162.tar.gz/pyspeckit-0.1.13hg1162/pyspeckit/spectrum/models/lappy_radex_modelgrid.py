"""
Fit a line based on parameters output from a grid of RADEX models
"""
import numpy as np
from mpfit import mpfit
from .. import units
from . import fitter,model
import matplotlib.cbook as mpcb
import copy

