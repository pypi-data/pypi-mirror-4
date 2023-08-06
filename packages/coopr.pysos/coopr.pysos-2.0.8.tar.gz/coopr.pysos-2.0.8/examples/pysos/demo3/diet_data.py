#
# Create a Pyomo ModelData object, which imports the diet data
# file, along with other data files that might be created
# by the Pysos application.
#
from coopr.pyomo import *

modeldata = ModelData()

modeldata.add_data_file("diet.dat")

if os.path.exists("diet_tmp.dat"):
    print("Found diet_tmp.dat")
    modeldata.add_data_file("diet_tmp.dat")
