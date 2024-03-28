#random note -- I should make a list of all the packages people will have to pip install to run this code
#also, a lot of my comments are what copilot told me. not my own words! might be an issue?

import os #lets us interact with the operating system to make directories, delete files, etc
import requests #lets us download files from the internet; is a simple API
import subprocess #lets us run other programs from this code; may need to remove??
import zipfile #reading and writing zip files

#If we don't want to import all of os:
#import os.path.join #concatenates separate strings that describe the location of a file or directory
#import os.path.isdir #checks if a given path is a directory
#import os.makedirs #creates new directory at the given path


#We can directly access the data we need from the CyVerse Data Store using the following URL:
input_data_url = "https://de.cyverse.org/dl/d/B8A1E227-19BC-4994-8762-ABE4FCBA348A/LeSueurNetworkData.zip"

#Define paths for our workspace, input data, and results
#We need to define the paths so that we can make sure the directories that we will need exist
workspace = "../data/LeSueur"
inputs_dir = os.path.join(workspace, "inputs")
results_dir = os.path.join(workspace, "results")

#define a main function to run the code; we will define set_up_workspace and download_data functions later
def main():
    set_up_workspace()
    download_data()

"Create data/LeSueur containing inputs and results folders "
def set_up_workspace():
    for path in [workspace, inputs_dir, results_dir]:
        if not os.path.isdir(path):
            os.makedirs(path)

"Download the data from the CyVerse Data Store and unzip it"

def download_data():
    target_file = os.path.join(inputs_dir, "LeSueurNetworkData.zip")
    response = requests.get(input_data_url)
    with open(target_file, 'wb') as f:
        f.write(response.content)
    with zipfile.ZipFile(target_file, 'r') as zip_ref:
        zip_ref.extractall(inputs_dir)
    os.remove(target_file)


#trigger the execution of the program!
main()

#Testing to make sure the code works:

#Verify that the workspace was made correctly/check if directory exists
def verify_workspace():
    for path in [workspace, inputs_dir, results_dir]:
        if not os.path.isdir(path):
            print(f"Directory {path} does not exist.")
        else:
            print(f"Directory {path} exists.")

verify_workspace()

#Verify that the data was downlaoded correctly

def list_all_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            print(os.path.join(root, file))

# Call the function with the path to the directory
list_all_files(inputs_dir)

