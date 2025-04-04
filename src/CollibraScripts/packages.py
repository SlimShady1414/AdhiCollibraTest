# Example payload
import requests
import os
import json
from base64 import b64encode
import pandas as pd
import re
from collibra_lib import CollibraAPI,log,COLORS
from consts import *
import os
import shutil


col = CollibraAPI()

paths = {}
paths["packages"] = os.path.join(os.path.dirname(__file__), '../../fos_dpd/packages/')


def get_attribute_types(asset_id,publicid): #Get attribute values for assets
    response = col.call(url_path='attributes', parameters={"assetId": asset_id,"typePublicIds":publicid})
    return response['results'] 


def get_ord_package(package_name): #Get ORD package part of dp version
    response = col.call(url_path='assets', parameters={'name': package_name,'typePublicId':ORD_PACKAGE}) 
    return response['results']

def write_file(obj, main_path, sub_path, name, version):
    path = main_path + sub_path + "/"
    os.makedirs(path, exist_ok=True)

    filename = path + name + "_" + version + ".json"
    with open(filename, "w") as f:
        f.write(json.dumps(obj, indent=3))

def package_dir(namespace : str, item : str):
    parts = namespace.split(".")
    ##parts.insert(0, item) leave it for now
    return '/'.join(parts)

def ord_relation(package_id): #Get ORD package part of dp version
    response = col.call(url_path='relations', parameters={'targetId': package_id,'typePublicId':DP_VERSION_TO_ORD_PACKAGE}) 
    payload = []

    for result in response.get('results', []):
        payload.append({
            "target_id": result['source']['id'],
            "target_name": result['source']['name']
            # "target_status": result['source']['status']
        })
    return payload


def get_dpv_status (dpv_name): #get data product version status
    response = col.call(url_path='assets', parameters={'name': dpv_name, "typePublicIds": DATA_PRODUCT_VERSION,"nameMatchMode": "EXACT"})
    return response['results'][0]['status']['name']



def package_stub():
    
    packages_response = col.call(url_path='assets', parameters={'domainId': PACKAGES,'communityId': COMMUNITY_ID})
    ord_packages = packages_response.get('results', []) 

    for ord_package in ord_packages:
            package_id = ord_package.get('id')
            get_linked_dpvs = ord_relation(package_id)
            if get_linked_dpvs != []:
                for dpv in get_linked_dpvs:
                    dpv_status = dpv['target_name']
                    status = get_dpv_status(dpv_status)
                    if status != 'In Development':
                        name = get_attribute_types(ord_package.get('id'), LOCAL_ID)[0]['value']
                        namespace = get_attribute_types(ord_package.get('id'), NAMESPACE)[0]['value']
                        major_version = get_attribute_types(ord_package.get('id'), MAJOR_VERSION)[0]['value']
                        minor_version = get_attribute_types(ord_package.get('id'), MINOR_VERSION)[0]['value']
                        patch_version = get_attribute_types(ord_package.get('id'), PATCH_VERSION)[0]['value']
                        vendor = 'sap:vendor:SAP:'
                        title = get_attribute_types(ord_package.get('id'), TITLE)[0]['value'] if get_attribute_types(ord_package.get('id'), TITLE) else ''
                        short_description = get_attribute_types(ord_package.get('id'), SHORT_DESCRIPTION)[0]['value'] if get_attribute_types(ord_package.get('id'), SHORT_DESCRIPTION) else ''
                        description = get_attribute_types(ord_package.get('id'), DESCRIPTION)[0]['value'] if get_attribute_types(ord_package.get('id'), DESCRIPTION) else ''
                        payload = {
                            'name': name,
                            'namespace': namespace,
                            'version': f'{int(major_version)}.{int(minor_version)}.{int(patch_version)}',
                            'vendor': vendor,
                            'partOfProducts': ['sap:product:SAPSuccessFactors:'],
                            'title': title,
                            'shortDescription': short_description,
                            'description': description
                        }
                        write_file(payload, paths["packages"], package_dir(namespace, "payload"), name, payload['version'])
                        log(payload,COLORS.GREEN)
    return payload

if __name__ == "__main__":
   package_stub()
