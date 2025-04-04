# import pandas as pd
import json
import ast
from os import listdir
from os.path import isfile, join
import os
import glob
import shutil

from file_utils import _purge_old_files, paths, _deep_copy

from fos_utils import _dataproduct , _share, _dataset, _datasources, _getNodes

released = {}

# clean up the target directories
_purge_old_files()


# generate FOS files into a flat strcuture
all_dp_json_files = [
    os.path.join(root, file)
    for root, _, files in os.walk(paths["input"])
    for file in files
    if file.endswith("DP.json")
]
for file_path in all_dp_json_files:
    with open(file_path) as input_file:

        
        current_json = json.load(input_file)

        _dataproduct(current_json=current_json)
        _share(current_json=current_json)
        _dataset(current_json=current_json)
        _datasources(current_json=current_json)

        # mark some data for the released data products to save the parsing afterwards
        if current_json["status"] == "centApproved":
            released[current_json["name"]] = dict(namespace = current_json["namespace"], version = current_json["version"], nodes = _getNodes(current_json=current_json))




# copy the files into the correct folder structure
for n, fn in released.items():

    _deep_copy(n, fn, "dataset")
    _deep_copy(n, fn, "dataproduct")
    _deep_copy(n, fn, "share")

    for node in fn["nodes"]:
        _deep_copy(node, fn, "datasource")
#        _deep_copy(node, fn, "csn")

print("FOS files generated successfully")


    



