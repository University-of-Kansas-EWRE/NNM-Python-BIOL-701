#Ways to improve this code:
#I could add TYPE annotations in here to show people in the future what types of objects are used. 
#I could also use dataclass decorators to make the code more readable for new users
#for now, for consistency with FlowRegimes, I am going to leave my classes defined in the manual way with init and self and not use any type annotations.
#I could also jsut add comments with the data type, but that is not as good as using type annotations.
#type annotations allow you to use mypy to check for type errors in your code.

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

        """
    reset_model_vars!(model::StreamModel)

Sets all values in all arrays in mv to 0.0. This way we don't have to
allocate a new ModelVariables object to rerun.
"""


    def reset_model_vars(self):
        self.mv['q'] = 0.0 #each var is set to 0 to reset the model
        self.mv['Q_in'] = 0.0
        self.mv['Q_out'] = 0.0
        self.mv['B'] = 0.0
        self.mv['U'] = 0.0
        self.mv['H'] = 0.0
        self.mv['N_conc_ri'] = 0.0
        self.mv['N_conc_us'] = 0.0
        self.mv['N_conc_ds'] = 0.0
        self.mv['N_conc_in'] = 0.0
        self.mv['C_conc_ri'] = 0.0
        self.mv['C_conc_us'] = 0.0
        self.mv['C_conc_ds'] = 0.0
        self.mv['C_conc_in'] = 0.0
        self.mv['mass_N_in'] = 0.0
        self.mv['mass_N_out'] = 0.0
        self.mv['mass_C_in'] = 0.0
        self.mv['mass_C_out'] = 0.0
        self.mv['cn_rat'] = 0.0
        self.mv['jden'] = 0.0
