from jsonschema import validate
import os
from glob import glob
import json
from datetime import datetime
import requests
import jsonschema
import argparse

schema1= "dataproduct-schema.json"
schema2= "dataset-schema.json"
schema3= "datasource-schema.json"
schema4= "share-schema.json"

fosFolderName1 = "dataproducts"
fosFolderName2 = "datasets"
fosFolderName3 = "datasources"
fosFolderName4 = "shares"

def inputARG():
    parser = argparse.ArgumentParser(description="Provide Personal Access Token and continueOnError")
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('--PersonalAccessToken',required = True, type= str, help='Github User Personal Access token', default=None)
    optional.add_argument('--continueOnError', type= str, help='Use either Yes or No.Should script raise an exception on encountering errors or only show errors in console', default= 'Yes')
    args = parser.parse_args()
    return args.PersonalAccessToken, args.continueOnError

def numberOfLinesInErrorFile(fosFolderName):
    with open(r"./results/ValidatorErrors_"+ fosFolderName + ".txt", "r") as fp:
        for count, line in enumerate(fp):
            pass
    print("Total Number of Lines in Validator Error file: ", count +1)
    ARG=inputARG()
    #print(ARG[0])
    print("continueOnError:" +ARG[1])
    if (count +1) >1 and ARG[1] == "No":
      raise Exception("Failure due to errors observed in the FOS files")




# define the function to validate FOS files and try to reuse it for multiple fos_dpp subfolders
def validateSchemaS4FOSfiles(schemaVar,fosFolderName):
    # Trying to use raw.github url to fetch json content of schema files, we need also PAT of a user with valid access.
    ARG=inputARG()
    #print(ARG[0])
    print(ARG[1])
    page = requests.get(f'https://raw.github.tools.sap/bdc-fos/dp-metadata/main/schemas/json/' + schemaVar, headers = {'Authorization': 'token '+ARG[0]})
    print(page.status_code)
    print(page.text)
    schema_json=page.json() # If 404: Not Found returned , it fails here itself. Issue mostly in PAT used.
    with open("./schemas/" + schemaVar, 'w') as f5:
        f5.write(f"{page.text}")
    # List of Path of Instance of schema i.e generated FOS files path
    json_files_path_dataproducts = glob(os.path.join('../../fos_dpd/' + fosFolderName + "/sap/sf/" , '*','*.json'))
    print (json_files_path_dataproducts)
    with open("./results/ValidatorErrors_"+ fosFolderName + ".txt", 'w') as f:
        #f.write("Printing Validation Errors in generated FOS files against " + schemaVar + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n")
        f.write("Printing Validation Errors in generated FOS files against " + schemaVar + "\n")
    for file in json_files_path_dataproducts:
        with open(file, 'r') as f:
            json_instance_object = json.load(f)
            validator= jsonschema.Draft202012Validator(schema_json)
            print(file)
            errors = validator.iter_errors(json_instance_object)  # get all validation errors
            for e in errors:
                print(e)
                with open("./results/ValidatorErrors_"+ fosFolderName + ".txt", 'a') as f2:
                    f2.write(f"{file}\n{e}\n\n"+"--------------------------------------------------"+"\n")



# call the function to validate generated FOS files against schemas
validateSchemaS4FOSfiles(schema1,fosFolderName1)
validateSchemaS4FOSfiles(schema2,fosFolderName2)
validateSchemaS4FOSfiles(schema3,fosFolderName3)
validateSchemaS4FOSfiles(schema4,fosFolderName4)

# In case execution needs to be terminated immediately , we need to use optional argument "--continueOnError No" , By default execution is not terminated"
numberOfLinesInErrorFile(fosFolderName1)
numberOfLinesInErrorFile(fosFolderName2)
numberOfLinesInErrorFile(fosFolderName3)
numberOfLinesInErrorFile(fosFolderName4)
