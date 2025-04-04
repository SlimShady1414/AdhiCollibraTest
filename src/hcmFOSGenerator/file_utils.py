import glob
import json
import os
import shutil

# relevant paths
paths = {}
paths["input"] = os.path.join(os.path.dirname(__file__), '../../hcm_dpd/DPDFiles/')
paths["dataset"] = os.path.join(os.path.dirname(__file__), '../../fos_dpd/datasets/')
paths["dataproduct"] = os.path.join(os.path.dirname(__file__), '../../fos_dpd/dataproducts/')
paths["datasource"] = os.path.join(os.path.dirname(__file__), '../../fos_dpd/datasources/')
paths["share"] = os.path.join(os.path.dirname(__file__), '../../fos_dpd/shares/')
paths["csn"] = os.path.join(os.path.dirname(__file__), '../../fos_dpd/csn_documents/')

def _purge_old_files():
    folder_paths = {
        'fos_dataproducts_json': os.path.join(os.path.dirname(__file__), f'../../fos_dpd/dataproducts/'),
        'fos_datasets_json': os.path.join(os.path.dirname(__file__), f'../../fos_dpd/datasets/'),
        'fos_datasources_json': os.path.join(os.path.dirname(__file__), f'../../fos_dpd/datasources/'),
        'fos_shares_json': os.path.join(os.path.dirname(__file__), f'../../fos_dpd/shares/'),
        'fos_csn_json': os.path.join(os.path.dirname(__file__), f'../../fos_dpd/csn_documents/sap/')
    }

    for extension, folder_path in folder_paths.items():
        if not os.path.isdir(folder_path):
            continue
        
        # Delete CSN subfolders
        subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
        for subfolder in subfolders:
            shutil.rmtree(subfolder)

        # Delete files
        pattern = os.path.join(folder_path, f'*.{extension.rsplit("_", 1)[-1]}')
        json_files = glob.glob(pattern)
        for file_path in json_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(e)
                # todo - implement proper logging

def write_file(obj, main_path, sub_path, name, version):
    path = main_path + sub_path + "/"
    os.makedirs(path, exist_ok=True)

    filename = path + name + "_" + version + ".json"
    with open(filename, "w") as f:
        f.write(json.dumps(obj, indent=3))

def get_file_name(name, ftype, version):
    filename = paths[ftype] + "/" + name + "_" + version + ".json"
    return filename

def fos_dir(namespace : str, item : str):
    parts = namespace.split(".")
    ##parts.insert(0, item) leave it for now
    return '/'.join(parts)

def copy_file_deep(source, namespace, ftype):
    target_dir = paths[ftype] + fos_dir(namespace, ftype) + "/"
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    shutil.copy(source, target_dir)

def _deep_copy(name, fn, ftype):
    fname = get_file_name(name, ftype, fn["version"])
    copy_file_deep(fname, fn["namespace"], ftype)