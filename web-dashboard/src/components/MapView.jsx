import React, { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import './MapView.css'

// Marker iconları için custom iconlar
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  })
}

function MapView({ data, selectedTransformer, onTransformerSelect }) {
  const mapRef = useRef(null)

  // İzmir merkez koordinatları
  const center = [38.4237, 27.1428]

  const getMarkerColor = (riskScore, riskLevel, isAnomaly) => {
    // Veri yoksa gri göster
    if (riskLevel === 'unknown' || riskScore === 0 || riskScore === undefined) {
      return '#95a5a6' // Gri - Veri yok
    }
    // Arızalı trafolar için koyu kırmızı
    if (isAnomaly && riskScore >= 80) return '#6B0000' // Çok koyu kırmızı - Arızalı
    if (riskScore >= 70) return '#ff4757' // Kırmızı - Yüksek risk
    if (riskScore >= 40) return '#ffa502' // Turuncu - Orta risk
    return '#2ed573' // Yeşil - Düşük risk
  }

  useEffect(() => {
    if (mapRef.current && selectedTransformer) {
      const transformer = data.find(t => t.transformer_id === selectedTransformer)
      if (transformer) {
        mapRef.current.setView([transformer.latitude, transformer.longitude], 13)
      }
    }
  }, [selectedTransformer, data])

  return (
    <div className="map-view">
      <MapContainer
        center={center}
        zoom={11}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {data && data.length > 0 ? (
          data.map((transformer) => {
            const riskScore = transformer.risk_score || 0
            const riskLevel = transformer.risk_level || 'unknown'
            const isAnomaly = transformer.is_anomaly || false
            const color = getMarkerColor(riskScore, riskLevel, isAnomaly)
            const icon = createCustomIcon(color)
            
            return (
              <Marker
                key={transformer.transformer_id}
                position={[transformer.latitude, transformer.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => {
                    onTransformerSelect(transformer.transformer_id)
                  }
                }}
              >
                <Popup>
                  <div className="popup-content">
                    <h3>{transformer.name}</h3>
                    <p>Bölge: {transformer.region}</p>
                    {riskScore > 0 ? (
                      <>
                        <p>Risk Skoru: <strong>{riskScore.toFixed(1)}</strong></p>
                        <p>Durum: <span style={{ color }}>
                          {isAnomaly && riskScore >= 80 
                            ? 'ARIZALI' 
                            : riskLevel.toUpperCase()}
                        </span></p>
                      </>
                    ) : (
                      <p style={{ color: '#95a5a6' }}>Veri bekleniyor...</p>
                    )}
                  </div>
                </Popup>
              </Marker>
            )
          })
        ) : (
          <div style={{ 
            position: 'absolute', 
            top: '50%', 
            left: '50%', 
            transform: 'translate(-50%, -50%)',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '20px',
            borderRadius: '8px',
            zIndex: 1000
          }}>
            <p>Trafo verileri yükleniyor...</p>
            <p style={{ fontSize: '12px', marginTop: '10px' }}>
              Simülasyonu başlatın: python simulasyon.py
            </p>
          </div>
        )}
      </MapContainer>
    </div>
  )
}

export default MapView

