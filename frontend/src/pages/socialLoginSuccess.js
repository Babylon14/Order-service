import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom'; // Для React Router

function SocialLoginSuccess() {
  const location = useLocation(); // Объект, содержащий информацию о текущем URL
  const navigate = useNavigate(); // Функция для программного перехода

  useEffect(() => {
    // 1. Извлечение токенов из URL-параметров (query string)
    const params = new URLSearchParams(location.search);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (accessToken && refreshToken) {
      // 2. СОХРАНЕНИЕ ТОКЕНОВ
      // **Это самый важный шаг.** Храним токены для дальнейших запросов.
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      
      // 3. Удаление токенов из URL (опционально, но рекомендуется)
      navigate('/', { replace: true }); // Переход на главную страницу, очищая URL
      
      console.log("Успешный вход! Токены сохранены.");
    } else {
      // Обработка ошибки (токены не найдены)
      console.error("Не удалось получить токены.");
      navigate('/login');
    }
  }, [location.search, navigate]);
  return <div>Загрузка... Устанавливаю сессию.</div>;
}
export default SocialLoginSuccess;