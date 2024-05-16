
from StreamModels import ModelConstants, ModelVariables, NetworkConstants, StreamModel 
from nnm import get_delivery_ratios
import pickle
import pandas as pd

import os
print("Current working directory:", os.getcwd())
print("Does the file exist?", os.path.exists('base_params.csv'))

"""
    StreamModel(baseparams_file::String, network_file::String)

Constructs a [`StreamModel`](@ref) based on inputs in two csv files. The files
should be structured as follows:

* baseparams_file: columns "variable" and "value".
* network_file: many more columns.
"""

def read_baseparams(baseparams_file):
    df = pd.read_csv(baseparams_file, header=0, index_col=0)
    baseparams = df.squeeze('columns').to_dict()

    # Extracting specific parameters for NetworkConstants configuration
    n_links = int(baseparams['n_links']) if 'n_links' in baseparams else 0
    outlet_link = int(baseparams['outlet_link']) - 1 if 'outlet_link' in baseparams else -1
    gage_link = int(baseparams['gage_link']) - 1 if 'gage_link' in baseparams else -1
    gage_flow = float(baseparams['gage_flow']) if 'gage_flow' in baseparams else -1.0

    # Create and return ModelConstants instance
    model_constants = ModelConstants(
        a1=baseparams.get("a1"),
        a2=baseparams.get("a2"),
        b1=baseparams.get("b1"),
        b2=baseparams.get("b2"),
        Qbf=baseparams.get("Qbf"),
        agN=baseparams.get("agN", 30.0),
        agC=baseparams.get("agC", 90.0),
        agCN=baseparams.get("agCN", 4.5),
        g=baseparams.get("g", 9.81),
        n=baseparams.get("n", 0.035),
        Jleach=baseparams.get("Jleach", 85/3600)
    )

    return model_constants, n_links, outlet_link, gage_link, gage_flow

def read_network_table(network_table, n_links, outlet_link, gage_link, gage_flow):
    df = pd.read_csv(network_table, header=0, index_col=0)

    # Prepare routing_order and hw_links
    routing_depth = df['routing_depth'].tolist()
    #print('Routing depth, not sorted', routing_depth)

    is_hw = df['is_hw'].tolist()
    
    #a little different from the Julia code since Python is 0-based and Julia is 1-based
    routing_order = sorted(range(n_links),
                           key=lambda x: (routing_depth[x], n_links - 1 - x),
                           reverse=True)
    
    # First, determine hw_links based on zero-based index directly
    hw_links = [x for x in range(n_links) if is_hw[x] == 1]

    to_node_adjusted = [x - 1 for x in df['to_node'].tolist()]


    return NetworkConstants(
        n_links=n_links,
        outlet_link=outlet_link,
        gage_link=gage_link,
        gage_flow=gage_flow,
        feature=df['feature'].tolist(),
        to_node=to_node_adjusted,
        us_area=df['us_area'].tolist(),
        contrib_area=df['contrib_area'].tolist(),
        contrib_subwatershed=df['swat_sub'].tolist(),
        contrib_n_load_factor=[1.0] * n_links,
        routing_order=routing_order,
        hw_links=hw_links,
        slope=df['slope'].tolist(),
        link_len=df['link_len'].tolist(),
        wetland_area=df['wetland_area'].tolist(),
        pEM=df['pEM'].tolist(),
        fainN=df['fainN'].tolist(),
        fainC=df['fainC'].tolist(),
        B_gage=df.get('B_gage', -1),
        B_us_area=df.get('B_us_area', -1.0)
    )
  

def init_model_vars(n_links):
    print("Initializing model variables...")
    # Initialize all variables
    q = [0.0] * n_links
    Q_in = [0.0] * n_links
    Q_out = [0.0] * n_links
    B = [0.0] * n_links
    U = [0.0] * n_links
    H = [0.0] * n_links
    N_conc_ri = [0.0] * n_links
    N_conc_us = [0.0] * n_links
    N_conc_ds = [0.0] * n_links
    N_conc_in = [0.0] * n_links
    C_conc_ri = [0.0] * n_links
    C_conc_us = [0.0] * n_links
    C_conc_ds = [0.0] * n_links
    C_conc_in = [0.0] * n_links
    mass_N_in = [0.0] * n_links
    mass_N_out = [0.0] * n_links
    mass_C_in = [0.0] * n_links
    mass_C_out = [0.0] * n_links
    cn_rat = [0.0] * n_links
    jden = [0.0] * n_links

    return ModelVariables(q, Q_in, Q_out, B, U, H, N_conc_ri, N_conc_us, N_conc_ds, N_conc_in, C_conc_ri, C_conc_us, C_conc_ds, C_conc_in, mass_N_in, mass_N_out, mass_C_in, mass_C_out, cn_rat, jden)



"Load either a YAML or CSV (legacy) baseparams file to a Dict"


import yaml
import csv

def save_constants(mc, nc, filename):
    with open(filename, 'wb') as f:
        pickle.dump({'mc': mc, 'nc': nc}, f)

def load_constants(filename):
    with open(filename, 'rb') as f:
        d = pickle.load(f)
    return d['mc'], d['nc']


"""
    save_model_variables(mv::ModelVariables, filename::String)

Write a ModelVariables struct to a table
"""

def save_model_variables(mv, filename):
    df = pd.DataFrame({
        'link': range(1, len(mv.q) + 1),
        'q': mv.q,
        'Q_in': mv.Q_in,
        'Q_out': mv.Q_out,
        'B': mv.B,
        'H': mv.H,
        'U': mv.U,
        'Jden': mv.jden,
        'cnrat': mv.cn_rat,
        'N_conc_ri': mv.N_conc_ri,
        'N_conc_us': mv.N_conc_us,
        'N_conc_ds': mv.N_conc_ds,
        'N_conc_in': mv.N_conc_in,
        'C_conc_ri': mv.C_conc_ri,
        'C_conc_us': mv.C_conc_us,
        'C_conc_ds': mv.C_conc_ds,
        'C_conc_in': mv.C_conc_in,
        'mass_N_out': mv.mass_N_out,
        'mass_C_out': mv.mass_C_out
    })

    df.to_csv(filename, index=False)


def save_model_results(model: StreamModel, filename): #model is an instance of the class StreamModel
    mv, mc, nc = model.mv, model.mc, model.nc

    df = pd.DataFrame() #creates a new DF
    df['link'] = range(0, nc.n_links) 
    df['feature'] = nc.feature
    df['q'] = mv.q
    df['Q_in'] = mv.Q_in
    df['Q_out'] = mv.Q_out
    df['B'] = mv.B
    df['H'] = mv.H
    df['U'] = mv.U
    df['Jden'] = mv.jden
    df['cnrat'] = mv.cn_rat
    df['N_conc_ri'] = mv.N_conc_ri
    df['N_conc_us'] = mv.N_conc_us
    df['N_conc_ds'] = mv.N_conc_ds
    df['N_conc_in'] = mv.N_conc_in
    df['C_conc_ri'] = mv.C_conc_ri
    df['C_conc_us'] = mv.C_conc_us
    df['C_conc_ds'] = mv.C_conc_ds
    df['C_conc_in'] = mv.C_conc_in
    df['mass_N_out'] = mv.mass_N_out
    df['mass_C_out'] = mv.mass_C_out
    ldr, lef = get_delivery_ratios(model)
    df['link_DR'] = ldr
    df['link_EF'] = lef

    df.to_csv(filename, index=False) #writes model results to a csv file

    results_dir = os.path.normpath('../data/LeSueur/results/')
    if not os.path.exists(results_dir):
        print("Directory does not exist. Trying to create it.")
        os.makedirs(results_dir)

    # Try to write a test file
    test_file_path = os.path.join(results_dir, 'test_file.txt')
    try:
        with open(test_file_path, 'w') as file:
            file.write('This is a test file.')
        print(f"Test file successfully written to {test_file_path}")
    except Exception as e:
        print(f"Failed to write test file: {e}")

    # Now attempt to write  actual output file
    output_file_path = os.path.join(results_dir, 'base_results.csv')
    try:
        # Assuming 'df' is DataFrame
        df.to_csv(output_file_path, index=False)
        print(f"Results successfully saved to {output_file_path}")
    except Exception as e:
        print(f"Failed to save results: {e}")

