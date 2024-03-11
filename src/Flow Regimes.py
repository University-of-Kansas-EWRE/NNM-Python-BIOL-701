

#Julia NNM code:
#https://github.com/phawthorne/NitrateNetworkModel.jl
#3/7/24 most recent version!

#FlowRegime(flowfile:: String; q_gage)

import pandas as pd
import numpy as np
from copy import deepcopy

class FlowRegime:
    """
    Input structure for evaluating StreamModel against multiple flow values.
    Single-link flow regime - values measured at gaged link.

    q_gage, p_exceed, p_mass: List[float]
    """
    def __init__(self, q_gage, p_exceed, p_mass):
        self.q_gage = q_gage
        self.p_exceed = p_exceed
        self.p_mass = p_mass
    """
    function FlowRegime
    Constructor function to build FlowRegime from csv file.
    Q, cp and cf are the default values if nothing else is provided
    """
    @classmethod
    def from_file(cls, flowfile, q_gage_col = 'Q', p_exceed_col = 'cp', p_mass_col = 'cf'): #Q, cp and cf are the default values if nothing else is provided
        flowdf = pd.read_csv(flowfile) #reads data into a pandas dataframe
        q_gage = np.copy(flowdf[q_gage_col].values)
        p_exceed = np.copy(flowdf[p_exceed_col].values)
        p_mass = np.copy(flowdf[p_mass_col].values)
        return cls(q_gage, p_exceed, p_mass)
     
print(type(flowregime.p_mass)) #should return <class 'list'>

class FlowRegimeSimResults:
    """
    Output structure for evaluating StreamModel against multiple flow values.
    Single-link flow regime - values measured at gaged link.

    n_conc_outlet, n_conc_avg, p_mass: List[float]

    Results structure returned by `evaluate!`. Contains outlet
    and average nitrate concentration values for each of the flow values in
    `flowregime.q_gage`. `flowregime.p_mass` is copied over for convenience.
    """ 
    def __init__(self, n_conc_outlet, n_conc_avg, p_mass):
        self.n_conc_outlet = n_conc_outlet
        self.n_conc_avg = n_conc_avg
        self.p_mass = p_mass    

"""
    evaluate!(model::StreamModel, flowregime::FlowRegime)

Runs `stream_model.evaluate!(model, q)` for each q in `flowregime.q_gage.` Outlet
and average concentrations are saved to a `FlowRegimeSimResults` struct and
returned.

Evaluate modifies its arguments in place
"""

def evaluate(model, flowregime, contrib_n_load_reduction=None):
    nqvals = len(flowregime.q_gage)
    results = FlowRegimeSimResults(
        np.zeros(nqvals), #initialized as numpy arrays with np.zeros
        np.zeros(nqvals),
        np.copy(flowregime.p_mass) #deepcopy is not a method of numpy arrays, so np.copy is used instead
    )

    for i in range(nqvals):
        evaluate2(model, qgage=flowregime.q_gage[i], contrib_n_load_reduction=contrib_n_load_reduction) #unsure if this should be evaluate or evaluate2
        results.n_conc_outlet[i] = get_outlet_nconc(model) 
        results.n_conc_avg[i] = get_avg_nconc(model)

    return results


"""
    weighted_outlet_nconc(results::FlowRegimeSimResults)

Convenience function for getting probability exceedance weighted outlet concentration.
"""

def weighted_outlet_nconc(results):
    return np.sum(np.array(results.n_conc_outlet) * np.array(results.p_mass)) #double check this line


"""
    weighted_avg_nconc(results::FlowRegimeSimResults)

Convenience function for getting probability exceedance weighted average concentration.
"""
def weighted_avg_nconc(results):
    return np.sum(np.array(results.n_conc_avg) * np.array(results.p_mass)) #double check this line


"""
    full_eval_flow_regime(model::StreamModel, flowregime::FlowRegime)

Run `stream_model.evaluate!(model, q)` for each q in `flowregime.q_gage`.
Save averaged link values for values in `ModelVariables`.
"""

def full_eval_flow_regime(model, flowregime):
    results = init_model_vars(model.nc.n_links)

    for q, p in zip(flowregime.q_gage, flowregime.p_mass):
        evaluate(model, qgage=q)
        results = results + (p * model.mv) #may need to use n __add_ method here instead of +, depending on how the model variables are defined

    return results

"""
Write `flowregime` to CSV file `output_file
"""

def write_flow_regime(output_file, flowregime, q_gage_col="Q", p_exceed_col="cp", p_mass_col="cf"):
    nflows = len(flowregime.q_gage)

    with open(output_file, "w") as io:
        io.write(f"{q_gage_col},{p_exceed_col},{p_mass_col}\n")
        for i in range(nflows):
            q = flowregime.q_gage[i]
            cp = flowregime.p_exceed[i]
            cf = flowregime.p_mass[i]
            io.write(f"{q},{cp},{cf}\n")


#Copilot suggests the following improvements as of 3/7/2024:
"""
Your code seems to be well-structured for handling array data. You're using numpy arrays in the right places, such as initializing the n_conc_outlet and n_conc_avg in the FlowRegimeSimResults class and in the evaluate function. You're also correctly using numpy operations like np.sum and np.zeros.

However, there are a few potential issues and improvements that could be made:

In the evaluate function, you're calling evaluate2. Make sure that evaluate2 is defined somewhere in your code and that it modifies the model argument in-place as expected.

In the evaluate function, get_outlet_nconc and get_avg_nconc are used but not defined in the provided code. Ensure these functions are defined and return the expected values.

In the full_eval_flow_regime function, you're performing an operation results = results + (p * model.mv). Make sure that the __add__ method is properly defined for the type of results and model.mv to handle this operation.

The print statement print(type(flowregime.p_mass)) might not work as expected because flowregime is not defined in the provided code.

In the write_flow_regime function, you're writing the data to a CSV file manually. You could simplify this by creating a pandas DataFrame and using its to_csv method.

Lastly, make sure to close the docstrings properly. Each docstring should be enclosed within triple quotes ("""). In your code, some docstrings are not closed properly.
"""