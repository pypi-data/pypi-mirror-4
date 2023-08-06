#
# This example illustrates the architecture of an optimization application
# defined by Pysos, with a nontrivial example.
#
# This example considers a variant of the classic 'diet' problem, where
# the system model is aimed at designing a new category of food that can
# be profitably sold in an optimal diet.  Abstractly, this model attempts to
# maximize profit, while controlling the profit margin and the nutritional
# value of the target food.  We assume a simple linear model for the cost of
# the new target food: cost is a linear function of the amount of
# nutrients available in the food.
#

import coopr.pysos

#
# This class is used by the Application class to define the top-level
# optimization problem.
#
# This is a Coopr COLIN optimization problem, which treats
# a Pysos application as an optimization problem
#
class TopLevelProblem(coopr.opt.colin.MixedIntOptProblem):

    def __init__(self, app):
        """
        Constructor

        This defines a 2D continuous optimization problem, with lower bounds
        of zero and no upper bounds on the variables.

        For now, all of this is hard-coded here.  Eventually, I'd like to
        augment Pysos to support this formulation in a more generic manner.
        """
        coopr.opt.colin.MixedIntOptProblem.__init__(self)
        self.app=app
        self.real_lower=[   0.0, 0.0, 0.0, 0.0, 0.0]
        self.real_upper=[ 100.0, 100.0, 100.0, 100.0, 100.0 ]
        self.nreal=5

    def function_value(self, point):
        """
        The method that sets the decision variables from the
        current point, applies the application, and extracts
        the final value.
        """
        #
        # Validate the point being evaluated
        #
        self.validate(point)
        #
        # Set the decision variables in the application
        #
        self.app.decision_vars["percent_profit"] = point.reals[0]
        self.app.decision_vars["xA"] = point.reals[1]
        self.app.decision_vars["xB1"] = point.reals[2]
        self.app.decision_vars["xB2"] = point.reals[3]
        self.app.decision_vars["xC"] = point.reals[4]
        #
        # Iterate within the Pysos application.  We pass in the names of
        # the initial an final values to help manage the cache.
        #
        self.app.iterate(initial_values=["percent_profit","xA","xB1","xB2","xC"])
        #
        # Extract the variable 'f', which is the objective
        # used in the top-level optimization formulation
        #
        val = self.app.decision_vars["bought"]*self.app.decision_vars["profit_per_unit"]
        #
        # Update the cache with the value of this point
        #
        self.app.cache.add_response("profit",val)
        #
        # We're minimizing negative profit, since the Coopr
        # pattern searcher doesn't know how to maximize...
        #
        return -1.0*val



#
# This is the SoS application that uses TopLevelProblem and a
# Python optimizer (from coopr.opt) to optimize the SoS system.
#
class Application(coopr.pysos.OptimizationApplication):

    def __init__(self):
        """
        Constructor.  Setup the Coopr optimizer.
        """
        coopr.pysos.OptimizationApplication.__init__(self)
        self.opt = coopr.opt.colin.PatternSearch()
        self.opt.debug=True
        self.problem = TopLevelProblem(self)
        self.opt.min_delta=0.9
        self.opt.min_function_value=-10000.0

    def presolve(self):
        """
        Get the initial point
        """
        self.opt.initial_point = \
            [ self.get_decision_variable("percent_profit"),
              self.get_decision_variable("xA"),
              self.get_decision_variable("xB1"),
              self.get_decision_variable("xB2"),
              self.get_decision_variable("xC") ]


#
# A simple model that predicts the cost of manufacturing a type of food
# and the associated profit per unit sold.
#
class Model1(coopr.pysos.SystemModel):

    def __init__(self):
        """
        Constructor.  Setup the input and output variables.
        """
        coopr.pysos.SystemModel.__init__(self)
        self.inputs.add("percent_profit")
        self.inputs.add("xA")
        self.inputs.add("xB1")
        self.inputs.add("xB2")
        self.inputs.add("xC")
        self.outputs.add("cost")
        self.outputs.add("profit_per_unit")

    def eval(self, input_vars, debug=False):
        """
        Evaluate this mode:
        """
        output_vals={}
        tmp = 0.010 *(input_vars["xA"] + input_vars["xB1"] + input_vars["xB2"] + input_vars["xC"])
        output_vals["cost"] = tmp*(1.0+input_vars["percent_profit"]/100.0)
        output_vals["profit_per_unit"] = tmp*(input_vars["percent_profit"]/100.0)
        return [output_vals,output_vals]

#
# A Pysos model that computes an optimal diet for the consumer,
# for fixed costs.  This uses Pyomo to model the diet optimization
# problem, for which a new food type has been inserted based on
# the decision variables in the top-level model.
#
class Model2(coopr.pysos.PyomoModel):

    def __init__(self, *arg, **kwd):
        """
        Constructor.  Setup the input and output variables.
        """
        coopr.pysos.PyomoModel.__init__(self, *arg, **kwd)

    def import_inputs(self,input):
        """
        This method creates an AMPL *.dat file that overrides the default
        values provided in diet_tmp.dat
        """
        OUTPUT = open("diet_tmp.dat","w")
        OUTPUT.write("param new_cost := "+str(input["cost"])+" ;\n")
        OUTPUT.write("param new_amt := \n")
        OUTPUT.write("A " +str(input["xA"])+"\n")
        OUTPUT.write("B1 "+str(input["xB1"])+"\n")
        OUTPUT.write("B2 "+str(input["xB2"])+"\n")
        OUTPUT.write("C "+str(input["xC"])+"\n")
        OUTPUT.write(";\n")
        OUTPUT.close()
        return None

##
## MAIN - This is the main block of code executed
##

#
# Create the Pysos application
#
app = Application()
app.decision_variable("percent_profit",0.01)
app.decision_variable("xA",20)
app.decision_variable("xB1",30)
app.decision_variable("xB2",40)
app.decision_variable("xC",20)
app.decision_variable("cost",0.0)
app.decision_variable("profit_per_unit",0.0)
app.decision_variable("bought",0)
#
# Insert model instances into the Pysos application
#
app.set_model("m1", Model1())
m2_inputs={}
m2_inputs["cost"]="cost"
m2_inputs["xA"]="xA"
m2_inputs["xB1"]="xB1"
m2_inputs["xB2"]="xB2"
m2_inputs["xC"]="xC"
m2_outputs={}
m2_outputs["bought"]="new_Buy"
m2 = Model2(m2_inputs, m2_outputs, model="diet.py", data="diet_data.py")
m2.options=[]
app.set_model("m2", m2)
#
# Solve with debugging
#
app.solve(True)
print("Termination Status - "+str(app.termination_info))
#
# Print the cache of evaluated points, in different formats
#
print("")
print("Application Cache")
print("")
print("  FORMAT=simple")
print("")
app.cache.write(format="simple")
print("")
print("  FORMAT=verbose")
print("")
app.cache.write(format="verbose")
print("")
print("  FORMAT=csv")
print("")
app.cache.write(format="csv")
