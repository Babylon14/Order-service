import React from 'react';

// Указываем базовый URL вашего бэкенда Django/DRF
// В продакшене это будет ваш публичный домен, например: 'https://api.orderservice.com'
const BACKEND_BASE_URL = 'http://127.0.0.1:8000'; 

function LoginPage() {
  
  // Функция, которая обрабатывает клик по кнопке
  const handleSocialLogin = (provider) => {
    // Определяем полный URL для перенаправления на Django-бэкенд
    // Это использует URL-маршруты social_django: /auth/login/<backend_name>/
    const loginUrl = `${BACKEND_BASE_URL}/auth/login/${provider}/`;
    
    // Ключевой шаг: Перенаправляем браузер пользователя на бэкенд.
    // Это инициирует весь процесс OAuth2.
    window.location.href = loginUrl;
  };

  return (
    <div className="login-container">
      <h2>Войти в Сервис Заказов</h2>
      
      {/* Кнопка Google */}
      <button 
        onClick={() => handleSocialLogin('google-oauth2')}
        className="google-btn"
      >
        Войти через Google
      </button>

      {/* Кнопка GitHub */}
      <button 
        onClick={() => handleSocialLogin('github')}
        className="github-btn"
      >
        Войти через GitHub
      </button>
    </div>
  );
}

export default LoginPage;

