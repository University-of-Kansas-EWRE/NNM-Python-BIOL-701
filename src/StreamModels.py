import pandas as pd

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
        print(f"ModelConstants instance created with a1={a1}, a2={a2}, ...")

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
        print(f"NetworkConstants instance created with n_links={n_links}, outlet_link={outlet_link}, ...")

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

class StreamModel:
    def __init__(self, nc: NetworkConstants, mv: ModelVariables, mc: ModelConstants):
        self.nc = nc
        self.mv = mv
        self.mc = mc
        print(f"StreamModel instance created with NetworkConstants={nc}, ModelVariables={mv}, ModelConstants={mc}")


#Only necessary when introducing FlowRegimes back into the model:
    # def reset_model_vars(self):
    # #reset all model vars to 0.0
    #     self.mv.q = 0.0
    #     self.mv.Q_in = 0.0
    #     self.mv.Q_out = 0.0
    #     self.mv.B = 0.0
    #     self.mv.U = 0.0
    #     self.mv.H = 0.0
    #     self.mv.N_conc_ri = 0.0
    #     self.mv.N_conc_us = 0.0
    #     self.mv.N_conc_ds = 0.0
    #     self.mv.N_conc_in = 0.0
    #     self.mv.C_conc_ri = 0.0
    #     self.mv.C_conc_us = 0.0
    #     self.mv.C_conc_ds = 0.0
    #     self.mv.C_conc_in = 0.0
    #     self.mv.mass_N_in = 0.0
    #     self.mv.mass_N_out = 0.0
    #     self.mv.mass_C_in = 0.0
    #     self.mv.mass_C_out = 0.0
    #     self.mv.cn_rat = 0.0
    #     self.mv.jden = 0.0

