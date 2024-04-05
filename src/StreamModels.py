#Ways to improve this code:
#I could add TYPE annotations in here to show people in the future what types of objects are used. 
#I could also use dataclass decorators to make the code more readable for new users
#for now, for consistency with FlowRegimes, I am going to leave my classes defined in the manual way with init and self and not use any type annotations.
#I could also jsut add comments with the data type, but that is not as good as using type annotations.
#type annotations allow you to use mypy to check for type errors in your code.

import pandas as pd
#from nnm import init_model_vars #this is going to create some circular dependencies; nnm.py is importing StreamModel and now StreamModels.py is importing something from nnm.py

#from nnm_io
def read_baseparams(baseparams_file):
    df = pd.read_csv(baseparams_file, header=None, index_col=0)
    return df.squeeze('columns').to_dict()

baseparams = read_baseparams('base_params.csv')


class ModelConstants:
    def __init__(self, a1, a2, b1, b2, Qbf, agN=30.0, agC=90.0, agCN=4.5, g=9.81, n=0.035, Jleach=85/3600):
        self.a1 = a1
        self.a2 = a2
        self.b1 = b1
        self.b2 = b2
        self.Qbf = Qbf
        self.agN = agN
        self.agC = agC
        self.agCN = agCN
        self.g = g
        self.n = n
        self.Jleach = Jleach


class NetworkConstants:
    def __init__(self, n_links, outlet_link, gage_link, gage_flow, feature, to_node, us_area, contrib_area, contrib_subwatershed, contrib_n_load_factor, routing_order, hw_links, slope, link_len, wetland_area, pEM, fainN, fainC, B_gage=-1, B_us_area=-1.0):
        self.n_links = n_links
        self.outlet_link = outlet_link
        self.gage_link = gage_link
        self.gage_flow = gage_flow
        self.feature = feature
        self.to_node = to_node
        self.us_area = us_area
        self.contrib_area = contrib_area
        self.contrib_subwatershed = contrib_subwatershed
        self.contrib_n_load_factor = contrib_n_load_factor
        self.routing_order = routing_order
        self.hw_links = hw_links
        self.slope = slope
        self.link_len = link_len
        self.wetland_area = wetland_area
        self.pEM = pEM
        self.fainN = fainN
        self.fainC = fainC
        self.B_gage = B_gage
        self.B_us_area = B_us_area

class ModelVariables:
    def __init__(self, q, Q_in, Q_out, B, U, H, N_conc_ri, N_conc_us, N_conc_ds, N_conc_in, C_conc_ri, C_conc_us, C_conc_ds, C_conc_in, mass_N_in, mass_N_out, mass_C_in, mass_C_out, cn_rat, jden):
        self.q = q
        self.Q_in = Q_in
        self.Q_out = Q_out
        self.B = B
        self.U = U
        self.H = H
        self.N_conc_ri = N_conc_ri
        self.N_conc_us = N_conc_us
        self.N_conc_ds = N_conc_ds
        self.N_conc_in = N_conc_in
        self.C_conc_ri = C_conc_ri
        self.C_conc_us = C_conc_us
        self.C_conc_ds = C_conc_ds
        self.C_conc_in = C_conc_in
        self.mass_N_in = mass_N_in
        self.mass_N_out = mass_N_out
        self.mass_C_in = mass_C_in
        self.mass_C_out = mass_C_out
        self.cn_rat = cn_rat
        self.jden = jden



"""
    StreamModel(
        mc::ModelConstants,
        nc::NetworkConstants,
        mv::ModelVariables
    )

The StreamModel structure is a wrapper around three other structures.
`ModelConstants` holds values of physical and process constants that do not
change during the run. `NetworkConstants` holds the specification of the
links, their characteristics, and nitrate concentrations from the landscape.
It will not change during the run, but is expected to be adapted for each
management scenario. Finally, `ModelVariables` holds the values that are
calculated during the model run. All `NitrateNetworkModel` functions will take the
entire `StreamModel` as an argument, so there is no need to pull out the
component structures. It is also expected that users will use the file-based
constructor [`StreamModel(::String, ::String)`](@ref).
"""

class StreamModel:
    def __init__(self, mc, nc, mv):
        self.mc = mc #model constants
        self.nc = nc #network constants
        self.mv = mv #model variables


    @classmethod #factory method; cretes a new StreamModel instance from the two files it imports
    def from_files(cls, baseparams_file, network_file):
        

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
        
        #init method reads CSV file into pandas df
        netdf = pd.read_csv('network_table.csv') #reads network file into a pandas dataframe
        n_links = int(baseparams["n_links"]) #retrieves the number of links from the baseparams dictionary
        routing_depth = netdf['routing_depth'] #gets the routing depth from the DF
        routing_order = sorted(range(1, n_links + 1), key=lambda x: (routing_depth[x - 1], n_links - x), reverse=True) #sorts the links based on their routing depth and index
        is_hw = netdf['is_hw'] #retrieves the is_hw column from the DF
        hw_links = [l for l in range(1, n_links + 1) if is_hw[l - 1] == 1] #list of links, is_hw =1 

        
        #creates an instance of Network Constants
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
        
        
    #creates an instance of model variables
        mv = init_model_vars(nc.n_links) #nc is an isntance of NetworkConstants but NetworkConstatnts doesn't have any instances yet 

        return cls(mc, nc, mv)
        #return StreamModel(mc, nc, mv)
    
    """
    reset_model_vars!(model::StreamModel)

Sets all values in all arrays in mv to 0.0. This way we don't have to
allocate a new ModelVariables object to rerun.
"""


    def reset_model_vars(self):
        self.mv.q = 0.0
        self.mv.Q_in = 0.0
        self.mv.Q_out = 0.0
        self.mv.B = 0.0
        self.mv.U = 0.0
        self.mv.H = 0.0
        self.mv.N_conc_ri = 0.0
        self.mv.N_conc_us = 0.0
        self.mv.N_conc_ds = 0.0
        self.mv.N_conc_in = 0.0
        self.mv.C_conc_ri = 0.0
        self.mv.C_conc_us = 0.0
        self.mv.C_conc_ds = 0.0
        self.mv.C_conc_in = 0.0
        self.mv.mass_N_in = 0.0
        self.mv.mass_N_out = 0.0
        self.mv.mass_C_in = 0.0
        self.mv.mass_C_out = 0.0
        self.mv.cn_rat = 0.0
        self.mv.jden = 0.0


