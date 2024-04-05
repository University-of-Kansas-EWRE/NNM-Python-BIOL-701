
import os
import sys

# Get the absolute path of the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Append the "src" directory to the script's directory
src_dir = os.path.join(script_dir, '..', 'src')

# Add the "src" directory to the beginning of sys.path
sys.path.insert(0, src_dir)

print(sys.path)

import NitrateNetworkModel #I don't think that I can import this until I resolve the base_param issues that its depndent files are having! This module needs to actually run in order to be imported, I think 

workspace = "../data/LeSueur"

def inputpath(basename):
    return os.path.join(workspace, "inputs", "LeSueurNetworkData", basename)

def resultpath(basename):
    return os.path.join(workspace, "results", basename)


def main():
    sm = NitrateNetworkModel.StreamModel(
        inputpath("base_params.csv"), 
        inputpath("network_table.csv"),
        inputpath("base_results.csv") 

    )
    sm.evaluate() #streammodel object has no attribute evaluate
    sm.save_model_results(resultpath("base_results.csv"))

    #If you want to evaluate the model with different flow regimes:
    #flowregime = NitrateNetworkModel.FlowRegime(inputpath("flow_values.csv"))
    #results = sm.evaluate(flowregime)
    #print("weighted_avg_nconc:", results.weighted_avg_nconc())
    #print("weighted_outlet_nconc:", results.weighted_outlet_nconc())

main()
