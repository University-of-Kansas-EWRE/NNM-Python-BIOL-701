
import os

import sys


# Get the absolute path of the current script's directory
script_dir = os.path.dirname(os.path.abspath('run_le_sueur.ipynb'))

# Append the "src" directory to the script's directory
src_dir = os.path.join(script_dir, '..', 'src')

# Add the "src" directory to the beginning of sys.path
sys.path.insert(0, src_dir)

print(sys.path)

import NitrateNetworkModel

workspace = "../data/LeSueur"

def inputpath(basename):
    return os.path.join(workspace, "inputs", "LeSueurNetworkData", basename)

def resultpath(basename):
    return os.path.join(workspace, "results", basename)


def main():
    sm = NitrateNetworkModel.StreamModel(
        inputpath("base_params.csv"), 
        inputpath("network_table.csv")
    )
    sm.evaluate()
    sm.save_model_results(resultpath("base_results.csv"))

    #If you want to evaluate the model with different flow regimes:
    #flowregime = NitrateNetworkModel.FlowRegime(inputpath("flow_values.csv"))
    #results = sm.evaluate(flowregime)
    #print("weighted_avg_nconc:", results.weighted_avg_nconc())
    #print("weighted_outlet_nconc:", results.weighted_outlet_nconc())

main()
