import axios from 'axios'

// Für lokal: Backend auf http://localhost:8000
// In Hetzner kannst du das später auf deine Domain/IP ändern.
const api = axios.create({
  baseURL: 'http://localhost:8000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
