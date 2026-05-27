# Architecture and Validation Decisions

This document explains the main design choices, validation rules, and testing strategy used in the project.

## Why these source types?

The application supports three source categories:
- `SAP` for procurement/fuel purchase data
- `UTILITY` for energy consumption data
- `TRAVEL` for business travel data

These were chosen because they map naturally to common ESG categories:
- SAP → likely Scope 1 / direct operational emissions
- Utility → Scope 2 purchased energy
- Travel → Scope 3 business travel

## Validation strategy

The validation rules are designed to catch bad or suspicious rows without rejecting everything prematurely.

### Common validation principles
- Required fields must be present.
- Dates should parse in the formats found in the sample data.
- Numeric values should be non-negative, except where negative values are explicitly meaningful.
- Units should be consistent with the expected type.
- If a row is structurally valid but suspicious, it is flagged rather than silently accepted.

### SAP validation choices
- Required columns: `Document_Number`, `Posting_Date`, `Plant_Code`, `Material_Description`, `Quantity`, `UOM`
- Quantity must be numeric and non-zero.
- Recognizes `L` and `GAL` as valid units.
- Warns on unknown plant codes and supplier values, because these often identify data quality issues without blocking ingestion.
- Supports both `dd.MM.yyyy` and `dd/MM/yyyy` date formats to match the sample files.

### Utility validation choices
- Required columns: `Meter_ID`, `Billing_Start`, `Billing_End`, `Consumption`, `Unit`
- Billing dates are validated and billing range order is checked.
- Consumption must be numeric and non-negative.
- Accepts `kWh`, `MWh`, and `GWh` because utility data can use differing energy units.
- Flags missing meter IDs or zero consumption as quality issues.

### Travel validation choices
- Required columns: `Trip_ID`, `Employee_ID`, `Trip_Type`, `Origin`, `Destination`, `Travel_Date`, `Distance_km`, `Cost`, `Currency`
- `Trip_Type` normalization allows empty or inconsistent class values.
- Flight rows require both origin and destination.
- Distance values are validated and must make sense for the selected trip type.
- Accepts multiple travel-related data shapes, including flights, hotels, and taxis.

## Normalization decisions

Normalization is intentionally lightweight:
- It converts raw numeric/temporal data into a standard form.
- It assigns a `scope` based on source type.
- It stores normalized amounts and units in standard units.
- It preserves the original raw row in JSON so details are not lost.

Why this matters:
- Standardized data is easier to display and compare in the UI.
- Scope assignment makes ESG reporting categories explicit.
- Storing the raw row provides a fallback if requirements change.

## Review and audit decisions

- Records can be flagged during ingestion, then reviewed manually.
- Approved records are `locked` to prevent accidental change.
- Audit logs store both previous and new values for every meaningful update.
- This creates a traceable workflow from file upload through review.

## Testing decisions

The project includes focused unit tests for:
- Validator logic for each source type.
- Normalizer behavior and scope assignment.

Why this testing focus?
- Validation logic is the most fragile part of an ingestion pipeline.
- Normalization determines the values that the UI and reporting pages show.
- These tests prove the core business rules without depending on full API wiring.

## Summary

The overall design favors:
- Clear separation of raw input and normalized output.
- A simple review workflow.
- Data quality checks that flag issues without discarding useful data.
- Minimal but meaningful test coverage around the most important rules.
