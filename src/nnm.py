import numpy as np
import pandas as pd
import math
from StreamModels import StreamModel


def nnm_eval(model, qgage=math.nan, contrib_n_load_reduction=None): # qgage is the flow at the gage link
    print('Starting evaluation with model nc instance:', model.nc)
    #model.reset_model_vars()  ###TURN THIS BACK ON WHEN I USE FLOW REGIMES EVENTUALLY
    print(f'Initial qgage value: {qgage}')


    for attr in dir(model.nc):
        value = getattr(model.nc, attr)
        #print("attributes of model.nc:", attr, ':', value)


    if math.isnan(qgage):
        print('qgage is NaN, using default gage_flow from model.nc')
        assign_qQ(model, model.nc.gage_flow) #used if qgage is not provided
    else:
        print(f'qgage provided: {qgage}, using it for flow calculation')
        assign_qQ(model, qgage)

    assign_B(model)
    determine_U_H_wetland_hydraulics(model)
    compute_N_C_conc(model, contrib_n_load_reduction=contrib_n_load_reduction)  
    print('Evaluation completed.')


"""
    init_model_vars(n_links::Int64)

Returns a new `ModelVariables` instance with zero-initialized vectors.
"""


"""
    assign_qQ!(model::StreamModel, q_gage::Float64)

Routes water
"""


def assign_qQ(model, q_gage):
    q = model.mv.q
    Q_in = model.mv.Q_in
    Q_out = model.mv.Q_out
    us_area = model.nc.us_area
    contrib_area = model.nc.contrib_area
    routing_order = model.nc.routing_order
    to_node = model.nc.to_node
    gage_link = model.nc.gage_link
    outlet_link = model.nc.outlet_link

    contrib_q_per_area = q_gage / us_area[gage_link]

    #print("Routing order (assing_qQ function):", routing_order)

    #print("Initial Q_in (before loop in assign_qQ):", Q_in)

    print("to node of 482", to_node[482])
    
    for l in routing_order:

        q[l] = contrib_q_per_area * contrib_area[l]
        Q_out[l] = q[l] + Q_in[l]
        
        # Ensure to_node[l] is within valid range and not the outlet link
        if 0 <= to_node[l] < len(Q_in):
            Q_in[to_node[l]] += Q_out[l]

        print("l, Q_in 641", l, Q_in[641])

    q[outlet_link] = contrib_q_per_area * contrib_area[outlet_link]
    Q_out[outlet_link] = q[outlet_link] + Q_in[outlet_link]

    # print("Final Q_in[641]", Q_in[641])
    # print("Final Q_out[641]", Q_out[641])
    # print("Final Q_in:", Q_in)
    # print("Final Q_out:", Q_out)
    # print("Final q:", q)
    #print("to_node", to_node)

    #print("routing order", routing_order)
"""
    assign_B!(model::StreamModel)

Calculates average channel width (B).

Options:
    - If `model` has an assigned `B_gage` and `B_us_area`, channel widths will
    be calculated relative to those values. Otherwise, channel widths will be
    calculated relative to `Q_out[gage_link]` and `us_area[gage_link]`.
"""

def assign_B(model):
    Qbf = model.mc.Qbf
    a1 = model.mc.a1
    a2 = model.mc.a2
    b1 = model.mc.b1
    b2 = model.mc.b2
    gage_link = model.nc.gage_link
    us_area = model.nc.us_area
    B_gage = model.nc.B_gage
    B_us_area = model.nc.B_us_area
    #B = model.mv.B
    Q_out = model.mv.Q_out

    # Get reference flow and upstream area
    Q_ref = B_gage if B_gage > 0 else Q_out[gage_link]
    us_area_ref = B_us_area if B_us_area > 0 else us_area[gage_link]

    # Apply flow-based scaling function to calculate reference width
    B_ref = a1 * Q_ref ** b1 if Q_ref < Qbf else a2 * Q_ref ** b2

    # Apply area-based scaling over the network
    model.mv.B  = (B_ref / math.sqrt(us_area_ref)) * np.sqrt(us_area)


"""
    determine_U_H_wetland_hydraulics!(model::StreamModel)

Calculates U and H, and updates B for wetlands.
#TODO: move the B updating to the function for B?
    the wrong version of B is used to calculate U and H, but then these
    are updated - could skip the update?
"""

def determine_U_H_wetland_hydraulics(model):
    n = model.mc.n
    g = model.mc.g
    n_links = model.nc.n_links
    feature = model.nc.feature
    link_len = model.nc.link_len
    slope = model.nc.slope
    wetland_area = model.nc.wetland_area
    Q_in = model.mv.Q_in
    Q_out = model.mv.Q_out
    B = model.mv.B
    H = model.mv.H
    U = model.mv.U

    tmp_U = [0.0 for i in range(n_links)]
    tmp_H = [0.0 for i in range(n_links)]


    # Calculate tmp_U and tmp_H
    tmp_U = np.power((1/n * np.power(Q_out/B, 2/3) * np.sqrt(slope)), 3/5)
    tmp_H = Q_out / tmp_U / B

    # Initialize wetl_vol
    wetl_vol = np.zeros(n_links)

    for i in range(n_links):
        U[i] = tmp_U[i]
        H[i] = tmp_H[i]

        if feature[i] == 1:
            continue

        if feature[i] == 2:
            wetl_vol = 0.0032 * wetland_area[i] ** 1.47
        elif feature[i] == 3:
            wetl_vol = 2.1 * wetland_area[i]
        else:
            wetl_vol = 0

        link_len[i] = math.sqrt(wetland_area[i])
        B[i] = math.sqrt(wetland_area[i]) #should this be math or np?
        H[i] = wetl_vol / wetland_area[i]
        U[i] = Q_out[i] / B[i] / H[i]


"""
    compute_N_C_conc!(model::StreamModel)

Routes N and C, computes denitrification.
"""
def compute_N_C_conc(model, contrib_n_load_reduction=None):
    # Initialize counters
    counters = {
        "calc_N_conc_us": 0,
        "calc_C_conc_us": 0,
        "add_N_conc_ri": 0,
        "add_C_conc_ri": 0,
        "update_mass_N_in": 0,
        "update_mass_C_in": 0,
        "calc_N_conc_in": 0,
        "calc_C_conc_in": 0,
        "calc_jden": 0,
        "update_mass_C_out": 0,
        "update_mass_N_out": 0,
        "calc_N_conc_ds": 0,
        "calc_C_conc_ds": 0,
        "route_N_mass_downstream": 0,
        "route_C_mass_downstream": 0,
        "Q_in_zero": 0  # Counter for Q_in[l] == 0

    }

    # Unpack mc
    agN = model.mc.agN
    agC = model.mc.agC
    agCN = model.mc.agCN
    Jleach = model.mc.Jleach

    # Unpack mv using attribute access
    q = model.mv.q
    Q_in = model.mv.Q_in
    Q_out = model.mv.Q_out
    B = model.mv.B
    N_conc_ri = model.mv.N_conc_ri
    N_conc_us = model.mv.N_conc_us
    N_conc_ds = model.mv.N_conc_ds
    N_conc_in = model.mv.N_conc_in
    C_conc_ri = model.mv.C_conc_ri
    C_conc_ds = model.mv.C_conc_ds
    C_conc_us = model.mv.C_conc_us
    C_conc_in = model.mv.C_conc_in
    cn_rat = model.mv.cn_rat
    jden = model.mv.jden
    mass_N_in = model.mv.mass_N_in
    mass_N_out = model.mv.mass_N_out
    mass_C_in = model.mv.mass_C_in
    mass_C_out = model.mv.mass_C_out

    # Unpack nc using attribute access
    link_len = model.nc.link_len
    routing_order = model.nc.routing_order
    to_node = model.nc.to_node
    outlet_link = model.nc.outlet_link
    fainN = model.nc.fainN
    fainC = model.nc.fainC
    wetland_area = model.nc.wetland_area
    pEM = model.nc.pEM
    contrib_n_load_factor = model.nc.contrib_n_load_factor

    # print("Length of routing_order:", len(routing_order))
    # print("Length of Q_in:", len(Q_in))

    # print("Minimum index in routing_order:", min(routing_order))
    # print("Maximum index in routing_order:", max(routing_order))

    # if max(routing_order) >= len(Q_in):
    #     raise ValueError("routing_order contains an index out of range for Q_in")

    if contrib_n_load_reduction is None:
        contrib_n_load = contrib_n_load_factor

    for l in routing_order:
        # bookkeeping

        if Q_in[l] == 0:
            N_conc_us[l] = 0
            C_conc_us[l] = 0
            counters["Q_in_zero"] += 1

        else:
            N_conc_us[l] = mass_N_in[l] / Q_in[l]
            counters["calc_N_conc_us"] += 1
            C_conc_us[l] = mass_C_in[l] / Q_in[l]
            counters["calc_C_conc_us"] += 1

        N_conc_ri[l] = agN * fainN[l] * contrib_n_load[l]
        counters["add_N_conc_ri"] += 1
        C_conc_ri[l] = agC * fainC[l] + agCN * fainN[l]
        counters["add_C_conc_ri"] += 1

        mass_N_in[l] += N_conc_ri[l] * q[l]
        counters["update_mass_N_in"] += 1
        mass_C_in[l] += (C_conc_ri[l] * q[l]) + (Jleach * wetland_area[l] * pEM[l] * 1.0e-5)
        counters["update_mass_C_in"] += 1

        N_conc_in[l] = mass_N_in[l] / (Q_in[l] + q[l])
        counters["calc_N_conc_in"] += 1
        C_conc_in[l] = mass_C_in[l] / (Q_in[l] + q[l])
        counters["calc_C_conc_in"] += 1

        if mass_N_in[l] == 0.0:
            jden[l] = 0
        else:
            cn_rat[l] = mass_C_in[l] / mass_N_in[l]
            if cn_rat[l] >= 1:
                jden[l] = (11.5 * np.sqrt(N_conc_in[l])) / 3600
            else:
                jden[l] = (3.5 * C_conc_in[l]) / 3600
            counters["calc_jden"] += 1

        mass_C_out[l] = max(0, mass_C_in[l] - jden[l] * B[l] * link_len[l] * 1.0e-3)
        counters["update_mass_C_out"] += 1
        mass_N_out[l] = max(0, mass_N_in[l] - jden[l] * B[l] * link_len[l] * 1.0e-3)
        counters["update_mass_N_out"] += 1

        # if Q_out[l] == 0: #it wouldn't be a link if there wasn't q out
        #     N_conc_ds[l] = 0
        #     C_conc_ds[l] = 0
        # else:
        if Q_out[l] == 0:
            print(f"Unexpected zero Q_out at link {l}")

        N_conc_ds[l] = mass_N_out[l] / Q_out[l]
        counters["calc_N_conc_ds"] += 1
        C_conc_ds[l] = mass_C_out[l] / Q_out[l]
        counters["calc_C_conc_ds"] += 1

        if l != outlet_link:
            mass_N_in[to_node[l]] += mass_N_out[l]
            counters["route_N_mass_downstream"] += 1
            mass_C_in[to_node[l]] += mass_C_out[l]
            counters["route_C_mass_downstream"] += 1

    # Print the lengths
    # print("The length of N_conc_ri is:", len(N_conc_ri))
    # print("The length of mass_N_in is:", len(mass_N_in))
    # print("The length of q is:", len(q))

    # Print the counters to see how many times each calculation was executed
    for key, count in counters.items():
        print(f"{key}: {count}")


#= Solution querying functions =#
"""
    get_outlet_n_conc(model::StreamModel)::Float64

Gets nitrate concentration leaving outlet link
"""

def get_outlet_n_conc(model):
    #unpack mv
    mv = model.mv
    mc = model.mc
    nc = model.nc

    return mv.N_conc_ds[nc.outlet_link] #this line might be wrong, might be     return mv['N_conc_ds'][nc['outlet_link']]

"""
    get_avg_n_conc(model::StreamModel)::Float64

Gets link length-weighted nitrate concentration
"""

def get_average_nconc(model):
    #unpack mv
    mv = model.mv
    mc = model.mc
    nc = model.nc

    tot_len_w_nconc = sum(mv.N_conc_ds * nc.link_len)
    tot_len = sum(nc.link_len)
    return tot_len_w_nconc / tot_len


#def get_avg_n_conc(model): #confused on why this is here
    #return get_average_n_conc(model)

"""
    get_delivery_ratios(model::StreamModel)::Tuple{Vector{Float64}, Vector{Float64}}

Returns vectors with net delivery ratio and escape fraction for each link.
"""

import networkx as nx

def get_delivery_ratios(model):
    #unpack q
    q = model.mv.q
    Q_in = model.mv.Q_in
    N_conc_ri = model.mv.N_conc_ri
    N_conc_ds = model.mv.N_conc_ds
    N_conc_in = model.mv.N_conc_in

    #unpack to_node
    to_node = model.nc.to_node
    outlet_link = model.nc.outlet_link
    n_links = model.nc.n_links

    to_node = [x - 1 for x in to_node]  # Adjust all entries for 0-based indexing
    outlet_link = outlet_link - 1

    #print("to node (get_delivery_ratios)", to_node)

    #loop detection!
    def detect_cycles(to_node):
        G = nx.DiGraph()
        for src, dest in enumerate(to_node):
            if dest != -1:  # Assuming -1 indicates no outgoing link
                G.add_edge(src, dest)
        try:
            cycle = nx.find_cycle(G, orientation='original')
            return cycle
        except nx.NetworkXNoCycle:
            return None

    # Assuming to_node is your list
    cycle = detect_cycles(to_node), 
    print("Cycle detected:", cycle)

    # we set EF to 1.0 for links that aren't measuring any input
    #this section may need review later
    link_escape_frac = [1.0 if in_val == 0.0 else out/in_val for in_val, out in zip(N_conc_in, N_conc_ds)]

    link_delivery_ratio = [0.0] * n_links

    visited_links = set()  # Track visited links to detect loops

    for l in range(n_links):
        ll = l
        
        #print(f"Current link: {ll}, Target link: {to_node[ll]}, Outlet link: {outlet_link}")

        #link_delivery_ratio[l] = link_escape_frac[l]
        
        while ll != outlet_link:
            if ll in visited_links or ll < 0 or ll >= n_links:
                break

            visited_links.add(ll)
            ll = to_node[ll]

            if ll >= 0 and ll < n_links:
                link_delivery_ratio[l] *= link_escape_frac[ll]
        
        visited_links.clear()  # Reset for the next link

    return link_delivery_ratio, link_escape_frac


"Compare two streammodels' network constants - just prints differences for now"

#straight from co-pilot, not double checked yet because this isn't critical to running NNM 

def compare_network_constants(sm1, sm2):
    nc1 = sm1['nc']
    nc2 = sm2['nc']

    if nc1['n_links'] != nc2['n_links']:
        print("n_links")

    if nc1['outlet_link'] != nc2['outlet_link']:
        print("outlet_link")

    if nc1['gage_link'] != nc2['gage_link']:
        print("gage_link")

    if nc1['gage_flow'] != nc2['gage_flow']:
        print("gage_flow")

    feature_diffs = [i for i, (a, b) in enumerate(zip(nc1['feature'], nc2['feature'])) if a != b]
    if feature_diffs:
        print("feature_diffs", feature_diffs)

    us_area_diffs = [i for i, (a, b) in enumerate(zip(nc1['us_area'], nc2['us_area'])) if a != b]
    if us_area_diffs:
        print("us_area_diffs", us_area_diffs)

    contrib_area_diffs = [i for i, (a, b) in enumerate(zip(nc1['contrib_area'], nc2['contrib_area'])) if a != b]
    if contrib_area_diffs:
        print("contrib_area_diffs", contrib_area_diffs)

    contrib_n_load_factor_diffs = [i for i, (a, b) in enumerate(zip(nc1['contrib_n_load_factor'], nc2['contrib_n_load_factor'])) if a != b]
    if contrib_n_load_factor_diffs:
        print("contrib_n_load_factor_diffs", contrib_n_load_factor_diffs)

    link_len_diffs = [i for i, (a, b) in enumerate(zip(nc1['link_len'], nc2['link_len'])) if a != b]
    if link_len_diffs:
        print("link_len_diffs", link_len_diffs)

    wetland_area_diffs = [i for i, (a, b) in enumerate(zip(nc1['wetland_area'], nc2['wetland_area'])) if a != b]
    if wetland_area_diffs:
        print("wetland_area_diffs", wetland_area_diffs)

    pEM_diffs = [i for i, (a, b) in enumerate(zip(nc1['pEM'], nc2['pEM'])) if a != b]
    if pEM_diffs:
        print("pEM_diffs", pEM_diffs)

    fainN_diffs = [i for i, (a, b) in enumerate(zip(nc1['fainN'], nc2['fainN'])) if a != b]
    if fainN_diffs:
        print("fainN_diffs", fainN_diffs)

    fainC_diffs = [i for i, (a, b) in enumerate(zip(nc1['fainC'], nc2['fainC'])) if a != b]
    if fainC_diffs:
        print("fainC_diffs", fainC_diffs)


"""
    save_model_results(model::StreamModel, filename::String)

Writes model results to csv file
"""

