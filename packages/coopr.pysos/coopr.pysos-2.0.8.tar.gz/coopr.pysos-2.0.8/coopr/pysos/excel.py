#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

##
## See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440661/index_txt
##

#
# A system model that uses an Excel spreadsheet
#

import os
from .model import SystemModel
import coopr.pysos
try:
    from pythoncom import CoInitialize, CoUninitialize, pywintypes
except ImportError:
    pass


class ExcelModel(SystemModel):

    def __init__(self,spreadsheet,inputs,outputs):
        """Construct the model"""
        SystemModel.__init__(self)
        #
        # Set the inputs/outputs of this spreadsheet
        #
        self.input_map = inputs
        for name in inputs.keys():
            self.inputs.add(name)
        self.output_map = outputs
        for name in outputs.keys():
            self.outputs.add(name)
        #
        # Start the excel spreadsheet
        #
        self.xl = spreadsheet

    def calculate(self):
        pass

    def set_inputs(self, input):
        for name in input.keys():
            ##print self.input_map[name]
            if type(self.input_map[name]) is tuple:
                self.xl.ws().Cells( self.input_map[name][0], self.input_map[name][1] ).Value = input[name]
            else:
                self.xl.set_range(self.input_map[name],input[name])

    def get_inputs(self):
        modified_input={}
        for name in self.input_map.keys():
            if type(self.input_map[name]) is tuple:
                modified_input[name] = self.xl.ws().Cells( self.input_map[name][0], self.input_map[name][1] ).Value
            elif isinstance(self.input_map[name],basestring):
                try:
                    modified_input[name] = self.xl.get_range(self.input_map[name])
                except pywintypes.com_error:
                    raise ValueError("Problem reading range "+self.input_map[name]+" from spreadsheet "+self.xl.xlsfile)
            else:
                raise ValueError("Unknown type "+str(type(self.input_map[name]))+" for input "+str(name))
        return modified_input

    def eval(self, input, debug=False):
        """Evaluate the spreadsheet"""
        if input.keys() != self.input_map.keys():
            raise ValueError("The input keys do not match the input_map keys!")
        #
        # Set the values in the spreadsheet
        #
        self.set_inputs(input)
        #
        # Perform the appropriate calculation
        # By default, this is function does nothing, but it can be
        # overridden for a given application.
        #
        self.calculate()
        #
        # Get the (possibly modified) input values
        #
        modified_input = self.get_inputs()
        #
        # Get output values
        #
        output = self.get_outputs()
        #
        # Return
        #
        return [modified_input,output]

    def get_outputs(self):
        """
        Method for getting output values
        """
        output={}
        for name in self.output_map.keys():
            if type(self.output_map[name]) is tuple:
                output[name] = self.xl.ws().Cells( self.output_map[name][0], self.output_map[name][1] ).Value
            elif isinstance(self.output_map[name],basestring):
                try:
                    output[name] = self.xl.get_range(self.output_map[name])
                except pywintypes.com_error as err:
                    raise ValueError("Problem reading range "+self.output_map[name]+" from spreadsheet "+self.xl.xlsfile)
            else:
                raise ValueError("Unknown type "+str(type(self.output_map[name]))+" for output "+str(name))
        return output
