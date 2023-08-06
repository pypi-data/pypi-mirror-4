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
# A system model that uses a Pyomo model
#
# Note: for now, this reconstructs the model instance.  Later, we could
# try to setup an incremental instance creation process.
#

import os
import coopr
import coopr.pyomo.scripting.pyomo
from .model import SystemModel

class PyomoModel(SystemModel):
    def __init__(self,inputs,outputs,model=None,data=None,options=["--debug=instance","--summary"]):
        """
        Construct the model
        """
        SystemModel.__init__(self)
        #
        # Set the inputs/outputs of this model
        #
        self.input_map = inputs
        for name in inputs.keys():
            self.inputs.add(name)
        self.output_map = outputs
        for name in outputs.keys():
            self.outputs.add(name)
        #
        # Set Pyomo solver options
        #
        self.options=options
        #
        # Set the Pyomo model and data file
        #
        if model[1] == ":" or model[0] == "/":
            self.model=model
        else:
            self.model=os.getcwd() + os.sep +model
        if data[1] == ":" or data[0] == "/":
            self.data=data
        else:
            self.data=os.getcwd() + os.sep +data
        if self.model is None:
            raise ValueError("Cannot create a PyomoModel without a model name")


    def import_inputs(self,input):
        """
        Initialize this model with the input data.
        If this function returns None, then input data is ignored
        """
        return None

    def export_outputs(self,modified_inputs,outputs):
        """
        Archive output values.

        This could take the form of a file, printing out the values, or
        filling in values in a spreadsheet.
        """
        return None

    def get_results(self, instance, input_keys, output_keys):
        """
        A default implementation of the method used to get model results

        This implementation returns None input and output values.
        """
        inputs={}
        for key in input_keys:
            inputs[key] = None
        outputs={}
        for key in output_keys:
            outputs[key] = self.results.solution(0).variable[output_keys[key]]
        for (name,val) in self.results.solution(0).variable:
            outputs[name] = val
        return [inputs,outputs]

    def eval(self, input, debug=False):
        """
        Create the Pyomo instance and perform optimization
        """
        modified_input={}
        output={}
        #
        # Create a temporary data file
        #
        tmpdata = self.import_inputs(input)
        #
        # Setup and solve the model using the Pyomo script
        #
        args=self.options+[self.model]
        if self.data is not None:
            args.append(self.data)
        [self.instance,self.results] = coopr.pyomo.scripting.pyomo.run(args)
        #
        # Get modified input and output values
        #
        [modified_input, output] = self.get_results(self.instance, self.input_map, self.output_map)
        #
        # Export inputs and outputs
        #
        self.export_outputs(modified_input, output)
        #
        # Return
        #
        return [modified_input,output]
