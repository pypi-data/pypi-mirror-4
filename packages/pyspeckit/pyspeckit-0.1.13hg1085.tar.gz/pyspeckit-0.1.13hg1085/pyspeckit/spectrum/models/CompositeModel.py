"""
A flexible Spectral Model class.  Allows you to add and subtract, fix and unfix functions, etc.

Goal is to allow adding/subtracting/multiplying components...
(like these: https://astrophysics.gsfc.nasa.gov/XSPECwiki/Basic_single_dataset)
"""

import numpy as np


class ModelComponent(object):
    def __init__(self, function, name, parameters=None, fixed=False):
        """
        Each Model object consists of a function...
        """
        self.function = function
        self.name = name
        self.parameters = parameters
        self.fixed = fixed

    def __call__(self, xaxis, parameters):
        """
        A model is defined over an X-axis.  It can do anything here, but must
        return an array of length len(xaxis).
        """

        return self.function(xaxis, parameters)

        return sum_of_model_functions

class AdditiveModelComponent(ModelComponent):
    pass
    
class MultiplicativeModelComponent(ModelComponent):
    pass
    

class CompositeModel(ModelComponent):
    """
    A model will consist of a sum of its children?

    """
    def __init__(self):
        """
        Generic model...
        """
        self.additive_components = {}
        self.multiplicative_components = {}
        self.parameters = {}
        self.npars = 0

    def __call__(self, xaxis):
        """
        Return sum/
        """

        model = np.zeros(xaxis.shape)

        for name,func in additive_components.iteritems():
            #model += func(xaxis, ??parameters??)
            pass

    def __add__(self, other):
        """
        Models can be added together
        """
        self.additive_components[other.name] = other
        self.parameters[other.name] = other.parameters
        for ii in xrange(len(other.parameters)):
            self.parameters[self.npars+ii] = other.parameters[ii]
        self.npars += len(other.parameters)

        return self

    def __sub__(self, other):
        """
        Models can be removed
        """
        try:
            self.additive_components.remove(other)
        except ValueError:
            print "Can only remove components that have been included in the model"

        return self

    def __mul__(self, other):
        """
        Models can be added multiplicatively too
        """
        self.multiplicative_components[other.name] = other
        self.parameters[other.name] = other.parameters
        for ii in xrange(len(other.parameters)):
            self.parameters[self.npars+ii] = other.parameters[ii]
        self.npars += len(other.parameters)
        return self

    def __div__(self, other):
        """
        And models can be divided out
        """
        try:
            self.multiplicative_components.remove(other)
        except ValueError:
            print "Can only remove components that have been included in the model"

        return self


if __name__ == "__main__":
    # unit test

    test_xaxis = np.linspace(-5,5,100)
    test_spectrum = (np.exp(-(test_xaxis-1.2)**2/2.)*1.5 +
                    np.exp(-(test_xaxis-1.1)**2/(2.*1.5**2))*1.0 +
                    (6.0+test_xaxis*1.5) )

    import pyspeckit.spectrum.models as models

    # not implemented yet, but this is how it should work
    MyModel = CompositeModel()
    MyModel += Model(models.inherited_gaussfitter.gaussian,'gaussian1',params=[1,0,0])
    MyModel += Model(models.inherited_gaussfitter.gaussian,'gaussian2',params=[1,0,0])
    MyModel += Model(lambda x,m,b: m*x+b,'line1',params=[1,0])

    MyModel.fit(test_xaxis, data)
    MyModel.gaussian1.fixed[:] = True
