import axios from 'axios';

// Базовый URL вашего бэкенда Django/DRF
const BACKEND_BASE_URL = 'http://127.0.0.1:8000'; 

// 1. Создание экземпляра Axios
const api = axios.create({
  baseURL: BACKEND_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
// 2. Настройка Interceptor для автоматического добавления Access Token
api.interceptors.request.use(
  (config) => {
    // Получаем Access Token из LocalStorage
    const token = localStorage.getItem('accessToken');
    
    // Если токен есть, добавляем его в заголовок Authorization
    if (token) {
      // Формат JWT: Bearer <token_value>
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
// Экспортируем настроенный экземпляр, чтобы использовать его в других компонентах
export default api;

