/**
 * Centralized API client for all backend requests
 * Uses axios with configured base URL
 */

import axios from 'axios'
import { API_BASE_URL } from '../config'

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Optional: Add request/response interceptors for error handling
apiClient.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

export default apiClient
