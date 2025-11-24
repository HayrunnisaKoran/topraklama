import React from 'react'
import './AlertFeed.css'

function AlertFeed({ alerts }) {
  return (
    <div className="alert-feed">
      <div className="alert-feed-header">
        <h2>🔔 Canlı Bildirimler</h2>
        <span className="alert-count">{alerts.length}</span>
      </div>
      <div className="alert-list">
        {alerts.length === 0 ? (
          <div className="no-alerts">
            <p>Henüz bildirim yok</p>
            <span>Simülasyon çalıştığında bildirimler burada görünecek</span>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <div key={index} className={`alert-item ${alert.severity}`}>
              <div className="alert-icon">
                {alert.severity === 'high' ? '🔴' : '🟡'}
              </div>
              <div className="alert-content">
                <div className="alert-message">{alert.message}</div>
                <div className="alert-time">
                  {new Date(alert.timestamp).toLocaleTimeString('tr-TR')}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AlertFeed

