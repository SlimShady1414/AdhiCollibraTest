# HCMGenerator

## Actions status
## Actions Status

[![HCM events to CSN → Collibra Import](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/Events_Csn_Collibra.yml/badge.svg?branch=main)](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/Events_Csn_Collibra.yml)
[![DPD, FOS and Packages Generator](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/fos_stub_gen.yml/badge.svg?branch=main)](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/fos_stub_gen.yml)
[![CSN Validation Results](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/ValidateCSNfiles.yml/badge.svg)](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/ValidateCSNfiles.yml)
[![Schema Validation Results](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/ValidateJSONfiles.yml/badge.svg)](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/ValidateJSONfiles.yml)
[![HCMGen to bdc-fos(sf)](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/Push_from_HCMGenerator_to_dp-metadata.yml/badge.svg)](https://github.tools.sap/bdc/HCMGenerator/actions/workflows/Push_from_HCMGenerator_to_dp-metadata.yml)

## Data products generator for HCM

## Steps to Generate DPD Files :

1. **Push Events to Domain Import**
 
    HCM Module Developer to push events to `domain_import/events/<namespace=foundationobjects/jsonfiles>` (e.g., `sap.sf.foundationobjects`)

Example:

```
├── foundationobjects
│   └── Location-metadata.json
└── workforce
    ├── Person-metadata.json
    └── assignment_metadata.json
```

2. **Planning Excel Import**

    One-time import of the planning Excel file.


3. **Generate DPD and FOS**

     DPD and FOS files can be generated by Git Action. (Refreshes every 12 hours)
