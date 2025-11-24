import React, { useState, useEffect } from 'react'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import AlertFeed from './components/AlertFeed'
import './App.css'

function App() {
  const [selectedTransformer, setSelectedTransformer] = useState(null)
  const [realtimeData, setRealtimeData] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [alerts, setAlerts] = useState([])

  // Gerçek zamanlı veri çekme
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/realtime-data')
        const data = await response.json()
        setRealtimeData(data.data || [])
      } catch (error) {
        console.error('Veri çekme hatası:', error)
      }
    }

    // İlk yükleme
    fetchData()

    // Her 5 saniyede bir güncelle
    const interval = setInterval(fetchData, 5000)

    return () => clearInterval(interval)
  }, [])

  // İstatistikleri çekme
  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const response = await fetch('/api/statistics')
        const data = await response.json()
        setStatistics(data)
      } catch (error) {
        console.error('İstatistik çekme hatası:', error)
      }
    }

    fetchStatistics()
    const interval = setInterval(fetchStatistics, 10000)

    return () => clearInterval(interval)
  }, [])

  // Bildirimleri çekme
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch('/api/alerts')
        const data = await response.json()
        setAlerts(data.alerts || [])
      } catch (error) {
        console.error('Bildirim çekme hatası:', error)
      }
    }

    fetchAlerts()
    const interval = setInterval(fetchAlerts, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app">
      <Header statistics={statistics} />
      <div className="app-content">
        <div className="map-container">
          <MapView
            data={realtimeData}
            selectedTransformer={selectedTransformer}
            onTransformerSelect={setSelectedTransformer}
          />
        </div>
        <div className="sidebar-container">
          {selectedTransformer ? (
            <Sidebar
              transformerId={selectedTransformer}
              onClose={() => setSelectedTransformer(null)}
            />
          ) : (
            <AlertFeed alerts={alerts} />
          )}
        </div>
      </div>
    </div>
  )
}

export default App

