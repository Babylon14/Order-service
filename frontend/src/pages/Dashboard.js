// import React, { useEffect, useState } from 'react';
// import api from '../api/api'; // Импортируем настроенный экземпляр

// function Dashboard() {
//   const [userData, setUserData] = useState(null);

//   useEffect(() => {
//     // Используем 'api' для запроса
//     api.get('/api/v1/users/me/')
//       .then(response => {
//         setUserData(response.data);
//       })
//       .catch(error => {
//         console.error("Не удалось загрузить данные:", error);
//         // Тут можно перенаправить на страницу входа, если 401
//       });
//   }, []);

//   return (
//     <div>
//       {userData ? (
//         <h3>Добро пожаловать на Сервис Заказов, {userData.email || userData.username}!</h3>
//       ) : (
//         <p>Загрузка данных...</p>
//       )}
//     </div>
//   );
// }

// export default Dashboard;

import React, { useEffect, useState } from 'react';
import api from '../api/api';
// --- Импорт Sentry ---
import * as Sentry from '@sentry/react'; 

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
  
  // --- ФУНКЦИИ ТЕСТИРОВАНИЯ SENTRY ---

  // 1. Тестирование ошибки JavaScript (будет отправлено вручную)
  const triggerSentryError = () => {
    try {
      // Имитация ошибки: попытка деления на ноль или доступа к несуществующему свойству
      const x = null;
      console.log(x.someProperty); // <-- Эта строка вызовет TypeError
      
    } catch (e) {
      // Sentry.captureException отправляет ошибку в Sentry
      Sentry.captureException(e); 
      alert("Тестовая JS-ошибка отправлена в Sentry! Проверьте вашу панель.");
    }
  };

  // 2. Тестирование ошибки рендеринга React (будет поймано ErrorBoundary в index.js)
  const triggerReactError = () => {
      // throw new Error приводит к сбою компонента, ErrorBoundary его ловит
      throw new Error("Sentry: Тестовая ошибка рендеринга React!");
  };
  
  // ------------------------------------

  return (
    <div style={{ padding: '20px' }}>
      {userData ? (
        <h3>Добро пожаловать на Сервис Заказов, {userData.email || userData.username}!</h3>
      ) : (
        <p>Загрузка данных...</p>
      )}
      
      {/* --- БЛОК ТЕСТИРОВАНИЯ SENTRY --- */}
      <div style={{ marginTop: '30px', border: '1px solid #ccc', padding: '15px' }}>
        <h2>Тестирование Sentry (Front-end)</h2>
        
        {/* Кнопка 1: Тестирование ошибки JavaScript, отправляемой вручную */}
        <button 
          onClick={triggerSentryError} 
          style={{ padding: '10px', marginRight: '15px', backgroundColor: 'lightblue', cursor: 'pointer' }}
        >
          1. Вызвать JS-ошибку (ручная отправка)
        </button>

        {/* Кнопка 2: Тестирование ошибки, которая должна быть поймана Sentry ErrorBoundary */}
        <button 
          onClick={triggerReactError} 
          style={{ padding: '10px', backgroundColor: 'lightcoral', cursor: 'pointer' }}
        >
          2. Вызвать критическую ошибку React (Проверить Fallback UI)
        </button>
      </div>
      {/* ------------------------------------ */}

    </div>
  );
}

export default Dashboard;
