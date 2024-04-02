import csv
import pandas as pd
import os #standard library for interacting with the operating system; similar to delimited files
import yaml #similar to YAML in Julia; json is a subset of YAML. they are data serialization formats to configure files and exhange data between languages with different data structures
#from dataclasses import dataclass #similar to parameters in Julia; it is a decorator that is used to create a data class

#Julia code imported FileIO, which supported many different file formats. Python has different libraries for different file formats
#So I need to import the file reader for the file format I want to use
#import geopandas as gpd #geopandas is a library for working with geospatial data


#Importing modules from the other files in src
#though I will try to stick to the exact Julia names, go over this section at the end and make sure each data class and fnc name matches the ones actually used in that file**

from link_network import LinkNetwork, calc_routing_depth, get_routing_order, get_headwater_links #imports classes and functions from link_network.py
from StreamModels import StreamModel, ModelConstants, NetworkConstants, ModelVariables


from nnm import * #might be a better way to do this; Julia code seems to have imported all of nnm

from nnm_io import  ModelConstants, StreamModel, NetworkConstants, ModelVariables
from nnm_io import  get_delivery_ratios, save_constants, load_constants, save_model_results, save_model_variables

#from operators import * 

#from FlowRegimes import FlowRegime, FlowRegimeSimResults, evaluate, evaluate2, weighted_avg_nconc, weighted_outlet_nconc, full_eval_flow_regime, write_flow_regime
#from SubNetworks import SubNetworkDef, generate_subnetwork, generate_subnetwork_file, generate_subnetwork_modelparams_file, generate_subnetwork_flowregime_file

