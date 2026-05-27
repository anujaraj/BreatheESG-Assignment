# Tradeoffs and Remaining Scope

This file explains the tradeoffs made during the project and the work that remains.

## Key tradeoffs

### 1. Simplicity over completeness
- The app supports only three source types (`SAP`, `UTILITY`, `TRAVEL`).
- This is enough for a focused prototype, but it is not a generic ingestion engine.
- Tradeoff: easier implementation and clearer UX, at the cost of less flexibility for new CSV schemas.

### 2. Raw storage + normalized summary
- Raw rows are preserved in JSON, while normalized rows store a standardized value.
- This gives auditability but duplicates some data.
- Tradeoff: more storage and model complexity, but stronger traceability.

### 3. Minimal frontend behavior
- The UI focuses on upload, review, normalized display, audit log, and data source listing.
- It does not provide advanced filtering, search, bulk edit, or user roles.
- Tradeoff: faster delivery and lower frontend complexity, at the cost of a richer user experience.

### 4. No authentication or authorization
- There is no user login, roles, or access control.
- Tradeoff: easier to build and test, but not secure enough for production use.

### 5. SQLite for persistence
- The backend uses SQLite for simplicity. For persistent cloud deployments, PostgreSQL would be the proper production choice.
- Tradeoff: fine for development and small demos, but not ideal for production scaling or concurrency.

### 6. Limited API testing
- The project includes backend unit tests for validation and normalization.
- It does not include full API endpoint tests or frontend integration tests.
- Tradeoff: core logic is covered, but the surface area of the system is not fully verified.

## What was left unfinished

### Functional gaps
- No user authentication or permission model.
- No bulk approve/reject workflow for many records at once.
- No deduplication of uploaded rows or duplicate file detection.
- No retry / error recovery for failed ingestion tasks.
- No file history view beyond the current source status.

### UX and reporting gaps
- No advanced filtering, search, or pagination in table views.
- No dashboards or aggregated ESG metrics.
- No export/download capability for normalized or reviewed data.

### Data quality and processing gaps
- No dynamic schema mapping or automatic column matching.
- No support for additional ESG source types beyond the three implemented.
- No configurable validation rules or thresholds.
- No timezone-aware date handling.

### Technical gaps
- No production-ready deployment scripts or containerization.
- No logging beyond basic audit record creation.
- No performance optimization for large CSV files.

## What we left as tradeoffs

- The system accepts a limited set of structured CSV shapes rather than arbitrary spreadsheets.
- Validation is explicit and rule-based rather than fully adaptive.
- Review logic is simple and record-level rather than workflow-driven.
- The frontend is intentionally lightweight and not a full operations dashboard.

## Good starting points for the next phase

- Add API tests for upload, review, and audit endpoints.
- Add React UI filtering and pagination.
- Add authentication and permission checks.
- Support more source types and dynamic schema discovery.
- Add a deployment plan using Docker or a cloud service.
