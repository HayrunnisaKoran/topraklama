import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Tüm trafoları getir
export const getTransformers = async () => {
  const response = await api.get('/transformers');
  return response.data;
};

// Trafo detayı
export const getTransformer = async (id) => {
  const response = await api.get(`/transformers/${id}`);
  return response.data;
};

// Trafo geçmişi
export const getTransformerHistory = async (id) => {
  const response = await api.get(`/transformers/${id}/history`);
  return response.data;
};

// Dashboard istatistikleri
export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

// Trafo izolasyonu
export const isolateTransformer = async (id, action = 'isolate') => {
  const response = await api.post(`/transformers/${id}/isolate`, { action });
  return response.data;
};

// Bildirimler
export const getAlerts = async () => {
  const response = await api.get('/alerts');
  return response.data;
};

// Sistem konfigürasyonu
export const getConfig = async () => {
  const response = await api.get('/config');
  return response.data;
};

export default api;

