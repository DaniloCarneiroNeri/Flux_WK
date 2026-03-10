const API_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : window.location.origin;

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erro na requisição');
  }
  return response.json();
};

export const api = {
  get: (endpoint) => fetch(`${API_URL}${endpoint}`).then(handleResponse),
  post: (endpoint, data) => fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(handleResponse),
  put: (endpoint, data) => fetch(`${API_URL}${endpoint}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(handleResponse),
  patch: (endpoint, data) => fetch(`${API_URL}${endpoint}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(handleResponse),
  delete: (endpoint) => fetch(`${API_URL}${endpoint}`, {
    method: 'DELETE'
  }).then(handleResponse)
};