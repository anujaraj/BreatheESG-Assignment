# Data Sources and Column Choices

This document explains why the project uses the selected source files, why those columns matter, and how the data was mapped into ESG categories.

## Why CSV?

CSV is a common delivery format for ESG and operational data.
- It is easy to export from spreadsheets, ERP systems, and utility billing tools.
- The assignment focuses on ingestion and validation, and CSV is a natural fit for that.
- It keeps the pipeline simple and transparent.

## Source types and sample files

### SAP (`backend/sampledata/sap.csv`)
Key columns:
- `Document_Number`
- `Posting_Date`
- `Plant_Code`
- `Material_Description`
- `Quantity`
- `UOM`

Why these columns?
- They capture the essential procurement/fuel consumption event.
- `Quantity` + `UOM` are required for normalization.
- `Posting_Date` locates the item in time.
- `Plant_Code` is useful for organizational context and quality checks.

Additional columns such as `Supplier`, `Cost_Center`, `Currency`, and `Amount` are preserved as raw data but are not required for the core normalization path.

### UTILITY (`backend/sampledata/utility.csv`)
Key columns:
- `Meter_ID`
- `Billing_Start`
- `Billing_End`
- `Consumption`
- `Unit`

Why these columns?
- They capture energy use over a billing period.
- `Consumption` and `Unit` are the primary values needed for ESG tracking.
- The billing period is checked for validity and drift.

This source type is mapped to purchased energy reporting.

### TRAVEL (`backend/sampledata/travel.csv`)
Key columns:
- `Trip_ID`
- `Employee_ID`
- `Trip_Type`
- `Origin`
- `Destination`
- `Travel_Date`
- `Distance_km`
- `Cost`
- `Currency`

Why these columns?
- They capture business travel activities.
- `Distance_km` is the main quantity for travel-related emissions.
- `Trip_Type`, `Origin`, and `Destination` help validate whether the row is a flight, taxi, or hotel stay.

## Why these columns, not more?

The chosen columns are intentionally minimal:
- They support validation and normalization without requiring every detail in the source file.
- They make the core rules easier to reason about.
- Extra fields are still preserved in raw JSON when present.

## How these sources map to ESG categories

- `SAP` → Scope 1 / direct operational emissions.
- `UTILITY` → Scope 2 / purchased energy emissions.
- `TRAVEL` → Scope 3 / business travel emissions.

These mappings are explicit in the normalizer and are key to the project’s reporting flow.

## Practical source assumptions

- Dates may use multiple formats (`dd.MM.yyyy`, `dd/MM/yyyy`, ISO-like forms).
- Measurements may appear in mixed units (`L`, `GAL`, `kWh`, `MWh`, `GWh`).
- Travel rows can vary in structure, so validation focuses on required fields and obvious inconsistencies.

## Summary

The data source design is a pragmatic balance:
- enough structure to validate and normalize,
- enough flexibility to accept real-world CSV variations,
- and enough simplicity to keep the prototype maintainable.
