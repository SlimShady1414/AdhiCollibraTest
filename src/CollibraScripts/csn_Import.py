import os
import json
import shutil
from collibra_lib import CollibraAPI, log, COLORS
from consts import *

col = CollibraAPI()

def extract_entities(csn_file):
    with open(csn_file, 'r') as file:
        csn_data = json.load(file)
    # domain_object = csn_data.get('meta', {}).get('__name', 'UnknownRoot') # this is extracting the name from the meta object in the csn file
    # Extract the names of each entity and check for @ObjectModel.compositionRoot
    entities = csn_data.get('definitions', {})
    rootentity_definition = next(iter(entities))
    rootentity  = next(iter(entities.values()))

   #Attributes for Domain Object
    entity_type = rootentity.get('@EntityRelationship.entityType','')
    if entity_type:
        domain_object = entity_type
    else:
        domain_object = rootentity_definition
    
    odm_entity = rootentity.get('@ODM.entityName','')
    if odm_entity:
        odm_entity_name = odm_entity
    else:
        odm_entity_name = domain_object
    
    title = rootentity.get('@EndUserText.label','')
    local_id = domain_object.split(':')[-1]
    namespace = domain_object.split(':')[0]
    ordid = f"{namespace}:entityType:{local_id}:v1"
    description = rootentity.get('@EndUserText.quickInfo','')
    short_description = rootentity.get('@EndUserText.heading','')


    nodes = []
    for entity_name, entity_properties in entities.items():
        # Check if the current entity is of kind 'entity'
        if entity_properties.get('kind') == 'entity': 
            is_root = entity_properties.get('@ObjectModel.compositionRoot', False) #get the root from the csn file 
            node_name = entity_properties.get('@EntityRelationship.entityType',entity_name)
            node_local_id = node_name.split(':')[-1]
            node_title = entity_properties.get('@EndUserText.label','')
            node_description = entity_properties.get('@EndUserText.quickInfo','')
            node_short_description = entity_properties.get('@EndUserText.heading','') 
            nodes.append({
                'name': node_name,
                'is_root': str(is_root).capitalize(),
                'local_id': node_local_id,
                'title': node_title,
                'namespace': namespace,
                'ordid': f"{namespace}:entityType:{node_local_id}:v1",
                'description' : node_description,
                'short_description' : node_short_description
            }) #keep adding this when there is any other properties required from csn
    # Construct the payload
    payload = {domain_object: nodes} # nodes are extracted from the definition objects per entity kind in the csn file
    return payload,odm_entity_name,title,local_id,ordid,namespace,description,short_description

#Change the attributes of the domain object
def change_domain_object_attributes(id,local_id,title,ordid,namespace,description,short_description): 
    attributes = [{
        "typePublicId": LOCAL_ID,
        "values": [local_id],
    },
     {   "typePublicId": TITLE,
         "values": [title]
    },
    {   "typePublicId": ORD_ID,
         "values": [ordid]

    },
         {   "typePublicId": SHORT_DESCRIPTION,
         "values": [""]
    },
         {   "typePublicId": DESCRIPTION,
         "values": [""]
    },
         {   "typePublicId": NAMESPACE,
         "values": [namespace]
    },
             {   "typePublicId": DESCRIPTION,
         "values": [description]
    },
             {   "typePublicId": SHORT_DESCRIPTION,
         "values": [short_description]
    }
        ]
    for attribute in attributes:
        response = col.call(url_path=f'assets/{id}/attributes', json=attribute, method='put')
        log(response,COLORS.BLUE)


#change the attributes of the nodes
def change_node_attributes(id,is_root,local_id,title,ordid,namespace,description,short_description): 
    attributes = [{
        "typePublicId": IS_ROOT_NODE,
        "values": [is_root],
    },
     {   "typePublicId": TITLE,
         "values": [title]
    },
    {   "typePublicId": ORD_ID,
         "values": [ordid]

    },
         {   "typePublicId": SHORT_DESCRIPTION,
         "values": [""]
    },
         {   "typePublicId": DESCRIPTION,
         "values": [""]
    },
         {   "typePublicId": NAMESPACE,
         "values": [namespace]
    },
          {   "typePublicId": LOCAL_ID,
         "values": [local_id]
    },
                {   "typePublicId": DESCRIPTION,
         "values": [description]
    },
             {   "typePublicId": SHORT_DESCRIPTION,
         "values": [short_description]
    }
        ]
    for attribute in attributes:
        response = col.call(url_path=f'assets/{id}/attributes', json=attribute, method='put')
        log(response,COLORS.BLUE)

#Create Objects from csn file
def create_metadata_obj(obj, domain):
    obj_payload = {
        "name": obj,
        "typePublicId": DOMAIN_OBJECT,
        "domainId": domain
    }
    response = col.call(url_path=f'assets', json=obj_payload, method='post')
    return response['id']

#Create Nodes from csn file 
def create_metadata_nodes(node, node_fd):
    entity_payload = {
        "name": node,
        "typePublicId": NODES,
        "domainId": node_fd
    }
    response = col.call(url_path=f'assets', json=entity_payload, method='post')
    return response['id']

#Create mutiple relations between objects and nodes
def create_relation(obj_id, node_id):
    relation = [{
        "sourceId": obj_id,
        "targetId": node_id,
        "typePublicId": DOMAIN_OBJECT_TO_NODE
    }]
    response = col.call(url_path='relations/bulk', json=relation, method='post')
    log(response, color=COLORS.GREEN)

#Check if the name of the asset is case insensitive
def check_case_insenstive_match(incomming_name, existing_name):
    return incomming_name.lower() == existing_name.lower()

#Update the asset name if it is case insensitive
def update_asset_name(asset_id, updated_name):
    updated_json = {
        "name": updated_name,
        "displayName": updated_name}
    col.call(url_path=f'assets/{asset_id}', json=updated_json, method='patch')

#Get the nodes from collibra. Incase of just case insensitive match, update the name get the existing node uuid
def get_nodes(asset_name):
    response = col.call(url_path='assets', parameters={'name': asset_name, "domainId": METADATA_NODES, "nameMatchMode": "END"})
    if response and response.get('results'):
        node_name_in_collibra = response['results'][0].get('name')
        node_uuid_in_collibra = response['results'][0].get('id')
        case_insens_match = check_case_insenstive_match(asset_name, node_name_in_collibra)
        if case_insens_match:
            update_asset_name(node_uuid_in_collibra, asset_name) 
        return response['results'][0]
    return None


#Get the objects from collibra. Incase of just case insensitive match, update the name get the existing object uuid
def get_objects(asset_name):
    response = col.call(url_path='assets', parameters={'name': asset_name, "domainId": METADATA_OBJECTS, "nameMatchMode": "END"})
    if response and response.get('results'):
        dobj_name_in_collibra = response['results'][0].get('name')
        dobj_uuid_in_collibra = response['results'][0].get('id')
    
        case_insens_match = check_case_insenstive_match(asset_name, dobj_name_in_collibra)
        if case_insens_match:
            update_asset_name(dobj_uuid_in_collibra, asset_name) 
        return response['results'][0]
    return None

def get_odm_entities(asset_name):
    response = col.call(url_path='assets', parameters={'name': asset_name, "domainId": ODM_ENTITY_DOMAIN_ID, "nameMatchMode": "EXACT"})
    if response and response.get('results'):
        return response['results'][0]
    return None

def odm_to_domain_object_relation(odm_id, domain_id):
    relation = [{
        "sourceId": odm_id,
        "targetId": domain_id,
        "typePublicId": ODM_ENTITY_TO_DOMAIN_OBJECT
    }]
    response = col.call(url_path='relations/bulk', json=relation, method='post')
    log(response, color=COLORS.GREEN)

def csn_import(csn_file):
    payload,odm_entity_name,title,local_id,ordid,namespace,description,short_description = extract_entities(csn_file)
    obj = list(payload.keys())[0]
    domain = METADATA_OBJECTS
    existing_obj = get_objects(obj) # Check if the object already exists and overwrite it
    if existing_obj and obj.lower() == existing_obj.get('name').lower():
        obj_id = existing_obj.get('id')
    else:
        obj_id = create_metadata_obj(obj, domain)
    change_domain_object_attributes(obj_id,local_id,title,ordid,namespace,description,short_description)
    nodes_fd = METADATA_NODES
    for node in payload[obj]:
        node_name = node['name']
        is_root = node['is_root']
        local_id = node['local_id']
        title = node['title']
        ordid = node['ordid']
        namespace = node['namespace']
        node_exists = get_nodes(node_name) # Check if the node already exists and overwrite and relate it
        if node_exists and node_name.lower() == node_exists.get('name').lower():
            node_id = node_exists.get('id')
            create_relation(obj_id, node_id)
        else:
            node_id = create_metadata_nodes(node_name, nodes_fd)
            create_relation(obj_id, node_id)
        change_node_attributes(node_id, is_root,local_id,title,ordid,namespace,description,short_description)
    if odm_entity_name != None:
        odm_entity = get_odm_entities(odm_entity_name)
        if odm_entity:
            odm_id = odm_entity.get('id')
            odm_to_domain_object_relation(odm_id, obj_id)
        else:
            log(f"ODM entity '{odm_entity_name}' not found.", COLORS.YELLOW)

def domain_and_nodes_import(folder_path):
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.json') and 'archive' not in root:
                csn_file = os.path.join(root, filename)
                csn_import(csn_file)
                archive_folder = os.path.join('domain_import/csn', os.path.relpath(root, folder_path), 'archive', filename)
                os.makedirs(os.path.dirname(archive_folder), exist_ok=True)
                shutil.move(csn_file, archive_folder)

domain_and_nodes_import('domain_import/csn')

