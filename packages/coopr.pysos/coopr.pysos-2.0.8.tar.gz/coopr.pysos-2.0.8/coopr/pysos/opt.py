#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


from . import sos


#
# A SoS application that performs optimization, using call-backs to
# the application object to do the optimization 'work'.
#
class OptimizationApplication(sos.SoSApplication):

    def __init__(self):
        sos.SoSApplication.__init__(self)
        self.opt = None
        self.problem = None
        self.debug_iteration=False

    def presolve(self):
        pass

    def iterate(self, debug_iteration=False, initial_values=None, final_values=None):
        """
        This iterates through the models in an SoS.  We assume that this
        iteration processes the model data to result in a final solution
        and solution value.
        """
        if not initial_values is None:
            tmp=[]
            for name in initial_values:
                tmp.append(self.decision_vars[name])
            self.cache.set_top_level( tmp, descr=initial_values )
        debug = self.debug_iteration or debug_iteration
        if debug:
            print("------------------------------------------------------")
            print("------------------------------------------------------")
            print("SoS Iteration: ")
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
        if debug:
            print("Application Outputs: State Variables")
            for key in self.state_var_names:
                print("  "+key+" "+str(self.state_vars[key]))
            print("Application Outputs: Decision Variables")
            for key in self.decision_var_names:
                print("  "+key+" "+str(self.decision_vars[key]))
        #
        # Cache the final values
        #
        if not final_values is None:
            for val in final_values:
                self.cache.add_response(val, model_info[val])

    def solve(self, debug=False):
        """
        Apply a Coopr optimizer
        """
        self.presolve()
        self.debug_iteration=debug
        self.opt.problem=self.problem
        self.opt.reset()
        self.results = self.opt.solve()
        print("------------------------------------------------------")
        print("------------------------------------------------------")
        print(" Final Optimization Results: ")
        print("------------------------------------------------------")
        print("------------------------------------------------------")
        self.results.write()
