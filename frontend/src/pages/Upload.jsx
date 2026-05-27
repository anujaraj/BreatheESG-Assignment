import { useState } from 'react'
import { uploadCSV } from '../api'

export default function Upload({ onUpload }) {
  const [file, setFile] = useState(null)
  const [orgName, setOrgName] = useState('')
  const [sourceType, setSourceType] = useState('SAP')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file || !orgName) {
      setMessage('Please select a file and enter organization name')
      return
    }

    setLoading(true)
    setMessage('')
    setResult(null)

    try {
      const response = await uploadCSV(file, orgName, sourceType, file.name)
      setResult(response.data)
      setMessage('✓ Upload successful')
      setFile(null)
      setOrgName('')
      onUpload()
    } catch (error) {
      const errorData = error.response?.data || {}
      if (errorData.missing_columns) {
        setMessage(`Error: Missing columns: ${errorData.missing_columns.join(', ')}`)
      } else {
        setMessage(`Error: ${errorData.detail || error.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Upload CSV</h1>
      <p style={{ marginBottom: '1.5rem', color: '#7f8c8d' }}>
        Upload ESG data files (SAP, Utility, or Travel) for ingestion and normalization.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Organization Name</label>
          <input
            type="text"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            placeholder="e.g., XYZ Corp"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Source Type</label>
          <select value={sourceType} onChange={(e) => setSourceType(e.target.value)} disabled={loading}>
            <option value="SAP">SAP</option>
            <option value="UTILITY">Utility</option>
            <option value="TRAVEL">Travel</option>
          </select>
        </div>

        <div className="form-group">
          <label>CSV File</label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            disabled={loading}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </form>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`} style={{ marginTop: '1rem' }}>
          {message}
        </div>
      )}

      {result && (
        <div className="alert alert-info" style={{ marginTop: '1rem' }}>
          <strong>Upload Summary:</strong>
          <div style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
            <p>Rows parsed: {result.rows_parsed}</p>
            <p>Data source ID: {result.datasource_id}</p>
            <p>Status: {result.ingestion_status}</p>
            {result.validation?.flagged && (
              <p>Flagged rows: {result.validation.reasons.length}</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
