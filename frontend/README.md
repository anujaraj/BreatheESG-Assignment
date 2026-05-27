# ESG Dashboard

Minimal React dashboard for ESG data ingestion, audit, and normalization.

## Features

- **Upload CSV**: Ingest ESG data (SAP, Utility, Travel)
- **Review**: Approve/reject flagged records
- **Normalized Records**: View standardized metrics
- **Audit Logs**: Complete change history
- **Data Sources**: Track all ingested files

## Workflow

```
Upload CSV → Review Flagged → Approve → Inspect Normalized → Audit Trail
```

## Tech Stack

- React 18
- Vite
- Axios
- React Router v6
- Minimal CSS (no frameworks)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server (assumes Django backend on http://127.0.0.1:8000):
```bash
npm run dev
```

Dashboard will be available at `http://127.0.0.1:3000`

3. Build for production:
```bash
npm run build
```

## API Configuration

The dashboard proxies API requests to the Django backend:
- Edit `vite.config.js` to change the Django server URL
- Default: `http://127.0.0.1:8000`

## Pages

### Upload
- Select organization, source type, and CSV file
- CSV must include required columns for the source type
- Invalid schema returns detailed error messages

### Review
- Filter by approval status (pending, approved, rejected)
- Approve or reject flagged rows
- Locked approved records cannot be edited

### Normalized Records
- Browse standardized metrics (normalized amounts, units, scopes)
- Filter by approval status
- Shows lock status for audit protection

### Audit Logs
- Complete history of all changes
- Displays previous and new values
- Reverse chronological order

### Data Sources
- Track all uploaded files
- Shows ingestion status (UPLOADED, PARSING, PARSED, VALIDATED, NORMALIZED, FAILED)
- Organization and source type metadata

## Minimal CSS

- Clean, responsive design
- No external CSS framework (pure CSS Grid/Flexbox)
- Color-coded badges for status
- Consistent button and form styling

## Notes

- No authentication (set up auth in Django if needed)
- Assumes Django CORS is enabled for `/api` endpoints
- Review actions propagate to normalized records automatically
