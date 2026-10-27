import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Interceptor to inject bearer token from localStorage if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('eh_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor for uniform error and 403 view-limit detection
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Check if anonymous browsing limit exceeded
    if (error.response && error.response.status === 403 && error.response.data?.detail?.view_limit_reached) {
      window.dispatchEvent(new CustomEvent('eh:view-limit-reached', {
        detail: error.response.data.detail
      }));
    }
    return Promise.reject(error);
  }
);

export const eventService = {
  getEvents: (params) => api.get('/v1/events', { params }),
  getEventDetail: (identifier) => api.get(`/v1/events/${identifier}`),
  reportEvent: (id, payload) => api.post(`/v1/events/${id}/report`, payload),
  verifyLink: (id) => api.post(`/v1/events/${id}/verify-link`),
  parseQuery: (q) => api.get('/v1/events/parse-query', { params: { q } }),
};

export const regionService = {
  getRegions: () => api.get('/v1/regions'),
  getRegionDetail: (slug) => api.get(`/v1/regions/${slug}`),
};

export const authService = {
  register: (payload) => api.post('/v1/auth/register', payload),
  login: (payload) => api.post('/v1/auth/login', payload),
  getMe: () => api.get('/v1/auth/me'),
  updatePreferences: (payload) => api.put('/v1/auth/preferences', payload),
  getSavedEvents: () => api.get('/v1/auth/saved-events'),
  saveEvent: (payload) => api.post('/v1/auth/saved-events', payload),
  unsaveEvent: (eventId) => api.delete(`/v1/auth/saved-events/${eventId}`),
};

export const assistantService = {
  query: (payload) => api.post('/v1/assistant/query', payload),
};

export const adminService = {
  getStats: () => api.get('/v1/admin/stats'),
  getSources: () => api.get('/v1/admin/sources'),
  createSource: (payload) => api.post('/v1/admin/sources', payload),
  updateSource: (id, payload) => api.put(`/v1/admin/sources/${id}`, payload),
  createEvent: (payload) => api.post('/v1/admin/events', payload),
  updateEvent: (id, payload) => api.put(`/v1/admin/events/${id}`, payload),
  deleteEvent: (id) => api.delete(`/v1/admin/events/${id}`),
  bulkDelete: (payload) => api.post('/v1/admin/bulk-delete', payload),
  runDiscovery: () => api.post('/v1/admin/discovery/run'),
  runSourceDiscovery: (slug) => api.post(`/v1/admin/discovery/sources/${slug}/run`),
  getAuditLogs: (limit = 50) => api.get('/v1/admin/audit-logs', { params: { limit } }),
};

export const systemService = {
  getHealth: () => api.get('/health'),
};

export default api;
