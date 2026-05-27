import { useState, useEffect } from 'react'
import { getDataSources } from '../api'

export default function DataSources() {
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchSources()
  }, [])

  const fetchSources = async () => {
    setLoading(true)
    try {
      const response = await getDataSources()
      const data = response.data.results || response.data
      setSources(data)
    } catch (error) {
      setMessage('Error loading data sources')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badgeClass = `badge badge-${status}`
    return <span className={badgeClass}>{status}</span>
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString()
  }

  return (
    <div className="page">
      <h1>Data Sources</h1>
      <p style={{ marginBottom: '1.5rem', color: '#7f8c8d' }}>
        All uploaded ESG data files and their ingestion status.
      </p>

      {message && <div className="alert alert-error">{message}</div>}

      {loading ? (
        <div className="loading">Loading data sources...</div>
      ) : sources.length === 0 ? (
        <div className="loading">No data sources found</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Organization</th>
              <th>Source Type</th>
              <th>Filename</th>
              <th>Status</th>
              <th>Uploaded</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((source) => (
              <tr key={source.id}>
                <td>{source.id}</td>
                <td>{source.organization_name || 'N/A'} (ID: {source.organization})</td>
                <td style={{ fontWeight: 500 }}>{source.source_type}</td>
                <td style={{ fontSize: '0.9rem' }}>{source.filename}</td>
                <td>{getStatusBadge(source.ingestion_status)}</td>
                <td style={{ fontSize: '0.85rem' }}>
                  {formatDate(source.uploaded_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
