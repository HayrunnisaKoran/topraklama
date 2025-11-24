import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { getTransformers, getDashboardStats } from '../services/api';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Leaflet marker icon düzeltmesi
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

function Dashboard() {
  const [transformers, setTransformers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Her 5 saniyede bir güncelle
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [transformersData, statsData] = await Promise.all([
        getTransformers(),
        getDashboardStats(),
      ]);
      
      if (transformersData.success) {
        setTransformers(transformersData.transformers);
      }
      
      if (statsData.success) {
        setStats(statsData.stats);
      }
      
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'high':
        return '#ef4444'; // Kırmızı
      case 'medium':
        return '#f59e0b'; // Sarı
      case 'low':
        return '#10b981'; // Yeşil
      default:
        return '#6b7280'; // Gri
    }
  };

  const getMarkerColor = (riskLevel) => {
    return getRiskColor(riskLevel);
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Yükleniyor...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>Hata Oluştu</h2>
        <p>{error}</p>
        <button onClick={loadData}>Tekrar Dene</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Topraklama İzleme Sistemi</h1>
        <div className="header-stats">
          {stats && (
            <>
              <div className="stat-card">
                <span className="stat-label">Toplam Trafo</span>
                <span className="stat-value">{stats.total_transformers}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Anomali</span>
                <span className="stat-value warning">{stats.anomaly_count}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">İzole</span>
                <span className="stat-value danger">{stats.isolated_count}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Ortalama Risk</span>
                <span className="stat-value">{stats.average_risk.toFixed(1)}</span>
              </div>
            </>
          )}
        </div>
      </header>

      <div className="dashboard-content">
        <div className="dashboard-map">
          <h2>Trafo Lokasyonları</h2>
          {transformers.length > 0 && (
            <MapContainer
              center={[38.4237, 27.1428]}
              zoom={11}
              style={{ height: '600px', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              />
              {transformers.map((transformer) => (
                <Marker
                  key={transformer.id}
                  position={[transformer.latitude, transformer.longitude]}
                  icon={L.divIcon({
                    className: 'custom-marker',
                    html: `<div style="background-color: ${getMarkerColor(transformer.risk_level)}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
                    iconSize: [20, 20],
                  })}
                >
                  <Popup>
                    <div>
                      <h3>{transformer.name}</h3>
                      <p>Bölge: {transformer.region}</p>
                      <p>Risk: {transformer.risk_score} ({transformer.risk_level})</p>
                      <Link to={`/transformer/${transformer.id}`}>Detaylar</Link>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          )}
        </div>

        <div className="dashboard-list">
          <h2>Trafo Listesi</h2>
          <div className="transformer-list">
            {transformers.map((transformer) => (
              <Link
                key={transformer.id}
                to={`/transformer/${transformer.id}`}
                className="transformer-card"
              >
                <div className="transformer-header">
                  <h3>{transformer.name}</h3>
                  <span
                    className="risk-badge"
                    style={{ backgroundColor: getRiskColor(transformer.risk_level) }}
                  >
                    {transformer.risk_level.toUpperCase()}
                  </span>
                </div>
                <div className="transformer-info">
                  <p>Bölge: {transformer.region}</p>
                  <p>Risk Skoru: {transformer.risk_score}</p>
                  <p>
                    Durum:{' '}
                    {transformer.isolation_status ? (
                      <span className="status-active">Aktif</span>
                    ) : (
                      <span className="status-isolated">İzole</span>
                    )}
                  </p>
                  {transformer.is_anomaly && (
                    <p className="anomaly-warning">⚠️ Anomali Tespit Edildi</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

