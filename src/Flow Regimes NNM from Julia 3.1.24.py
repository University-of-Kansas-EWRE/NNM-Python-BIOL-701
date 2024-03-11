

#Julia NNM code:
#https://github.com/phawthorne/NitrateNetworkModel.jl

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
def from_file(cls, flowfile, q_gage_col='Q', p_exceed_col='cp', p_mass_col='cf'):  # Q, cp and cf are the default values if nothing else is provided
    flowdf = pd.read_csv(flowfile)
    q_gage = deepcopy(flowdf[q_gage_col])
    p_exceed = deepcopy(flowdf[p_exceed_col])
    p_mass = deepcopy(flowdf[p_mass_col])
    return cls(q_gage, p_exceed, p_mass)

print(type(flowregime.p_mass))  # should return <class 'list'>

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
        np.zeros(nqvals), #numpy array -- python doesn't do vectors so I can choose between an array or a list to replicate julia vector
        np.zeros(nqvals),
        flowregime.p_mass.deepcopy() #not sure about this line; deepcopy won't work for numpy arrays and not sure what p_mass is
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

"Write `flowregime` to CSV file `output_file`"

def write_flow_regime(output_file, flowregime, q_gage_col="Q", p_exceed_col="cp", p_mass_col="cf"):
    nflows = len(flowregime.q_gage)

    with open(output_file, "w") as io:
        io.write(f"{q_gage_col},{p_exceed_col},{p_mass_col}\n")
        for i in range(nflows):
            q = flowregime.q_gage[i]
            cp = flowregime.p_exceed[i]
            cf = flowregime.p_mass[i]
            io.write(f"{q},{cp},{cf}\n")
