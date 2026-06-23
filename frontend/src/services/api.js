import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(config => {
  try {
    const user = JSON.parse(localStorage.getItem('calmmind_user') || 'null');
    if (user && user.id) {
      config.headers['X-User-Id'] = String(user.id);
    }
  } catch (e) {
    console.error('Error loading user header:', e);
  }
  return config;
});

export const authAPI = {
  getProfile: () => api.get('/auth/profile').then(res => res.data),
  saveProfile: (data) => api.post('/auth/profile', data).then(res => res.data),
  deleteProfile: (userId) => api.delete(`/auth/profile/${userId}`).then(res => res.data),
  exportData: (userId) => api.get(`/auth/export/${userId}`).then(res => res.data),
};

export const chatAPI = {
  getConversations: () => api.get('/chat/conversations').then(res => res.data),
  createConversation: (title) => api.post('/chat/conversations', { title }).then(res => res.data),
  deleteConversation: (id) => api.delete(`/chat/conversations/${id}`).then(res => res.data),
  renameConversation: (id, title) => api.post(`/chat/conversations/${id}/rename`, { title }).then(res => res.data),
  pinConversation: (id) => api.post(`/chat/conversations/${id}/pin`).then(res => res.data),
  getMessages: (conversationId) => api.get(`/chat/messages?conversation_id=${conversationId}`).then(res => res.data),
  sendMessage: (conversationId, message) => api.post('/chat/message', { conversation_id: conversationId, message }).then(res => res.data),
};

export const moodAPI = {
  logMood: (data) => api.post('/mood/log', data).then(res => res.data),
  getMoodLogs: (days = 30) => api.get(`/mood/logs?days=${days}`).then(res => res.data),
  predictMood: (days = 30) => api.get(`/mood/predict?days=${days}`).then(res => res.data),
};

export const plansAPI = {
  getPlans: () => api.get('/plans').then(res => res.data),
  generatePlan: (planType) => api.post('/plans', { plan_type: planType }).then(res => res.data),
  generatePersonalizedPlan: (data) => api.post('/plans/generate_personalized', data).then(res => res.data),
  updatePlan: (id, tasks) => api.put(`/plans/${id}`, { tasks }).then(res => res.data),
  deletePlan: (id) => api.delete(`/plans/${id}`).then(res => res.data),
};

export const favoritesAPI = {
  getFavorites: () => api.get('/favorites').then(res => res.data),
  addFavorite: (type, content) => api.post('/favorites', { type, content }).then(res => res.data),
  deleteFavorite: (id) => api.delete(`/favorites/${id}`).then(res => res.data),
};

export const voiceAPI = {
  transcribeAudio: (formData) => api.post('/voice/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(res => res.data),
  textToSpeech: (text) => api.post('/voice/tts', { text }, { responseType: 'blob' }).then(res => res.data),
};

export default api;
