import React, { useEffect, useState } from 'react';
import api from '../api/api'; // Импортируем настроенный экземпляр

function Dashboard() {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    // Используем 'api' для запроса
    api.get('/api/v1/users/me/')
      .then(response => {
        setUserData(response.data);
      })
      .catch(error => {
        console.error("Не удалось загрузить данные:", error);
        // Тут можно перенаправить на страницу входа, если 401
      });
  }, []);

  return (
    <div>
      {userData ? (
        <h3>Добро пожаловать на Сервис Заказов, {userData.email || userData.username}!</h3>
      ) : (
        <p>Загрузка данных...</p>
      )}
    </div>
  );
}

export default Dashboard;

