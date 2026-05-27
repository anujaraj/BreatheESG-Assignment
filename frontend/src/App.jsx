import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { useState } from 'react'
import Upload from './pages/Upload'
import Review from './pages/Review'
import Normalized from './pages/Normalized'
import AuditLog from './pages/AuditLog'
import DataSources from './pages/DataSources'
import './App.css'

function App() {
  const [refreshKey, setRefreshKey] = useState(0)

  const triggerRefresh = () => setRefreshKey(k => k + 1)

  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">ESG Dashboard</div>
          <div className="nav-links">
            <Link to="/">Upload</Link>
            <Link to="/review">Review</Link>
            <Link to="/normalized">Normalized Data</Link>
            <Link to="/audit-logs">Audit Logs</Link>
            <Link to="/data-sources">Data Sources</Link>
          </div>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Upload onUpload={triggerRefresh} />} />
            <Route path="/review" element={<Review key={refreshKey} onAction={triggerRefresh} />} />
            <Route path="/normalized" element={<Normalized />} />
            <Route path="/audit-logs" element={<AuditLog />} />
            <Route path="/data-sources" element={<DataSources />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
