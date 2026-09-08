import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8011/api/v1'
const TOKEN_STORAGE_KEY = 'aqpg_token'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

export const getToken = () => window.localStorage.getItem(TOKEN_STORAGE_KEY)

export const setToken = (token) => {
  if (token) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
  } else {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY)
  }
}

export const clearToken = () => {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY)
}

export const isAuthenticated = () => Boolean(getToken())

export const formatApiError = (error, fallback = 'An error occurred') => {
  const detail = error?.response?.data?.detail
  if (!detail) return error?.message || fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        if (typeof d === 'object' && d?.msg) {
          const field = d.loc ? d.loc.filter((x) => x !== 'body').join('.') : ''
          return field ? `${field}: ${d.msg}` : d.msg
        }
        return JSON.stringify(d)
      })
      .join(', ')
  }
  if (typeof detail === 'object') {
    return JSON.stringify(detail)
  }
  return String(detail)
}

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      clearToken()
      if (
        typeof window !== 'undefined' &&
        window.location.pathname !== '/login' &&
        window.location.pathname !== '/register' &&
        window.location.pathname !== '/'
      ) {
        window.location.href = '/login'
      }
    }
    // Automatically convert validation error objects to flat strings to prevent React rendering crashes
    if (error.response?.data?.detail) {
      error.response.data.detail = formatApiError(error)
    }
    return Promise.reject(error)
  },
)

export default api
