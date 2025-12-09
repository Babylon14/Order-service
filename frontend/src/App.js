import React from 'react';
// Важно: Меняем BrowserRouter на Router
import { Router, Routes, Route } from 'react-router-dom'; 
import LoginPage from './pages/LoginPage'; 
import SocialLoginSuccess from './pages/socialLoginSuccess.js'; 
import Dashboard from './pages/Dashboard';

// Функция App теперь принимает пропс 'history'
// и использует его для компонента Router
function App({ history }) { 
  return (
    // Используем компонент Router (импортированный из react-router-dom)
    // и передаем ему history, полученный из index.js
    <Router navigator={history} location={history.location}> 
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/social-login-success" element={<SocialLoginSuccess />} /> 
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

