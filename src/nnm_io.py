
from StreamModels import ModelConstants, ModelVariables, NetworkConstants, StreamModel 
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
##NEW approach, changing the functions that read parameters to directly return class instances

def read_baseparams(baseparams_file):
    df = pd.read_csv(baseparams_file, header=0, index_col=0)
    baseparams = df.squeeze('columns').to_dict()
    n_links = int(baseparams['n_links']) if 'n_links' in baseparams else 0
    
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

    return model_constants, n_links  # Notice returning both the instance and n_links


def read_network_table(network_table, n_links):
    df = pd.read_csv(network_table, header=0, index_col=0)
    n_links = int(df.at['n_links', 'value'])  # Assuming 'n_links' is stored as a scalar in the DataFrame

    # Prepare routing_order and hw_links
    routing_depth = df['routing_depth'].tolist()
    is_hw = df['is_hw'].tolist()
    routing_order = sorted(range(1, n_links + 1),
                           key=lambda x: (routing_depth[x - 1], n_links - x),
                           reverse=True)
    hw_links = [x for x in range(1, n_links + 1) if is_hw[x - 1] == 1]

    return NetworkConstants(
        n_links=n_links,
        outlet_link=int(df.at['outlet_link', 'value']),
        gage_link=int(df.at['gage_link', 'value']),
        gage_flow=float(df.at['gage_flow', 'value']),
        feature=df['feature'].tolist(),
        to_node=df['to_node'].tolist(),
        us_area=df['us_area'].tolist(),
        contrib_area=df['contrib_area'].tolist(),
        contrib_subwatershed=df['swat_sub'].tolist(),
        contrib_n_load_factor=[1] * n_links,
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




##OLD APPROACH BEFORE 5.4.24
# def read_baseparams(baseparams_file):
#     # Read the CSV into a DataFrame
#     df = pd.read_csv(baseparams_file, header=0, index_col=0)
#     # Squeeze the DataFrame to a Series and convert to a dictionary
#     baseparams = df.squeeze('columns').to_dict()

#     # Check if 'n_links' is a key in the dictionary and convert it to an integer
#     if 'n_links' in baseparams:
#         baseparams['n_links'] = int(baseparams['n_links'])
    
#     return baseparams

# def read_network_table(network_table):
#     df = pd.read_csv(network_table, header=0, index_col=0)
#     return df

# print("Reading base parameters...")
# baseparams = read_baseparams('base_params.csv')
# netdf = read_network_table('network_table.csv')

# #Q: this code imports network_file-- is this supposed to be network_table?? or was network_file created elsewhere?
# #I temporariliy changed it to network_table.csv and put that data in the src file
# #baseparams is not defined -- I think it comes from StreamModel.py

# print("Converting n_links to integer...")
# n_links = int(baseparams["n_links"])
# print('n_links vale:', n_links)
# print('n_links type', type(n_links))
# print("baseparams['n_links'] type:", type(baseparams["n_links"]))


# def init_model_vars(n_links):
#     print("Initializing model variables...")
#     q = [0.0 for i in range(n_links)]            # flow from contrib area
#     Q_in = [0.0 for i in range(n_links)]         # channel flow from upstream
#     Q_out = [0.0 for i in range(n_links)]        # channel flow to downstream
#     B = [0.0 for i in range(n_links)]            # channel width
#     U = [0.0 for i in range(n_links)]
#     H = [0.0 for i in range(n_links)]
#     N_conc_ri = [0.0 for i in range(n_links)]    # [N] in q from land inputs
#     N_conc_us = [0.0 for i in range(n_links)]    # [N] in Q_in from upstream
#     N_conc_ds = [0.0 for i in range(n_links)]    # [N] in Q_out
#     N_conc_in = [0.0 for i in range(n_links)]
#     C_conc_ri = [0.0 for i in range(n_links)]    # same as N
#     C_conc_us = [0.0 for i in range(n_links)]
#     C_conc_ds = [0.0 for i in range(n_links)]
#     C_conc_in = [0.0 for i in range(n_links)]
#     mass_N_in = [0.0 for i in range(n_links)]
#     mass_N_out = [0.0 for i in range(n_links)]
#     mass_C_in = [0.0 for i in range(n_links)]
#     mass_C_out = [0.0 for i in range(n_links)]
#     cn_rat = [0.0 for i in range(n_links)]
#     jden = [0.0 for i in range(n_links)]          # denitrification rate

# #Create instances from imported data
# model_variables_instance = init_model_vars(int(baseparams["n_links"]))

# model_constants_instance = ModelConstants(
#     a1 = baseparams["a1"],
#     a2 = baseparams["a2"],
#     b1 = baseparams["b1"],
#     b2 = baseparams["b2"],
#     Qbf = baseparams["Qbf"],
#     agN = baseparams["agN"],
#     agC = baseparams["agC"],
#     agCN = baseparams["agCN"],
#     g = baseparams["g"],
#     n = baseparams["n"],
#     Jleach = baseparams["Jleach"]
# )

# print(netdf.keys())

# routing_depth = netdf['routing_depth'].tolist() #gets the routing depth from the DF 
# routing_order = sorted(range(1, baseparams["n_links"] + 1), key=lambda x: (routing_depth[x - 1], int(baseparams["n_links"]) - x), reverse=True) #sorts the links based on their routing depth and index
# is_hw = netdf['is_hw'].tolist() #retrieves the is_hw column from the DF
# hw_links = [l for l in range(1, n_links + 1) if is_hw[l - 1] == 1] #list of links, is_hw =1 

# network_constants_instance = NetworkConstants(
#     n_links = baseparams["n_links"],
#     outlet_link = baseparams["outlet_link"],
#     gage_link = baseparams["gage_link"],
#     gage_flow = baseparams["gage_flow"],
#     feature = netdf.feature,
#     to_node = netdf.to_node,
#     us_area = netdf.us_area,
#     contrib_area = netdf.contrib_area,
#     contrib_subwatershed = netdf.swat_sub,
#     contrib_n_load_factor = [1] * baseparams["n_links"],
#     routing_order = routing_order,
#     hw_links = hw_links,
#     slope = netdf.slope, 
#     link_len = netdf.link_len,
#     wetland_area = netdf.wetland_area,
#     pEM = netdf.pEM,
#     fainN = netdf.fainN,
#     fainC = netdf.fainC,
#     # optional values
#     B_gage = baseparams["B_gage"] if "B_gage" in baseparams else -1,
#     B_us_area = baseparams["B_us_area"] if "B_us_area" in baseparams else -1.0
#)

# #Feed instances of mv, mc, and nc into a streammodel instance
# stream_model_instance = StreamModel(
#     nc=network_constants_instance,
#     mv=model_variables_instance,
#     mc=model_constants_instance
# )


"Load either a YAML or CSV (legacy) baseparams file to a Dict"

#this part has not been double checked to make sure it's actually doing what Julia code did


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
