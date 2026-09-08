import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 12000,
});

export const getLeads = async (temperature = '', search = '') => {
  const params = {};
  if (temperature) params.temperature = temperature;
  if (search) params.search = search;
  const res = await api.get('/leads', { params });
  return res.data;
};

export const getLeadStats = async () => {
  const res = await api.get('/leads/stats');
  return res.data;
};

export const createLead = async (leadData) => {
  const res = await api.post('/leads', leadData);
  return res.data;
};

export const updateLead = async (id, updateData) => {
  const res = await api.put(`/leads/${id}`, updateData);
  return res.data;
};

export const deleteLead = async (id) => {
  const res = await api.delete(`/leads/${id}`);
  return res.data;
};

export const relayToN8n = async (payload) => {
  const res = await api.post('/n8n/relay', { initiate_call: true, ...payload });
  return res.data;
};

export const triggerOutboundCall = async (phoneNumber, assistantId = '') => {
  const res = await api.post('/vapi/call-phone', {
    phone_number: phoneNumber,
    assistant_id: assistantId,
  });
  return res.data;
};

export const simulateCall = async (data = {}) => {
  const res = await api.post('/leads/simulate-call', null, {
    params: data,
  });
  return res.data;
};

export default api;
