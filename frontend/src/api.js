import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const uploadCSV = (file, organizationName, sourceType, filename = null) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('organization_name', organizationName)
  formData.append('source_type', sourceType)
  if (filename) formData.append('filename', filename)
  
  return api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getDataSources = () => api.get('/data-sources/')

export const getDataSource = (id) => api.get(`/data-sources/${id}/`)

export const getRawRecords = (datasourceId) => api.get('/raw-records/', { params: { datasource: datasourceId } })

export const getNormalizedRecords = (rawRecordId = null) => {
  const params = rawRecordId ? { raw_record: rawRecordId } : {}
  return api.get('/normalized-records/', { params })
}

export const getReviews = (approvalStatus = null) => {
  const params = approvalStatus ? { approval_status: approvalStatus } : {}
  return api.get('/reviews/', { params })
}

export const approveReview = (reviewId) => api.post(`/reviews/${reviewId}/approve/`)

export const rejectReview = (reviewId) => api.post(`/reviews/${reviewId}/reject/`)

export const updateReview = (reviewId, data) => api.patch(`/reviews/${reviewId}/`, data)

export const getAuditLogs = () => api.get('/audit-logs/')

export default api
