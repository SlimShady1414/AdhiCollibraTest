import json

from collibra_lib import CollibraAPI, log, COLORS
import os
from consts import *
import re


col = CollibraAPI()

def get_community_id(community_name): 
    response = col.call(url_path='communities', parameters={'name': community_name, "nameMatchMode": "EXACT"})
    return response['results'][0]['id']

def get_domain_id(domain_name, community_id):
    response = col.call(url_path='domains', parameters={'name': domain_name, "communityId": community_id})
    return response['results'][0]['id']

def get_data_product_and_version(domain_id, data_product_name,dpv_id):
    response = col.call(url_path='assets', parameters={'name': data_product_name, "domainId": domain_id, "typePublicIds": DATA_PRODUCT,"nameMatchMode": "EXACT"})
    if response and response.get('results'):
        data_product = response['results'][0]
        
        relations_response = col.call(url_path='relations', parameters={'targetId': dpv_id})
        data_product_version = relations_response['results'][0]['target']
        return data_product, data_product_version

def get_dpv_status (dpv_name): #get data product version status
    response = col.call(url_path='assets', parameters={'name': dpv_name, "typePublicIds": DATA_PRODUCT_VERSION,"nameMatchMode": "EXACT"})
    return response['results'][0]['status']['name']

def get_ord_package(dpv_id): #Get ORD package part of dp version
    response = col.call(url_path='relations', parameters={'sourceId': dpv_id,'typePublicId':DP_VERSION_TO_ORD_PACKAGE}) 
    payload = []

    for result in response.get('results', []):
        payload.append({
            "target_id": result['target']['id'],
            "target_name": result['target']['name']
        })
    return payload

def get_domain_objects(dpv_id):#Get domain objects realted to dp version
    response = col.call(url_path='relations', parameters={'sourceId': dpv_id,'typePublicId': DP_VERSION_TO_DOMAIN_OBJECT}) 
    payload = []

    for result in response.get('results', []):
        payload.append({
            "target_id": result['target']['id'],
            "target_name": result['target']['name']
        })
    return payload

def get_nodes(dobj_id): #Get nodes realted to domain object
    response = col.call(url_path='relations', parameters={'sourceId': dobj_id})
    payload = []

    for result in response.get('results', []):
        payload.append({
            "target_id": result['target']['id'],
            "target_name": result['target']['name']
        })
    return payload

def get_odm_entity(dobj_id): #Get odm entity realted to domain object
    response = col.call(url_path='relations', parameters={'targetId': dobj_id,'typePublicId':ODM_ENTITY_TO_DOMAIN_OBJECT}) 
    payload = []

    for result in response.get('results', []):
        payload.append({
            "soucre_id": result['source']['id'],
            "source_name": result['source']['name']
        })
    return payload

def get_attribute_types(asset_id,publicid): #Get attribute values for assets
    response = col.call(url_path='attributes', parameters={"assetId": asset_id,"typePublicIds":publicid})
    return response['results'] 


def create_dpd_template(data_product,domain_object,data_product_version,ord_package,dpv_status):
    Local_id_data_product = get_attribute_types(data_product['id'],LOCAL_ID)[0]['value'] if get_attribute_types(data_product['id'],LOCAL_ID) else ''
    category_data_product = get_attribute_types(data_product['id'],CATEGORY)[0]['value'] if get_attribute_types(data_product['id'],CATEGORY) else ''
    type_data_product = get_attribute_types(data_product['id'],TYPE)[0]['value']
    dp_responsible = get_attribute_types(data_product['id'],RESPONSIBLE)[0]['value'] if get_attribute_types(data_product['id'],RESPONSIBLE) else ''
    name_data_product = data_product['name']
    status_data_product = dpv_status
    dpv_major_version = get_attribute_types(data_product_version['id'],MAJOR_VERSION)[0]['value']
    dpv_minor_version = get_attribute_types(data_product_version['id'],MINOR_VERSION)[0]['value']
    dpv_patch_version = get_attribute_types(data_product_version['id'],PATCH_VERSION)[0]['value']
    short_description_dpv = get_attribute_types(data_product_version['id'], SHORT_DESCRIPTION)[0]['value'] if get_attribute_types(data_product_version['id'], SHORT_DESCRIPTION) else ''
    description_dpv = get_attribute_types(data_product_version['id'],DESCRIPTION)[0]['value'] if get_attribute_types(data_product_version['id'],DESCRIPTION) else ''
    ord_package_namespace = get_attribute_types(ord_package[0]['target_id'],NAMESPACE)[0]['value'] if get_attribute_types(ord_package[0]['target_id'],NAMESPACE) else ''
    ord_package_local_id = get_attribute_types(ord_package[0]['target_id'],LOCAL_ID)[0]['value'] if get_attribute_types(ord_package[0]['target_id'],LOCAL_ID) else ''
    package_major_version = get_attribute_types(ord_package[0]['target_id'],MAJOR_VERSION)[0]['value']
    package_minor_version = get_attribute_types(ord_package[0]['target_id'],MINOR_VERSION)[0]['value']
    package_patch_version = get_attribute_types(ord_package[0]['target_id'],PATCH_VERSION)[0]['value']
    
    dpd_file_temp = {
        "name": Local_id_data_product,  # <dp_local_id>
        "version": f"{int(dpv_major_version)}.{int(dpv_minor_version)}.{int(dpv_patch_version)}", #<dpv_major_version>.<dpv_minor_version>.<dpv_patch_version>
        "category": category_data_product, # <dp_category>
        "type": type_data_product, # <dp_type>
        "title": name_data_product, # <dp_name>
        "status": status_data_product, # <dp_status>
        "namespace": ord_package_namespace, # <ord_package_namespace> # **Data product owner enters this value**
        "responsible":dp_responsible , # <sap:ach>:<dpv_responsible>
        "partOfPackage": f'{ord_package_namespace}:package:{ord_package_local_id}:v{int(package_major_version)}.{int(package_minor_version)}.{int(package_patch_version)}',# <ord_package_namespace>:package:<ord_package_local_id>:v<package_major_version>.<package_minor_version>.<package_patch_version>
        "shortDescription": short_description_dpv,#<dpv_short_description>
        "description": description_dpv,#<dpv_description>
        "entityTypes": [],#**Import from CSN - Domain Objects and GTNC - ODM entities #Need to confirm the mapping with HCM **
        "entities": [] 
    }
    domain_objects = get_domain_objects(data_product_version['id'])
    for domain_object in domain_objects:
        entitytypes = get_attribute_types(domain_object['target_id'],ORD_ID)[0]['value']# <ord_package_namespace>:entityType:<domain_obj_name>:v1
        entity = {
            "name": get_attribute_types(domain_object['target_id'],LOCAL_ID)[0]['value'], #<domain_obj_local_id>
            "nodes": [],
        "main": False
        }
        domain_object_odm_entity = get_odm_entity(domain_object['target_id']) #Get associated ODM Entities for Domain Object
        for odm_entity in domain_object_odm_entity:
            odm_entities = odm_entity['soucre_id']
            odm_ord_id = get_attribute_types(odm_entities,ORD_ID)[0]['value'] 
            dpd_file_temp["entityTypes"].append(odm_ord_id)
#<odm_entity_ord_id>

        domain_object_nodes = get_nodes(domain_object['target_id']) #Get associated Nodes for Domain Object
        for node in domain_object_nodes:
            entity["nodes"].append({ 
                "name": get_attribute_types(node['target_id'],LOCAL_ID)[0]['value'],
                "extensible": True, 
                "root": get_attribute_types(node['target_id'],IS_ROOT_NODE)[0]['value'],  
                "plugins": [] 
            })
        dpd_file_temp["entityTypes"].append(entitytypes)
        dpd_file_temp["entities"].append(entity)
    
    dpd_file_temp['entityTypes'] = sorted(list(set(dpd_file_temp['entityTypes']))) # Deduplicate entityTypes for odm entities 
    log(dpd_file_temp, color=COLORS.GREEN)
    return dpd_file_temp

def create_dpd_file(community_name, domain_name, data_product_name,dpv_id):
    community_id = get_community_id(community_name)
    domain_id = get_domain_id(domain_name, community_id)
    data_product, data_product_version = get_data_product_and_version(domain_id, data_product_name,dpv_id)
    dpv_status = get_dpv_status(data_product_version['name'])
    domain_objects = get_domain_objects(data_product_version['id'])
    ord_package = get_ord_package(data_product_version['id'])

    return create_dpd_template(data_product,domain_objects,data_product_version,ord_package,dpv_status)


def validate_asset_col_validator(asset_id):
    
    # TODO: Why is post and get giving different answers?
    # response = col.call(url_path='validation', parameters={'assetId': asset_id})
    response = col.call(url_path=f'validation/{asset_id}', method='POST')[0]
    error_log = [
        f'<span style="color:red">Validation failed: {result["message"]}</span>'
        for result in response.get("results", [])
        if not result.get("result", True)
    ]
    return error_log

def validate_asset_manual(dpd_file):
    validation_messages = {
        "responsible": "ACH Component missing in Data product",
        "name": "Local ID missing in Data product",
        "version": "Version missing in Data product version",
        "category": "Category missing in Data product",
        "type": "Type missing in Data product",
        "title": "Data product Name missing",
        "status": "Status missing in Data product version",
        "shortDescription": "Short Description missing in Data product version",
        "description": "Description missing in Data product version",
        "namespace": "Namespace missing in Data product",
        "partOfPackage": "Part of Package missing in Data product version",
        "entityTypes": "Link to Domain Objects are missing in Data product version",
    }

    validation_info = [
        message for key, message in validation_messages.items()
        if not dpd_file.get(key)
    ]

    formatted_info = "<br>".join(f"{idx + 1}. {info}" for idx, info in enumerate(validation_info))
    return [f'<span style="color:red">{formatted_info}</span>']

    
    
def Dpd_file():
    try:
        packages_response = col.call(url_path='communities', parameters={'parentId': COMMUNITY_ID})
        packages = packages_response.get('results', [])

        for package in packages: #Loop in the packages within parent community
            community_name = package['name']
            community_id = package['id']
            domains_response = col.call(url_path='domains', parameters={'communityId': community_id})
            domains = domains_response.get('results', []) 

            for domain in domains: #Loop in the domains within each package
                domain_name = domain['name']
                domain_id = domain['id']
                data_products_response = col.call(url_path='assets', parameters={'domainId': domain_id, 'typePublicIds': DATA_PRODUCT}) #loop domain that is package and then loop in the dataproducts within the domain
                
   
                data_products = data_products_response.get('results', []) 
                for data_product in data_products: #Loop in the data products within each domain
                    data_product_name = data_product['name']
                    # get dp version
                    data_product_version_response = col.call(
                    url_path='assets',
                    parameters={
                        'domainId': domain_id,
                        'typePublicIds': DATA_PRODUCT_VERSION
                    })
                    data_product_versions = data_product_version_response.get('results', [])
                    # print(json.dumps(data_product_versions,indent =4))
                    for data_product_version in data_product_versions:
                        dpv_id = data_product_version['id']
                        dpv_status = data_product_version['status']['name']
                        if dpv_status != 'In Development': #Check if the status of the data product version is in development
                    
                            try:
                                dpd_file = create_dpd_file(community_name, domain_name, data_product_name,dpv_id) #loop in the data products,domain,community
                                if not dpd_file["entities"] or any(not entity["nodes"] for entity in dpd_file["entities"]):
                                    raise ValueError("Entities or nodes are empty")
                                script_dir = "hcm_dpd/DPDFiles/" #Create a directory for DPD files
                                namespace = dpd_file['namespace'].replace('.', '/')
                                out_dir = os.path.join(script_dir, namespace)
                                # print(namespace, out_dir)
                                os.makedirs(out_dir, exist_ok=True)
                                file_name = f"{re.sub(r'[^A-Za-z0-9]', '', data_product_name).replace(' ', '')+'DP'}.json"
                                file_path = os.path.join(out_dir, file_name)
                                with open(file_path, 'w') as json_file:
                                    json.dump(dpd_file, json_file, indent=2)

                                validation_api_resp = validate_asset_col_validator(data_product_version['id'])
                                val_info_tag = validate_asset_manual(dpd_file)
                    
                                json_data = {
                                    "values": val_info_tag + validation_api_resp,
                                    "typePublicId": DPD_ERROR_LOG
                                    }
                                                        
                                col.call(url_path=f'assets/{data_product_version['id']}/attributes',
                                            method='PUT',
                                            json=json_data)
                                    

                            except Exception as e:                                                             
                                error_tag = validate_asset_manual(dpd_file)
                                validation_api_resp = validate_asset_col_validator(data_product_version['id'])
                                json_data = {
                                    "values": list(set(error_tag + validation_api_resp)),
                                    "typePublicId": DPD_ERROR_LOG
                                }                                                    
                                col.call(url_path=f'assets/{data_product_version['id']}/attributes',
                                            method='PUT',
                                            json=json_data)

    except Exception as e:
            print(f"An error occurred: {e}")

Dpd_file()