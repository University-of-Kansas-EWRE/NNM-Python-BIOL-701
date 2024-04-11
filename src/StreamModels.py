#Ways to improve this code:
#I could add TYPE annotations in here to show people in the future what types of objects are used. 
#I could also use dataclass decorators to make the code more readable for new users
#for now, for consistency with FlowRegimes, I am going to leave my classes defined in the manual way with init and self and not use any type annotations.
#I could also jsut add comments with the data type, but that is not as good as using type annotations.
#type annotations allow you to use mypy to check for type errors in your code.

import pandas as pd
#from nnm import init_model_vars #this is going to create some circular dependencies; nnm.py is importing StreamModel and now StreamModels.py is importing something from nnm.py

#import sys
#print(sys.version)

#from nnm_io 
#def read_baseparams(baseparams_file):
    #df = pd.read_csv(baseparams_file, header=None, index_col=0)
    #df = df.values
    #return df.squeeze('columns').to_dict()


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
        self.mv = mv
        #return cls(mc, nc, mv) I am not sure where this line should go now that I've changed a lot
        #it method reads CSV file into pandas df

        #self.baseparams = read_baseparams('base_params.csv')
        self.baseparams = pd.read_csv('base_params.csv', header=None, index_col=0).T #import and transpose
        self.n_links = int(self.baseparams.get("n_links", 0))  # Use get to handle missing keys

        self.netdf = pd.read_csv('network_table.csv')
        self.routing_depth = self.netdf['routing_depth'] #gets the routing depth from the DF 
        self.routing_depth = self.routing_depth.values
        self.routing_order = sorted(range(1, self.n_links + 1), key=lambda x: (self.routing_depth[x - 1], self.n_links - x), reverse=True) #sorts the links based on their routing depth and index
        self.is_hw = self.netdf['is_hw'] #retrieves the is_hw column from the DF
        self.hw_links = [l for l in range(1, self.n_links + 1) if self.is_hw[l - 1] == 1] #list of links, is_hw =1 

        self.a1 = self.baseparams["a1"]
        self.a2 = self.baseparams["a2"]
        self.b1 = self.baseparams["b1"]
        self.b2 = self.baseparams["b2"]
        self.Qbf = self.baseparams["Qbf"]
        self.agN = self.baseparams["agN"]
        self.agC = self.baseparams["agC"]
        self.agCN = self.baseparams["agCN"]
        self.g = self.baseparams["g"]
        self.n = self.baseparams["n"]
        self.Jleach = self.baseparams["Jleach"]


        mc = ModelConstants(
            a1=self.baseparams.get("a1", 0.0),  # Using get to handle missing keys
            a2=self.baseparams.get("a2", 0.0),
            b1=self.baseparams.get("b1", 0.0),
            b2=self.baseparams.get("b2", 0.0),
            Qbf=self.baseparams.get("Qbf", 0.0),
            agN=self.baseparams.get("agN", 30.0),
            agC=self.baseparams.get("agC", 90.0),
            agCN=self.baseparams.get("agCN", 4.5),
            g=self.baseparams.get("g", 9.81),
            n=self.baseparams.get("n", 0.035),
            Jleach=self.baseparams.get("Jleach", 85 / 3600)
    )
        
        #set up an object that contains all the model variables with their arrays set to zeros
    def init_model_vars(n_links):
        mv = ModelVariables(                              #creates a model variables object, so when you call init_model_vars, you get a ModelVariables object
            q = [0.0 for i in range(n_links)],            # flow from contrib area
            Q_in = [0.0 for i in range(n_links)],         # channel flow from upstream
            Q_out = [0.0 for i in range(n_links)],        # channel flow to downstream
            B = [0.0 for i in range(n_links)],            # channel width
            U = [0.0 for i in range(n_links)],
            H = [0.0 for i in range(n_links)],
            N_conc_ri = [0.0 for i in range(n_links)],    # [N] in q from land inputs
            N_conc_us = [0.0 for i in range(n_links)],    # [N] in Q_in from upstream
            N_conc_ds = [0.0 for i in range(n_links)],    # [N] in Q_out
            N_conc_in = [0.0 for i in range(n_links)],
            C_conc_ri = [0.0 for i in range(n_links)],    # same as N
            C_conc_us = [0.0 for i in range(n_links)],
            C_conc_ds = [0.0 for i in range(n_links)],
            C_conc_in = [0.0 for i in range(n_links)],
            mass_N_in = [0.0 for i in range(n_links)],
            mass_N_out = [0.0 for i in range(n_links)],
            mass_C_in = [0.0 for i in range(n_links)],
            mass_C_out = [0.0 for i in range(n_links)],
            cn_rat = [0.0 for i in range(n_links)],
            jden = [0.0 for i in range(n_links)]          # denitrification rate
        )

    
        #creates an instance of Network Constants -- THIS FUNCTION IS CAUSING the NONE error in reset_model_vars function later and attribute error in create_model_vars function later
    def create_network_constants_instance(self, nc): #I'm not sure if this data is organized in the right way
        self.nc = nc #assigns value of nc parameter to the nc attribute of the streammodel instance
        nc = NetworkConstants( 
            n_links = self.n_links,
            outlet_link = self.baseparams["outlet_link"],
            gage_link = self.baseparams["gage_link"],
            gage_flow = self.baseparams["gage_flow"],
            feature = self.netdf.feature,
            to_node = self.netdf.to_node,
            us_area = self.netdf.us_area,
            contrib_area = self.netdf.contrib_area,
            contrib_subwatershed = self.netdf.swat_sub,
            contrib_n_load_factor = [1] * self.n_links,
            routing_order = self.routing_order,
            hw_links = self.hw_links,
            slope = self.netdf.slope, 
            link_len = self.netdf.link_len,
            wetland_area = self.netdf.wetland_area,
            pEM = self.netdf.pEM,
            fainN = self.netdf.fainN,
            fainC = self.netdf.fainC,
            # optional values
            B_gage = self.baseparams["B_gage"] if "B_gage" in self.baseparams else -1,
            B_us_area = self.baseparams["B_us_area"] if "B_us_area" in self.baseparams else -1.0
        )
        return nc
        
        
    def create_model_variables_instance(self):
        mv = StreamModel.init_model_vars(self.nc.n_links)  
        return mv

#return StreamModel(mc, nc, mv) #I don't know where to put this line
    
    """
    reset_model_vars!(model::StreamModel)

Sets all values in all arrays in mv to 0.0. This way we don't have to
allocate a new ModelVariables object to rerun.
"""

def reset_model_vars(stream_model): #right now this is not a method of StreamModel class, as was the case in the Julia version. In Julia this just operates on a StreamModel object
    #stream_model is an instance of the StreamModel class that we are creating here
    mv = stream_model.create_model_variables_instance().mv
    mv.q = 0.0
    mv.Q_in = 0.0
    mv.Q_out = 0.0
    mv.B = 0.0
    mv.U = 0.0
    mv.H = 0.0
    mv.N_conc_ri = 0.0
    mv.N_conc_us = 0.0
    mv.N_conc_ds = 0.0
    mv.N_conc_in = 0.0
    mv.C_conc_ri = 0.0
    mv.C_conc_us = 0.0
    mv.C_conc_ds = 0.0
    mv.C_conc_in = 0.0
    mv.mass_N_in = 0.0
    mv.mass_N_out = 0.0
    mv.mass_C_in = 0.0
    mv.mass_C_out = 0.0
    mv.cn_rat = 0.0
    mv.jden = 0.0

    return


#return StreamModel(mc, nc, mv) #I don't know where to put this line
