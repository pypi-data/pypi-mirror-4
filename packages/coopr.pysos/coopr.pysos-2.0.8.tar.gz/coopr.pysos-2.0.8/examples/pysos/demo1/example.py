#
# This example illustrates the basic architecture of an optimization application
# defined by Pysos.
#
# This example uses three "system models":
#  * A top-level system, defined by two continuous variables
#  * Two sub-system models that are coordinated with Pysos
#
# Mathematically, this model can be viewed as computing:
#   s2(s1(x1,x2))
# where
#   s1 - the first subsystem        s1:R^2 -> R^2
#   s2 - the second subsystem       s2:R^2 -> R
#
# This application is equivalent to minimizing the function:
#
#   f(x1,x2) = x1*x2*(x1+x2)
#
# where
#   -1 <= x1 <= 1
#    1 <= x2 <= 2
#
# A SoSApplication object is used to coordinate the execution of these models,
# and to apply an optimization solver to iterate through the top-level
# decision variables.
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
        self.real_lower=[ -1.0, 1.0]
        self.real_upper=[  1.0, 2.0]
        self.nreal=2

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
        self.app.decision_vars["x1"] = point.reals[0]
        self.app.decision_vars["x2"] = point.reals[1]
        #
        # Iterate within the Pysos application.  We pass in the names of
        # the initial an final values to help manage the cache.
        #
        self.app.iterate(initial_values=["x1","x2"], final_values=["f"])
        #
        # Extract the variable 'f', which is the objective
        # used in the top-level optimization formulation
        #
        val = self.app.decision_vars["f"]
        return val



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
        self.opt.min_delta=0.1
        self.opt.min_function_value=-100.0

    def presolve(self):
        """
        Get the initial point
        """
        self.opt.initial_point = \
            [ self.get_decision_variable("x1"),
              self.get_decision_variable("x2") ]


#
# A simple model that generates y1 and y2 output values
# with the following values:
#
#   y1=x1*x2
#   y2=x1+x2
#
class Model1(coopr.pysos.SystemModel):

    def __init__(self):
        """
        Constructor.  Setup the input and output variables.
        """
        coopr.pysos.SystemModel.__init__(self)
        self.inputs.add("x1")
        self.inputs.add("x2")
        self.outputs.add("y1")
        self.outputs.add("y2")

    def eval(self, input_vars, debug=False):
        """
        Evaluate this mode:
        """
        output_vals={}
        output_vals["y1"] = input_vars["x1"]*input_vars["x2"]
        output_vals["y2"] = input_vars["x1"]+input_vars["x2"]
        return [output_vals,output_vals]

#
# A simple model that generates the f output value
# with the following value:
#
#   f=y1*y2
#
class Model2(coopr.pysos.SystemModel):

    def __init__(self):
        """
        Constructor.  Setup the input and output variables.
        """
        coopr.pysos.SystemModel.__init__(self)
        self.inputs.add("y1")
        self.inputs.add("y2")
        self.outputs.add("f")

    def eval(self, input_vars, debug=False):
        """
        Evaluate this model:
        """
        output_vals={}
        output_vals["f"] = input_vars["y1"]*input_vars["y2"]
        return [output_vals,output_vals]


##
## MAIN - This is the main block of code executed
##

#
# Create the Pysos application
#
app = Application()
app.decision_variable("x1",0.0)
app.decision_variable("x2",1.0)
app.decision_variable("y1",0.0)
app.decision_variable("y2",1.0)
app.decision_variable("f",0.0)
#
# Insert model instances into the Pysos application
#
app.set_model("m1", Model1())
app.set_model("m2", Model2())
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
