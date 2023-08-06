#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


#
# A model maps from an input to an output.  This class is agnostic
# to how that mapping is performed.
#
class SystemModel:

    def __init__(self):
        self.vars = {}
        self.inputs = set()
        self.outputs = set()

    def eval(self, input_vars, debug=False):
        """
        This method takes an input dictionary, and returns an output dictionary.
        The keys for these dictionaries are a superset of the keys in the
        'inputs' and 'outputs' objects.
        """
        raise "pyomo::SystemModel - method 'eval()' has not been defined"
