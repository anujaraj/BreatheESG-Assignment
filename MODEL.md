# Model Overview

This project is built around a simple but structured data pipeline for ESG ingestion, review, normalization, and auditing.

## Core Entities

### Organization
- Represents a business or company.
- Stored as a single record per unique `company_name`.
- Used as the top-level grouping for all uploaded ESG data.

### DataSource
- Tracks each CSV file upload.
- Contains:
  - `organization`
  - `source_type` (`SAP`, `UTILITY`, `TRAVEL`)
  - `filename`
  - `ingestion_status` (`UPLOADED`, `PARSING`, `PARSED`, `VALIDATED`, `NORMALIZED`, `FAILED`)
- Why it exists:
  - Separates file ingestion from row-level data.
  - Makes it easy to show upload status and identify failed loads.
  - Preserves the origin of every row.

### RawRecord
- Stores the original row data as JSON.
- Connected to a `DataSource`.
- Why it exists:
  - Keeps raw source data intact.
  - Supports auditing and future reprocessing if validation rules change.

### NormalizedRecord
- Stores standardized values derived from raw rows.
- Contains:
  - `scope` (`Scope 1`, `Scope 2`, `Scope 3`)
  - `normalized_amount`
  - `normalized_unit`
  - `approval_status` (`pending`, `approved`, `rejected`)
  - `lock_status` (`unlocked`, `locked`)
- Why it exists:
  - Centralizes reporting-friendly values.
  - Separates normalization from raw input.
  - Supports locking after approval.

### Review
- Stores review status and comments for flagged normalized records.
- Contains:
  - `flag_reason`
  - `comments`
  - `approved`
  - `approval_status`
- Why it exists:
  - Keeps the audit and review process distinct from normalized data.
  - Allows a record to be flagged, reviewed, and then locked.

### AuditLog
- Records every important change to normalized records.
- Stores:
  - `action`
  - `previous_values`
  - `new_values`
  - `timestamp`
- Why it exists:
  - Provides a history of approvals, rejections, and normalization steps.
  - Supports traceability and compliance.

## Relationship Summary

- `Organization` → has many `DataSource`
- `DataSource` → has many `RawRecord`
- `RawRecord` → has one or more `NormalizedRecord`
- `NormalizedRecord` → has many `Review`
- `NormalizedRecord` → has many `AuditLog`

## Why this design?

- The model is intentionally layered.
- Raw data and normalized values are stored separately so the original source is never lost.
- DataSource records make pipeline state visible and diagnose failures.
- Review and audit are separate, which keeps business workflow clear.
- Approval locks save a snapshot of the final audited value.
