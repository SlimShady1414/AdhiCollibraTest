using { person_biographicalDetail, person_personalDetail } from './input/sap/sf/workforce/Person';
 
@name: 'PersonInfo'
@title: 'Person Info'
@description: 'PersonInfo description'
@shortDescription: 'PersonInfo short description'
@version: '1.0.0'
@type: 'derived'
@partOfPackage: 'sap.sf.analytics'
@responsible: 'new'
@category: 'business-object'
@namespace: 'sap.sf.analytics'

@transformer: 'sap.sf.analytics:transformer:personInfo:v1'

service PersonInfo {
 

    @EndUserText.label: 'Biographical Information'
    entity PersonInfo as select from person_biographicalDetail as bio left join person_personalDetail as details on
    bio.id = details.person_id_virtual
    {
        bio.id,
        details.firstName,
        details.lastName,
        details.middleName,
        details.displayName,
        details.preferredName,
        details.startDate,
        details.endDate

        
    }     
}