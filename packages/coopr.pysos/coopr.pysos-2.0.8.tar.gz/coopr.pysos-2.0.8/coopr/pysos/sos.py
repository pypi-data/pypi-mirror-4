#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys

#
# A cache for a application data
#
# This is not quite as general as I'd like, but it works for now...
#
class ApplicationCache(object):

    def __init__(self):
        self.curr = None
        self.data = {}
        self.keys = []
        self.descr = []

    def add_response(self,name,value):
        if not "response" in self.data[self.curr]:
            self.data[self.curr]["response"]={}
        self.data[self.curr]["response"][name] = value

    def set_top_level(self,key,descr=None):
        if not descr is None:
            self.descr=descr
        ndx = tuple(key)
        if not ndx in self.data:
            #
            # For now, we do not attempt to reuse this cache'd info.
            #
            self.keys.append(ndx)
        self.data[ndx] = {}
        self.curr = ndx

    def add_model_data(self,model,data):
        if self.curr is None:
            raise KeyError("No top-level key has been specified")
        self.data[self.curr][model] = data

    def write(self, file=None, format="verbose"):
        if format=="simple":
            iter=0
            for key in self.keys:
                print_item = str(iter)+" "
                for val in key:
                    print_item += str(val)+" "
                for model in self.data[key]:
                    if model is "response":
                        continue
                    for item in self.data[key][model]:
                        print_item += str(self.data[key][model][item])+" "
                if "response" in self.data[key]:
                    for item in self.data[key]["response"]:
                        print_item += str(self.data[key]["response"][item])+" "
                iter=iter+1
                print(print_item)
        elif format=="verbose":
            iter=0
            for key in self.keys:
                sys.stdout.write("iter="+str(iter))
                i=0
                for val in key:
                    sys.stdout.write(" "+self.descr[i]+"="+str(val))
                    i=i+1
                for model in self.data[key]:
                    if model is "response":
                        continue
                    for item in self.data[key][model]:
                        sys.stdout.write(" "+model+"."+item+"="+str(self.data[key][model][item]))
                if "response" in self.data[key]:
                    for item in self.data[key]["response"]:
                        sys.stdout.write(" response."+item+"="+str(self.data[key]["response"][item]))
                iter=iter+1
                sys.stdout.write("\n")
        elif format=="csv":
            #
            # Dummy iteration, to print the header
            #
            for key in self.keys:
                sys.stdout.write("iter")
                for name in self.descr:
                    sys.stdout.write(","+name)
                for model in self.data[key]:
                    if model is "response":
                        continue
                    for item in self.data[key][model]:
                        sys.stdout.write(","+model+"."+item)
                if "response" in self.data[key]:
                    for item in self.data[key]["response"]:
                        sys.stdout.write(",response."+item)
                sys.stdout.write("\n")
                break
            #
            # Iterate through the data
            #
            iter=0
            for key in self.keys:
                sys.stdout.write(str(iter))
                i=0
                for val in key:
                    sys.stdout.write(","+str(val))
                    i=i+1
                for model in self.data[key]:
                    if model is "response":
                        continue
                    for item in self.data[key][model]:
                        sys.stdout.write(","+str(self.data[key][model][item]))
                if "response" in self.data[key]:
                    for item in self.data[key]["response"]:
                        sys.stdout.write(","+str(self.data[key]["response"][item]))
                iter=iter+1
                sys.stdout.write("\n")


#
# A system-of-systems application, which is solved by iteratively
# calling sub-system models
#
class SoSApplication(object):

    def __init__(self):
        self.model_names = []
        self.models = {}
        self.state_vars = {}
        self.state_var_names = []
        self.decision_vars = {}
        self.decision_var_names = []
        self.model_vals = {}
        self.objective_val = None
        self.min_objective_value = None
        self.termination_info = "unknown"
        self.cache = ApplicationCache()

    def decision_variable(self, name, init_value=None):
        self.decision_vars[name] = init_value
        self.decision_var_names.append(name)

    def get_decision_variable(self, name):
        return self.decision_vars[name]

    def state_variable(self, name, init_value):
        self.state_vars[name] = init_value
        self.state_var_names.append(name)

    def get_state_variable(self, name):
        return self.state_vars[name]

    def set_model(self, name, model):
        model.cache=self.cache
        self.models[name] = model
        self.model_names.append(name)

    def set_objective(self, name):
        self.objective_name = name

    def solve(self):
        """
        This analyzes the SoS to find a set of decision variables that
        (1) satisfy sub-system constraints and (2) optimize the
        SoS objective.
        """
        raise ValueError("pyomo::SystemModel - method 'solve()' has not been defined")

    def apply_model(self,name,debug=False):
        #
        # Generate the table of inputs for the model
        #
        input = {}
        model = self.models[name]
        for inp in model.inputs:
            try:
                val = self.state_vars[inp]
            except KeyError:
                try:
                    val = self.decision_vars[inp]
                except:
                    raise ValueError("SoSApplication::apply_model - unknown input " + str(inp) + " required by model " + str(name))
            input[inp] = val
        #
        # Apply the model to generate a table of outputs
        #
        if debug:
            print("  Model Input Variables:")
            if len(input.keys()) > 0:
                for key in input.keys():
                    print("    "+key+" "+str(input[key]))
            else:
                print("    None")
        output_vars = {}
        output_vals = {}
        [output_vars, output_vals]=model.eval(input,debug)
        if debug:
            print("  Model Output Variables:")
            for key in output_vars.keys():
                print("    "+key+" "+str(output_vars[key]))
            print("  Model Output Values:")
            for key in output_vals.keys():
                print("    "+key+" "+str(output_vals[key]))
        self.cache.add_model_data(name,output_vals)
        return [output_vars,output_vals]

#
# A SoS application that iteratively calls each model, and
# terminates if a new/improving solution is not generated
#
class IterativeRefinementApplication(SoSApplication):

    def __init__(self):
        SoSApplication.__init__(self)

    def compute_objective(self):
        self.objective_val = self.model_vals[ self.model_names[-1] ][self.objective_name]

    def solve(self, debug=False):
        """
        This analyzes the SoS to find a set of decision variables that
        (1) satisfy sub-system constraints and (2) optimize the
        SoS objective.

        An iterative refinement strategy is used.  Each model is analyzed
        iterative, until all have been done.  The search process is teriminated
        if the SoS objective has not changed.
        """
        i=1
        while True:
            if debug:
                print("------------------------------------------------------")
                print("------------------------------------------------------")
                print("Iteration: "+str(i))
                print("------------------------------------------------------")
                print("------------------------------------------------------")
            for model_name in self.model_names:
                if debug:
                    print("------------------------------------------------------")
                    print("Analyzing Model: "+str(model_name))
                    print("------------------------------------------------------")
                    print("Application Inputs: State Variables")
                    for key in self.state_var_names:
                        print("  "+key+" "+str(self.state_vars[key]))
                [output,model_info] = self.apply_model(model_name, debug=debug)
                #
                # Update the application data
                #
                for key in output.keys():
                    if self.decision_vars.has_key(key):
                        self.decision_vars[key] = output[key]
                for key in model_info.keys():
                    if self.decision_vars.has_key(key):
                        self.decision_vars[key] = model_info[key]
                #
                # Cache the model info
                #
                self.model_vals[model_name] = model_info
                foo = raw_input("Pausing for data")
            #
            # Update the objective and
            #
            prev_objective = self.objective_val
            self.compute_objective()
            if debug:
                print("Objective: " + str(self.objective_val))
                print("Application Outputs: State Variables")
                for key in self.state_var_names:
                    print("  "+key+" "+str(self.state_vars[key]))
                print("Application Outputs: Decision Variables")
                for key in self.decision_var_names:
                    print("  "+key+" "+str(self.decision_vars[key]))
            if prev_objective is not None and \
               abs(prev_objective-self.objective_val) < 1e-3:
                self.termination_info = "Objective difference is small: " + str(abs(prev_objective-self.objective_val)) + " < 1e-3"
                break
            if self.min_objective_value is not None and \
               self.objective_val < self.min_objective_value:
                self.termination_info = "Objective is small: " + str(self.objective_val) + " < " + str(self.min_objective_value)
                break
            i=i+1
            if debug:
                print("")
            foo = raw_input("Pausing for data")
