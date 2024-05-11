
import os
import sys

# Get the absolute path of the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Append the "src" directory to the script's directory
src_dir = os.path.join(script_dir, '..', 'src')

# Add the "src" directory to the beginning of sys.path
sys.path.insert(0, src_dir)

print(sys.path)
print("Source directory being added to path:", src_dir)

from NitrateNetworkModel import nnm_eval, save_model_results, read_baseparams, read_network_table, init_model_vars, StreamModel

workspace = "../data/LeSueur"

def inputpath(basename):
    path = os.path.join(workspace, "inputs", "LeSueurNetworkData", basename)
    print(f"Constructed input path: {path}")
    return path

def resultpath(basename):
    path = os.path.join(workspace, "results", basename)
    print(f"Constructed result path: {path}")
    return path


def main():
    print("Starting main function.")

    baseparams, n_links, outlet_link, gage_link, gage_flow = read_baseparams('base_params.csv') #creates an instance of Model Constants

    network_constants_instance = read_network_table('network_table.csv', n_links, outlet_link, gage_link, gage_flow)

    #Create instances from imported data
    model_variables_instance = init_model_vars(n_links) #Creates an instance of Model Variables

    # Create the StreamModel instance
    stream_model_instance = StreamModel(
        nc=network_constants_instance,
        mv=model_variables_instance,
        mc=baseparams
    )

    # Additional logic can follow here, like processing or displaying the model instance
    print("StreamModel instance created with:", stream_model_instance)

    nnm_eval(stream_model_instance) #I'm not sure WHICH evaluate function this is referring to -- I'll assume nnm_eval?
    print("Evaluation completed for StreamModel.")

    save_model_results(stream_model_instance, resultpath("base_results.csv")) #fncn defined in nnm_io
    print("Model results saved.")

    #If you want to evaluate the model with different flow regimes:
    #flowregime = NitrateNetworkModel.FlowRegime(inputpath("flow_values.csv"))
    #results = sm.evaluate(flowregime)
    #print("weighted_avg_nconc:", results.weighted_avg_nconc())
    #print("weighted_outlet_nconc:", results.weighted_outlet_nconc())
    # Check if the directory exists


main()


#it saved the test file to: C:\Users\gpcin\OneDrive - University of Kansas\data\LeSueur\results, which is not where I've been looking!