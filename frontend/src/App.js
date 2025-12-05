import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage'; // Импортируем созданный компонент
import SocialLoginSuccess from './pages/socialLoginSuccess.js'; // Компонент для обработки токенов (из прошлого шага)
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        {/* URL для обработки токенов, должен совпадать с SOCIAL_AUTH_LOGIN_REDIRECT_URL */}
        <Route path="/social-login-success" element={<SocialLoginSuccess />} /> 
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

