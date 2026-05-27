import { useState, useEffect } from 'react'
import { getNormalizedRecords } from '../api'

export default function Normalized() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchRecords()
  }, [filter])

  const fetchRecords = async () => {
    setLoading(true)
    try {
      const response = await getNormalizedRecords()
      let data = response.data.results || response.data
      if (filter !== 'all') {
        data = data.filter((r) => r.approval_status === filter)
      }
      setRecords(data)
    } catch (error) {
      setMessage('Error loading normalized records')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badgeClass = `badge badge-${status}`
    return <span className={badgeClass}>{status}</span>
  }

  const getLockBadge = (locked) => {
    const badgeClass = `badge ${locked === 'locked' ? 'badge-locked' : ''}`
    return <span className={badgeClass}>{locked}</span>
  }

  return (
    <div className="page">
      <h1>Normalized Records</h1>
      <p style={{ marginBottom: '1.5rem', color: '#7f8c8d' }}>
        View normalized ESG metrics converted to standard units and scopes.
      </p>

      <div className="form-group" style={{ marginBottom: '1.5rem' }}>
        <label>Filter by Approval Status</label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {message && <div className="alert alert-error">{message}</div>}

      {loading ? (
        <div className="loading">Loading normalized records...</div>
      ) : records.length === 0 ? (
        <div className="loading">No normalized records found</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Organization</th>
              <th>Scope</th>
              <th>Amount</th>
              <th>Unit</th>
              <th>Approval</th>
              <th>Lock Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td>{record.id}</td>
                <td>{record.organization_name || 'N/A'}</td>
                <td>{record.scope}</td>
                <td>{parseFloat(record.normalized_amount).toFixed(2)}</td>
                <td>{record.normalized_unit}</td>
                <td>{getStatusBadge(record.approval_status)}</td>
                <td>{getLockBadge(record.lock_status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
