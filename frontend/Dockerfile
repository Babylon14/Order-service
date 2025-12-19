# 1. Используем фиксированную версию Node и правильный регистр (исправляет Warning)
FROM node:20-alpine AS build

WORKDIR /app

# 2. Копируем конфиги npm
COPY package*.json ./

# 3. Устанавливаем зависимости. 
# --legacy-peer-deps спасает от 90% ошибок конфликтов версий в React/Vue
RUN npm install --legacy-peer-deps

# 4. Копируем остальное и собираем
COPY . .
RUN npm run build

# 5. Финальный этап: Nginx
FROM nginx:stable-alpine
# Копируем конфиг, который мы создали ранее
COPY nginx.conf /etc/nginx/nginx.conf
# Копируем билд фронтенда из предыдущего этапа
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

