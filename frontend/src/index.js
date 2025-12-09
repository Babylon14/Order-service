import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// --- ИМПОРТЫ ДЛЯ SENTRY И РОУТИНГА ---
import { createBrowserHistory } from 'history'; 
import * as Sentry from '@sentry/react';
// Импорт интеграции для роутера из установленного пакета
import { reactRouterTracingIntegration } from "@sentry/react-router"; 
// ------------------------------------

// Создаем объект истории браузера. Это обязательно, так как Sentry будет 
// использовать его для отслеживания смены маршрутов.
const history = createBrowserHistory(); 

// --- 1. ИНИЦИАЛИЗАЦИЯ SENTRY ---
// Получаем DSN из переменной окружения
const SENTRY_DSN_FRONTEND = process.env.REACT_APP_SENTRY_DSN_FRONTEND; 

if (SENTRY_DSN_FRONTEND) {
    Sentry.init({
        dsn: SENTRY_DSN_FRONTEND,
        // Перечисляем все интеграции (включая трассировку роутера)
        integrations: [
            // 1. Интеграция для трассировки React Router
            reactRouterTracingIntegration(history),
            
            // 2. Стандартная интеграция для трассировки браузера и ошибок (APM)
            Sentry.browserTracingIntegration(), 
        ],
        
        tracesSampleRate: 1.0, // Степень трассировки (1.0 = 100% данных)
        environment: process.env.NODE_ENV || 'development', 
    });
    console.log("Sentry успешно инициализирован для фронтенда.");
}

const root = ReactDOM.createRoot(document.getElementById('root'));

// --- 2. ОБЕРТЫВАНИЕ В ErrorBoundary ---
// Определяем компонент, который мы будем рендерить: App, обернутый Sentry, или просто App.
const RootComponent = SENTRY_DSN_FRONTEND 
    ? Sentry.withErrorBoundary(App, { 
        // Fallback UI (показывается пользователю при критической ошибке)
        fallback: <h1>⚠️ Произошла критическая ошибка.</h1> 
      }) 
    : App;

root.render(
  <React.StrictMode>
    {/* 3. РЕНДЕРИНГ: Передаем объект history в компонент App */}
    <RootComponent history={history} />
  </React.StrictMode>
);

reportWebVitals();