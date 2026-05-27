import { useState, useEffect } from 'react'
import { getReviews, approveReview, rejectReview, updateReview } from '../api'

export default function Review({ onAction }) {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('pending')
  const [message, setMessage] = useState('')
  const [actionInProgress, setActionInProgress] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [editingComments, setEditingComments] = useState({})

  useEffect(() => {
    fetchReviews()
  }, [filter])

  const fetchReviews = async () => {
    setLoading(true)
    try {
      const response = await getReviews(filter === 'all' ? null : filter)
      setReviews(response.data.results || response.data)
    } catch (error) {
      setMessage('Error loading reviews')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (reviewId) => {
    setActionInProgress(reviewId)
    try {
      await approveReview(reviewId)
      setMessage('✓ Review approved')
      fetchReviews()
      onAction()
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setActionInProgress(null)
    }
  }

  const handleReject = async (reviewId) => {
    setActionInProgress(reviewId)
    try {
      await rejectReview(reviewId)
      setMessage('✓ Review rejected')
      fetchReviews()
      onAction()
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setActionInProgress(null)
    }
  }

  const handleSaveComments = async (reviewId, comments) => {
    try {
      await updateReview(reviewId, { comments })
      setMessage('✓ Comments saved')
      setEditingComments({ ...editingComments, [reviewId]: false })
      fetchReviews()
    } catch (error) {
      setMessage(`Error: ${error.message}`)
    }
  }

  const getStatusBadge = (status) => {
    const badgeClass = `badge badge-${status}`
    return <span className={badgeClass}>{status}</span>
  }

  return (
    <div className="page">
      <h1>Review Flagged Records</h1>
      <p style={{ marginBottom: '1.5rem', color: '#7f8c8d' }}>
        Review and approve/reject flagged ESG records during the audit workflow.
      </p>

      <div className="form-group" style={{ marginBottom: '1.5rem' }}>
        <label>Filter by Status</label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="all">All</option>
        </select>
      </div>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
          {message}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading reviews...</div>
      ) : reviews.length === 0 ? (
        <div className="loading">No reviews found</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Review ID</th>
                <th>Organization</th>
                <th>Filename</th>
                <th>Flag Reason</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.id} style={{ cursor: 'pointer' }}>
                  <td>{review.id}</td>
                  <td onClick={() => setExpandedId(expandedId === review.id ? null : review.id)}>
                    {review.organization_name || 'N/A'}
                  </td>
                  <td onClick={() => setExpandedId(expandedId === review.id ? null : review.id)}>
                    {review.filename || 'N/A'}
                  </td>
                  <td style={{ fontSize: '0.9rem' }} onClick={() => setExpandedId(expandedId === review.id ? null : review.id)}>
                    {review.flag_reason}
                  </td>
                  <td>{getStatusBadge(review.approval_status)}</td>
                  <td>
                    {review.approval_status === 'pending' ? (
                      <div className="row" style={{ gap: '0.5rem' }}>
                        <button
                          className="success"
                          onClick={() => handleApprove(review.id)}
                          disabled={actionInProgress === review.id}
                          style={{ flex: 'none', padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                        >
                          Approve
                        </button>
                        <button
                          className="danger"
                          onClick={() => handleReject(review.id)}
                          disabled={actionInProgress === review.id}
                          style={{ flex: 'none', padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                        >
                          Reject
                        </button>
                      </div>
                    ) : (
                      <span style={{ color: '#7f8c8d', fontSize: '0.9rem' }}>
                        {review.approval_status === 'approved' ? 'Locked' : 'Final'}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Expanded Details for Comments */}
      {expandedId && reviews.find(r => r.id === expandedId) && (
        <div style={{
          marginTop: '2rem',
          padding: '1.5rem',
          border: '1px solid #ddd',
          borderRadius: '4px',
          backgroundColor: '#f9f9f9'
        }}>
          {(() => {
            const review = reviews.find(r => r.id === expandedId)
            return (
              <>
                <h3>Review Details - ID {review.id}</h3>
                <div style={{ marginTop: '1rem', lineHeight: '1.8' }}>
                  <p><strong>Organization:</strong> {review.organization_name || 'N/A'}</p>
                  <p><strong>Record ID:</strong> {review.record}</p>
                  <p><strong>Flag Reason:</strong> {review.flag_reason}</p>
                  <p><strong>Status:</strong> {getStatusBadge(review.approval_status)}</p>
                  <p><strong>Reviewed At:</strong> {new Date(review.reviewed_at).toLocaleString()}</p>
                </div>

                <div style={{ marginTop: '1.5rem' }}>
                  <label style={{ fontWeight: 'bold', marginBottom: '0.5rem', display: 'block' }}>
                    Comments
                  </label>
                  {editingComments[review.id] !== undefined && editingComments[review.id] !== false ? (
                    <div>
                      <textarea
                        value={editingComments[review.id]}
                        onChange={(e) => setEditingComments({ ...editingComments, [review.id]: e.target.value })}
                        placeholder="Add or edit comments..."
                        style={{
                          width: '100%',
                          minHeight: '100px',
                          padding: '0.75rem',
                          borderRadius: '4px',
                          border: '1px solid #ddd',
                          fontFamily: 'inherit',
                          fontSize: '0.95rem',
                          marginBottom: '0.5rem'
                        }}
                      />
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          className="success"
                          onClick={() => handleSaveComments(review.id, editingComments[review.id])}
                          style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingComments({ ...editingComments, [review.id]: false })}
                          style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div style={{
                        padding: '0.75rem',
                        backgroundColor: 'white',
                        border: '1px solid #eee',
                        borderRadius: '4px',
                        minHeight: '60px',
                        marginBottom: '0.5rem'
                      }}>
                        {review.comments || <span style={{ color: '#aaa', fontStyle: 'italic' }}>No comments yet</span>}
                      </div>
                      {review.approval_status === 'pending' && (
                        <button
                          onClick={() => setEditingComments({ ...editingComments, [review.id]: review.comments || '' })}
                          style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                        >
                          Edit Comments
                        </button>
                      )}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => setExpandedId(null)}
                  style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}
                >
                  Close
                </button>
              </>
            )
          })()}
        </div>
      )}
    </div>
  )
}
