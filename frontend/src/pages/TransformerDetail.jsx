import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getTransformer, getTransformerHistory, isolateTransformer } from '../services/api';

function TransformerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [transformer, setTransformer] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [id]);

  const loadData = async () => {
    try {
      const [transformerData, historyData] = await Promise.all([
        getTransformer(id),
        getTransformerHistory(id),
      ]);

      if (transformerData.success) {
        setTransformer(transformerData.transformer);
      }

      if (historyData.success) {
        setHistory(historyData.history);
      }

      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleIsolation = async (action) => {
    try {
      await isolateTransformer(id, action);
      loadData();
    } catch (err) {
      alert('İşlem başarısız: ' + err.message);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="detail-loading">
        <div className="loading-spinner"></div>
        <p>Yükleniyor...</p>
      </div>
    );
  }

  if (error || !transformer) {
    return (
      <div className="detail-error">
        <h2>Hata Oluştu</h2>
        <p>{error || 'Trafo bulunamadı'}</p>
        <button onClick={() => navigate('/')}>Ana Sayfaya Dön</button>
      </div>
    );
  }

  const chartData = history.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString('tr-TR'),
    risk: item.risk_score,
    direnc: item.toprak_direnci,
    kacak_akim: item.kacak_akim,
  }));

  return (
    <div className="transformer-detail">
      <div className="detail-header">
        <Link to="/" className="back-button">
          ← Geri
        </Link>
        <h1>{transformer.name}</h1>
        <div
          className="risk-indicator"
          style={{ backgroundColor: getRiskColor(transformer.risk_level) }}
        >
          Risk: {transformer.risk_score} ({transformer.risk_level.toUpperCase()})
        </div>
      </div>

      <div className="detail-content">
        <div className="detail-info">
          <div className="info-card">
            <h3>Genel Bilgiler</h3>
            <p><strong>Bölge:</strong> {transformer.region}</p>
            <p><strong>Koordinatlar:</strong> {transformer.latitude.toFixed(4)}, {transformer.longitude.toFixed(4)}</p>
            <p><strong>Durum:</strong> {transformer.isolation_status ? 'Aktif' : 'İzole'}</p>
            <p><strong>Anomali:</strong> {transformer.is_anomaly ? 'Evet' : 'Hayır'}</p>
            <p><strong>Son Güncelleme:</strong> {new Date(transformer.last_update).toLocaleString('tr-TR')}</p>
          </div>

          <div className="info-card">
            <h3>Sensör Verileri</h3>
            <div className="sensor-grid">
              <div className="sensor-item">
                <span className="sensor-label">Toprak Direnci</span>
                <span className="sensor-value">{transformer.sensor_data.toprak_direnci} Ohm</span>
              </div>
              <div className="sensor-item">
                <span className="sensor-label">Kaçak Akım</span>
                <span className="sensor-value">{transformer.sensor_data.kacak_akim} mA</span>
              </div>
              <div className="sensor-item">
                <span className="sensor-label">Toprak Potansiyeli</span>
                <span className="sensor-value">{transformer.sensor_data.toprak_potansiyel} V</span>
              </div>
              <div className="sensor-item">
                <span className="sensor-label">Toprak Nemi</span>
                <span className="sensor-value">{transformer.sensor_data.toprak_nemi} %</span>
              </div>
              <div className="sensor-item">
                <span className="sensor-label">Toprak Sıcaklığı</span>
                <span className="sensor-value">{transformer.sensor_data.toprak_sicakligi} °C</span>
              </div>
              <div className="sensor-item">
                <span className="sensor-label">Korozyon Seviyesi</span>
                <span className="sensor-value">{transformer.sensor_data.korozyon_seviyesi}</span>
              </div>
            </div>
          </div>

          <div className="info-card">
            <h3>İşlemler</h3>
            {transformer.isolation_status ? (
              <button
                className="btn-danger"
                onClick={() => handleIsolation('isolate')}
              >
                Trafoyu İzole Et
              </button>
            ) : (
              <button
                className="btn-success"
                onClick={() => handleIsolation('restore')}
              >
                İzolasyondan Çıkar
              </button>
            )}
          </div>
        </div>

        <div className="detail-charts">
          <div className="chart-card">
            <h3>Risk Skoru Geçmişi</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="risk" stroke="#ef4444" name="Risk Skoru" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Sensör Değerleri Geçmişi</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="direnc" stroke="#3b82f6" name="Toprak Direnci (Ohm)" />
                <Line type="monotone" dataKey="kacak_akim" stroke="#f59e0b" name="Kaçak Akım (mA)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TransformerDetail;

