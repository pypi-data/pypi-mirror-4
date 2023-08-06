from CompositeModel import AdditiveModelComponent
from inherited_gaussfitter import gaussian

class GaussianModel(AdditiveModelComponent):
    def __init__(self, parameters=(1,0,1), fixed=(False,False,False), parameter_names=('amplitude','offset','width')):
        self.function = gaussian
        self.name = 'gaussian'
        self.parameters = parameters
        self.fixed=fixed
