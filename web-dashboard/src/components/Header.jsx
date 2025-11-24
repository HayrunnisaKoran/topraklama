import React from 'react'
import './Header.css'

function Header({ statistics }) {
  return (
    <div className="header">
      <div className="header-left">
        <div className="logo">
          <div className="logo-icon">⚡</div>
          <span className="logo-text">Topraklama İzleme</span>
        </div>
      </div>
      <div className="header-center">
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Toplam Trafo</span>
            <span className="stat-value">{statistics?.total_transformers || 0}</span>
          </div>
          <div className="stat-item risk-high">
            <span className="stat-label">Yüksek Risk</span>
            <span className="stat-value">{statistics?.high_risk || 0}</span>
          </div>
          <div className="stat-item risk-medium">
            <span className="stat-label">Orta Risk</span>
            <span className="stat-value">{statistics?.medium_risk || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Tahmini Tasarruf</span>
            <span className="stat-value">{statistics?.estimated_savings?.toLocaleString('tr-TR') || 0} ₺</span>
          </div>
        </div>
      </div>
      <div className="header-right">
        <div className="notification-bell">🔔</div>
      </div>
    </div>
  )
}

export default Header

