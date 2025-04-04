# DomainTypes Public Id's 

DATA_PRODUCT_FOLDER = 'DataProductFolder_C' # Domain Type for Data Product Folder
GLOSSARY = "Glossary" # Domain Type for Metadata Objects and Nodes Folder
PACKAGES_DT = "Package_C" 

# AssestTypes Public Id's

SAP_PRODUCTS = "SapProducts_C"
PROVIDER_APPLICATION = "ProviderApplication_C" # Assest Type for Provider Applications
ORD_PACKAGE = "OrdPackage_C" # Assest Type for ORD Packages
DOMAIN_OBJECT = "DomainObject_C" # Assest Type for Domain Objects
NODES = "Node_C" # Assest Type for Nodes
ODM_ENTITY = "OdmEntityType_C" # Assest Type for ODM Entities
DATA_PRODUCT = "DataProduct_C" # Assest Type for Data Products
DATA_PRODUCT_VERSION = "DataProductVersion_C" # Assest Type for Data Product Versions

# RelationTypes Public Id's

DP_TO_DP_VERSION = "DataProductHasDataProductVersion_C" # Relation Type for Data Product to Data Product Versions 1:N
ORD_TO_PROVIDER_APP = "OrdPackageIsPartOfProviderApplication_C" # Relation Type for ORD Package to Data Product Versions 1:N
DP_VERSION_TO_DOMAIN_OBJECT = "DataProductVersionContainsDomainObject_C" # Relation Type for Data Product Version to Domain Objects 1:N
DOMAIN_OBJECT_TO_NODE = "DomainObjectContainsNode_C" # Relation Type for Domain Objects to Nodes 1:N
DP_VERSION_TO_ORD_PACKAGE = "DataProductVersionIsPartOfOrdPackage_C" 
ODM_ENTITY_TO_DOMAIN_OBJECT = "OdmEntityTypeIsRepresentedByDomainObject_C" # Relation Type for ODM Entities to Nodes 1:N

# Statuses Resource Id's

CANDIDATE = "00000000-0000-0000-0000-000000005008" # Status for Candidate
ACCEPTED = "00000000-0000-0000-0000-000000005009" # Status for Accepted
INDEVELOPMENT = "01953d5e-eb88-753d-a3dd-65bdd5c9921e" # Status for Development

# Specific to HCM LOB 


COMMUNITY_ID = "01959995-cdf6-743c-96f6-5ab4a21c34a1" 
METADATA_OBJECTS = "01959996-1f55-7128-8368-a5ad21a617e5"    
METADATA_NODES = "01959996-4bbe-7667-a428-24694d0cab37"    
PROVIDER_APPLICATION_ASSEST = "019546d1-7cc1-709b-b63b-16d631f1a084" # HCM Provider Application
PACKAGES = "01959996-8b3d-78f5-8d51-315dd91cd44d"
ODM_ENTITY_DOMAIN_ID = "01953c8c-6121-7601-8fc3-3c9e05b577f9"
PRODUCTS = "0195469d-307b-78db-9ae4-c704c2151a38"

# Attributes

TYPE = "Type_C" # Selection
LOCAL_ID = "LocalID_C" # Text
CATEGORY = "DataProductCategory" # Selection
MAJOR_VERSION = "MajorVersion_C" # Number
MINOR_VERSION = "MinorVersion_C" # Number
PATCH_VERSION = "PatchVersion_C" # Number  
NAMESPACE = "Namespace_C" # Text
BLOCKING_JIRA_ISSUE = "BlockingJiraIssue_C" # Text 
CONSUMPTION_TEST_STATUS = "ConsumptionTestStatus_C" # Selection
DESCRIPTION = "Description" # Text
DOMAIN_OBJECT_CATEGORY = "DomainObjectCategory_C" # Selection
DPD_FILES_GENERATED = "DpdFilesGenerated_C" # Boolean
DPP_REVIEW_STATUS = "DppReviewStatus_C" # Selection
GTNC_LINK = "GtncLink_C" # Text
IMPLEMENTATION_JIRA_ITEMS = "ImplementationJiraItems_C" # Text
IS_ROOT_NODE = "IsRootNode_C" # Boolean
ORD_ID = "OrdID_C" # Text
PLANNED_DELIVERY = "PlannedDelivery_C" # Date Selection
RELEASE_STATUS = "ReleaseStatus_C" # Selection
REQUEST_REASON = "RequestReason_C" # Text
RESPONSIBLE = "Responsible_C" # Text
SEMANTIC_VERSION = "SemanticVersion_C" # Text
SHORT_DESCRIPTION = "ShortDescription_C" # Text
STATUS = "Status_C" # Selection
TITLE = "Title_C" # Text
UA_REVIEW_STATUS = "UAReviewStatus_C" # Selection
VALIDATION_TEST_STATUS = "ValidationTestStatus_C" # Selection
VALID_FOR_NAMESPACES = "ValidForNamespaces_C" # Text
DPD_ERROR_LOG = "DpdErrorLog_C" # Text