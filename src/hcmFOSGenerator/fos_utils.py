
import json 
import os 
from file_utils import fos_dir, write_file, paths, copy_file_deep


def _namespace(current_json):
    namespace = current_json['namespace']
    """ partOfPackage = current_json['partOfPackage'] 
    namespace = partOfPackage.split(':') [0]     """
    if len(namespace) < 1:
        namespace = "!!Namespace is not set in the dpd file"
    return namespace

def _dataproduct(current_json):
    dataproduct = {}

    namespace = _namespace(current_json)
    name = current_json['name']

    dataproduct["name"] = name
    dataproduct["title"] = current_json['title']
    dataproduct["description"] = current_json['description']
    dataproduct["shortDescription"] = current_json['shortDescription']
    dataproduct["partOfPackage"] = current_json['partOfPackage']
    dataproduct["version"] = current_json['version']
    dataproduct["type"] = current_json['type']
    dataproduct["responsible"] = current_json['responsible']

    if current_json['category'] == "businessObject" or current_json['category'] == "business-object":
        dataproduct["category"] = "business-object"
    else:
        dataproduct["category"] = "other"

    dataproduct["entityTypes"] = []
    for et in current_json["entityTypes"]:
        dataproduct["entityTypes"].append(et)

    dataproduct["datasets"] = [namespace  + ":" + "dataset" + ":" + name + ":" + "v1.0.0"]
    dataproduct["shares"] = [namespace  + ":" + "share" + ":" + name + ":" + "v1.0.0"]

    write_file(dataproduct, paths["dataproduct"], fos_dir(namespace, "dataproducts"), name, current_json['version'])

    dataproduct.clear()

def _getNodes(current_json):
    nodes = []
    for e in current_json['entities'] :
        for n in e['nodes']:
            nodes.append(n["name"])
    return nodes

def _share(current_json):
    share = {}

    namespace = _namespace(current_json)
    name = current_json['name']

    share["name"] = name
    share["namespace"] = namespace
    share["title"] = current_json['title']
    share["shortDescription"] = current_json['shortDescription']
    share["description"] = current_json['description']
    share["version"] = current_json['version']

    extensible = {}
    share["extensible"] = extensible
    extensible["supported"] = "automatic"
    extensible["description"] = "Extensions to the model are automatically integrated in the API"

    # build nested structure - share < hdlfsSchemas < shareTables
    share["hdlfsSchemas"] = []

    hdlfsSchema = {"name" : name}
    share["hdlfsSchemas"].append(hdlfsSchema)

    hdlfsSchema["shareTables"] = []

    # add the subnodes
    nodes = _getNodes(current_json=current_json)
    for n in nodes :
        shareTable = {}
        shareTable["name"] =  n
        shareTable["version"] = "1.0.0"
        shareTable["medallionLayer"] = "silver"
        hdlfsSchema["shareTables"].append(shareTable)

    write_file(share, paths["share"], fos_dir(namespace, "shares"), name, current_json['version'])

    share.clear()

def _dataset(current_json):
    namespace = _namespace(current_json)
    name = current_json['name']

    dataset = {"name" : name}
    dataset["namespace"] = namespace
    dataset["version"] = current_json['version']
    datasources = []
    dataset["dataSources"] = datasources

    # loop at datasources - entities > name
    for e in current_json['entities'] :
        datasources.append(namespace  + ":" + "dataSource" + ":" + e["name"].capitalize() + ":" + "v" +current_json['version']) #Temp fix as HCM requested to upper camel case the first word of  datasource name

    datasources.sort()    
    write_file(dataset, paths["dataset"], fos_dir(namespace, "datasets"), name, current_json['version'])

    dataset.clear()
    datasources.clear()


def _datasource(n, current_json):
    datasource = {}
    current_file_name = n.capitalize() #  Temp fix as HCM requested to upper camel case the first word of  datasource name
    datasource["name"] = current_file_name
    datasource["namespace"] = _namespace(current_json)
    datasource["version"] = current_json['version']

    connector = {}
    datasource["connector"] = connector
    connector["connectorName"] = "dsapi"
    connector["outboundMedallionLayer"] = "staging"
    # additionalParameters = {}
    # connector["additionalParameters"] = additionalParameters
    # additionalParameters["beginWatermark"] = "2024-01-01"
    # additionalParameters["schedule"] = "* 8 * * *"

    metadata = {}
    datasource["metadata"] = metadata
    metadata["id"] = f"{_namespace(current_json)}:csnDocument:{n}:v{current_json['version']}" #TODO: check this

    transformers = []
    datasource["transformers"] = transformers
    transformer = {}
    transformer["transformerName"] = "sap.bdc.fos:transformer:jsonlDatasourcePlugins:v1.0.0"
    transformer["outboundMedallionLayer"] = "silver"
    transformers.append(transformer)

    plugins = []
    datasource["plugins"] = plugins
    
    jsonlIngestPlugin = {}
    jsonlIngestPlugin["isEnable"] = True
    jsonlIngestPlugin["primaryKeyColumn"] = "xsapsfseqkeys" #TODO: is this generic?
    jsonlIngestPlugin["watermarkColumn"] = "sequence" #TODO: is this generic?
    jsonlIngestPlugin["watermarkColumnType"] = "cds.Int64"
    plugins.append({"jsonlIngest" : jsonlIngestPlugin})
    jsonlMergePlugin = {}
    jsonlMergePlugin["isEnable"] = True
    plugins.append({"jsonlMerge" : jsonlMergePlugin})
    jsonlDecomposePlugin = {}
    jsonlDecomposePlugin["isEnable"] = True
    jsonlDecomposePlugin["sourceColumnName"] = "data"
    jsonlDecomposePlugin["normalize"] = True
    plugins.append({"jsonlDecompose" : jsonlDecomposePlugin})


    write_file(datasource, paths["datasource"], fos_dir(_namespace(current_json), "datasources"), n.capitalize(), current_json['version']) #Temp fix as HCM requested to upper camel case the first word of datasource name
    return datasource

def csn_document(n, current_json):
    datasource = _datasource(n, current_json)
    name = datasource["name"]
    namespace = datasource["namespace"]

    search_csn_documents = f"{namespace}:{name}"
    csn_path = os.path.join("domain_import", "csn", namespace.split(".")[-1])  # Construct path from namespace

    if os.path.exists(csn_path):
        for root, _, files in os.walk(csn_path):
            for file in files:
                if file.endswith(".json"): 
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        csn_data = json.load(f)
                        entities = csn_data.get('definitions', {})
                        rootentity = next(iter(entities.values()))
                        # Attributes for Domain Object
                        entity_type = rootentity.get('@EntityRelationship.entityType', '')
                        if entity_type:
                            domain_object = entity_type
                            if domain_object.lower() == search_csn_documents.lower():  # Match rootEntity with search
                                copy_file_deep(file_path,fos_dir(namespace, "csn_documents"), "csn")
                                break

def _datasources(current_json):
    for e in current_json['entities'] :
        _datasource(e["name"], current_json)
        csn_document(e["name"], current_json)
    
 