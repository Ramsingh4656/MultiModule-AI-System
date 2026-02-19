import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Resume API
export const resumeAPI = {
  analyze: (formData) => api.post('/resume/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getHistory: () => api.get('/resume/history'),
  getDetail: (id) => api.get(`/resume/analysis/${id}`),
};

// Spam API
export const spamAPI = {
  check: (data) => api.post('/spam/check', data),
  getHistory: () => api.get('/spam/history'),
  getStats: () => api.get('/spam/stats'),
};

// Summary API
export const summaryAPI = {
  create: (data) => api.post('/summary/create', data),
  getHistory: () => api.get('/summary/history'),
  getDetail: (id) => api.get(`/summary/detail/${id}`),
};

// Chat API
export const chatAPI = {
  sendMessage: (data) => api.post('/chat/message', data),
  getSessions: () => api.get('/chat/sessions'),
  getHistory: (sessionId) => api.get(`/chat/history/${sessionId}`),
  deleteSession: (sessionId) => api.delete(`/chat/session/${sessionId}`),
  getModelInfo: () => api.get('/chat/model-info'),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getUsageByModule: () => api.get('/analytics/usage-by-module'),
  getMonthlyUsage: () => api.get('/analytics/monthly-usage'),
  getActivityTimeline: (days) => api.get(`/analytics/activity-timeline?days=${days}`),
};

export default api;
