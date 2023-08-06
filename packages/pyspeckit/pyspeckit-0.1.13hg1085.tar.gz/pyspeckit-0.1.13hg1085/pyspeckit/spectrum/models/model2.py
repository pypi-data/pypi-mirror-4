"""
A flexible Spectral Model class.  Allows you to add and subtract, fix and unfix functions, etc.

Goal is to allow adding/subtracting/multiplying components...
(like these: https://astrophysics.gsfc.nasa.gov/XSPECwiki/Basic_single_dataset)
"""



class ModelComponent(object):
    def __init__(self, function, name, parameters=None, fixed=False):
        """
        Each Model object consists of a function...
        """
        self.function = function
        self.name = name
        self.parameters = parameters
        self.fixed = fixed

    def __call__(self, xaxis):
        """
        A model is defined over an X-axis.  It can do anything here, but must
        return an array of length len(xaxis).
        """

        return sum_of_model_functions

class AdditiveModelComponent(ModelComponent):
    pass
    
class MultiplicativeModelComponent(ModelComponent):
    pass
    

class Model(ModelComponent):
    """
    A model will consist of a sum of its children?

    """
    def __init__(self):
        """
        Generic model...
        """
        self.additive_components = []
        self.multiplicative_components = []

    def __call__(self):
        """
        Return sum/
        """

    def __add__(self, other):
        """
        Models can be added together
        """
        self.additive_components.append(other)

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
        self.multiplicative_components.append(other)
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
