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

  const getMarkerColor = (riskScore, riskLevel) => {
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
        {data.map((transformer) => {
          const color = getMarkerColor(transformer.risk_score, transformer.risk_level)
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
                  <p>Risk Skoru: <strong>{transformer.risk_score.toFixed(1)}</strong></p>
                  <p>Durum: <span style={{ color }}>{transformer.risk_level.toUpperCase()}</span></p>
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}

export default MapView

