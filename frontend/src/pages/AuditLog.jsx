import { useState, useEffect } from 'react'
import { getAuditLogs } from '../api'

export default function AuditLog() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await getAuditLogs()
      const data = response.data.results || response.data
      setLogs(Array.isArray(data) ? data.reverse() : [])
    } catch (error) {
      setMessage('Error loading audit logs')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleString()
  }

  const formatValues = (values) => {
    if (!values || Object.keys(values).length === 0) {
      return <span style={{ color: '#aaa', fontStyle: 'italic' }}>—</span>
    }
    return (
      <div style={{ fontSize: '0.85rem' }}>
        {Object.entries(values).map(([key, value], idx) => (
          <div key={idx} style={{ marginBottom: '0.3rem' }}>
            <strong>{key}:</strong> {String(value)}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="page">
      <h1>Audit Logs</h1>
      <p style={{ marginBottom: '1.5rem', color: '#7f8c8d' }}>
        Complete audit trail of all ESG data changes and approvals.
      </p>

      {message && <div className="alert alert-error">{message}</div>}

      {loading ? (
        <div className="loading">Loading audit logs...</div>
      ) : logs.length === 0 ? (
        <div className="loading">No audit logs found</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Record ID</th>
              <th>Action</th>
              <th>Previous Values</th>
              <th>New Values</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, idx) => (
              <tr key={log.id || idx}>
                <td style={{ fontSize: '0.85rem' }}>
                  {formatDate(log.timestamp || log.created_at)}
                </td>
                <td>{log.record}</td>
                <td style={{ fontWeight: 500 }}>{log.action}</td>
                <td style={{ color: '#7f8c8d', padding: '0.75rem' }}>
                  {formatValues(log.previous_values)}
                </td>
                <td style={{ color: '#27ae60', padding: '0.75rem' }}>
                  {formatValues(log.new_values)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
