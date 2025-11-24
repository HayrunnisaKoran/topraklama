import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './Sidebar.css'

function Sidebar({ transformerId, onClose }) {
  const [transformerData, setTransformerData] = useState(null)
  const [historicalData, setHistoricalData] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Trafo detaylarını çek
        const response = await fetch(`/api/transformer/${transformerId}`)
        const data = await response.json()
        setTransformerData(data)

        // Tarihsel veriyi çek
        const histResponse = await fetch(`/api/historical-data/${transformerId}?days=7`)
        const histData = await histResponse.json()
        
        // Grafik için formatla
        const formatted = histData.data.map(item => ({
          time: new Date(item.timestamp).toLocaleDateString('tr-TR'),
          direnç: item.toprak_direnci,
          kaçak_akım: item.kacak_akim
        }))
        setHistoricalData(formatted)
      } catch (error) {
        console.error('Veri çekme hatası:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000)

    return () => clearInterval(interval)
  }, [transformerId])

  if (!transformerData) {
    return (
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>Yükleniyor...</h2>
          <button onClick={onClose}>✕</button>
        </div>
      </div>
    )
  }

  const latest = transformerData.latest_data || {}
  const riskColor = latest.risk_color || '#8a8fa3'

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>{transformerData.name}</h2>
        <button onClick={onClose}>✕</button>
      </div>

      <div className="sidebar-content">
        <div className="info-section">
          <div className="info-item">
            <span className="info-label">Bölge</span>
            <span className="info-value">{transformerData.region}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Risk Skoru</span>
            <span className="info-value" style={{ color: riskColor }}>
              {latest.risk_score?.toFixed(1) || 'N/A'} / 100
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Durum</span>
            <span className="info-value" style={{ color: riskColor }}>
              {latest.risk_level?.toUpperCase() || 'UNKNOWN'}
            </span>
          </div>
        </div>

        <div className="sensor-section">
          <h3>Sensör Değerleri</h3>
          <div className="sensor-grid">
            <div className="sensor-item">
              <span className="sensor-label">Toprak Direnci</span>
              <span className="sensor-value">{latest.toprak_direnci?.toFixed(2) || 'N/A'} Ω</span>
            </div>
            <div className="sensor-item">
              <span className="sensor-label">Kaçak Akım</span>
              <span className="sensor-value">{latest.kacak_akim?.toFixed(2) || 'N/A'} mA</span>
            </div>
            <div className="sensor-item">
              <span className="sensor-label">Toprak Potansiyeli</span>
              <span className="sensor-value">{latest.toprak_potansiyel?.toFixed(2) || 'N/A'} V</span>
            </div>
            <div className="sensor-item">
              <span className="sensor-label">Toprak Nemi</span>
              <span className="sensor-value">{latest.toprak_nemi?.toFixed(1) || 'N/A'} %</span>
            </div>
            <div className="sensor-item">
              <span className="sensor-label">Sıcaklık</span>
              <span className="sensor-value">{latest.toprak_sicakligi?.toFixed(1) || 'N/A'} °C</span>
            </div>
            <div className="sensor-item">
              <span className="sensor-label">Korozyon</span>
              <span className="sensor-value">{latest.korozyon_seviyesi?.toFixed(1) || 'N/A'}</span>
            </div>
          </div>
        </div>

        {historicalData.length > 0 && (
          <div className="chart-section">
            <h3>Son 7 Gün - Trend Grafiği</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2f4a" />
                <XAxis dataKey="time" stroke="#8a8fa3" fontSize={10} />
                <YAxis stroke="#8a8fa3" fontSize={10} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1a1f3a', 
                    border: '1px solid #2a2f4a',
                    color: '#ffffff'
                  }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="direnç" 
                  stroke="#667eea" 
                  strokeWidth={2}
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="kaçak_akım" 
                  stroke="#ff4757" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  )
}

export default Sidebar

