
from StreamModels import ModelConstants, ModelVariables, NetworkConstants
from nnm import get_delivery_ratios, init_model_vars 
import pickle
import pandas as pd

#check working directory -- right now the code's working directory is the directory containing the local repo 
#would be better to provide an absolute path for future reference 
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
    df = pd.read_csv(baseparams_file, header=None, index_col=0)
    return df.squeeze('columns').to_dict()

baseparams = read_baseparams('base_params.csv')

#Q: this code imports network_file-- is this supposed to be network_table?? or was network_file created elsewhere?
#I temporariliy changed it to network_table.csv and put that data in the src file
#baseparams is not defined -- I think it comes from StreamModel.py

def StreamModel(baseparams_file, network_file):
    baseparams = read_baseparams(baseparams_file)
    mc = ModelConstants(
        a1 = baseparams["a1"],
        a2 = baseparams["a2"],
        b1 = baseparams["b1"],
        b2 = baseparams["b2"],
        Qbf = baseparams["Qbf"],
        agN = baseparams["agN"],
        agC = baseparams["agC"],
        agCN = baseparams["agCN"],
        g = baseparams["g"],
        n = baseparams["n"],
        Jleach = baseparams["Jleach"]
    )

    netdf = pd.read_csv('network_table.csv') #reads network file into a pandas dataframe
    n_links = int(baseparams["n_links"]) #retrieves the number of links from the baseparams dictionary
    routing_depth = netdf['routing_depth'] #gets the routing depth from the DF
    routing_order = sorted(range(1, n_links + 1), key=lambda x: (routing_depth[x - 1], n_links - x), reverse=True) #sorts the links based on their routing depth and index
    is_hw = netdf['is_hw'] #retrieves the is_hw column from the DF
    hw_links = [l for l in range(1, n_links + 1) if is_hw[l - 1] == 1] #list of links, is_hw =1 

    nc = NetworkConstants(
            n_links = n_links,
            outlet_link = baseparams["outlet_link"],
            gage_link = baseparams["gage_link"],
            gage_flow = baseparams["gage_flow"],
            feature = netdf.feature,
            to_node = netdf.to_node,
            us_area = netdf.us_area,
            contrib_area = netdf.contrib_area,
            contrib_subwatershed = netdf.swat_sub,
            contrib_n_load_factor = [1] * n_links,
            routing_order = routing_order,
            hw_links = hw_links,
            slope = netdf.slope,
            link_len = netdf.link_len,
            wetland_area = netdf.wetland_area,
            pEM = netdf.pEM,
            fainN = netdf.fainN,
            fainC = netdf.fainC,
            # optional values
            B_gage = baseparams["B_gage"] if "B_gage" in baseparams else -1,
            B_us_area = baseparams["B_us_area"] if "B_us_area" in baseparams else -1.0
        )

    mv = init_model_vars(nc.n_links) #nc is an isntance of NetworkConstants but NetworkConstatnts doesn't have any instances yet 

    return StreamModel(mc, nc, mv)

"Load either a YAML or CSV (legacy) baseparams file to a Dict"

#this part has not been double checked to make sure it's actually doing what Julia code did


import yaml
import csv

def read_baseparams(baseparams_file):
    fileext = baseparams_file.split('.')[-1]
    if fileext in ['yml', 'yaml']:
        with open(baseparams_file, 'r') as f:
            return yaml.safe_load(f)
    elif fileext == 'csv':
        baseparams = {}
        with open(baseparams_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header
            for row in reader:
                key, val = row
                baseparams[key] = float(val)
        return baseparams
    else:
        return None


def save_constants(mc, nc, filename):
    with open(filename, 'wb') as f:
        pickle.dump({'mc': mc, 'nc': nc}, f)

def load_constants(filename):
    with open(filename, 'rb') as f:
        d = pickle.load(f)
    return d['mc'], d['nc']


"""
    save_model_results(model::StreamModel, filename::String)

Writes model results to csv file
"""
def save_model_results(model: StreamModel, filename): #model is an instance of the class StreamModel
    mv, mc, nc = model.mv, model.mc, model.nc

    df = pd.DataFrame() #creates a new DF
    df['link'] = range(1, nc.n_links + 1)
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
