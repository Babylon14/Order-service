import os
import redis
import json
import logging


logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = None

try: 
    redis_client = redis.Redis( # Инициализируем Redis-клиента с явными параметрами
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=1,
        decode_responses=True, # Позволяет сразу получать данные как строки (str)
        socket_timeout=5,      # Таймаут соединения
    )
    # Проверяем подключение
    redis_client.ping()
    logger.info("Прямое подключение к Redis (redis-py) успешно!")
    IS_REDIS_CONNECTED = True
except Exception as err:
    logger.error(f"Критическая ошибка при подключении redis-py: {err}")
    redis_client = None
    IS_REDIS_CONNECTED = False


def set_cache(key, data, timeout=600):
    """Сохраняет данные (JSON-сериализует) в Redis."""
    if not IS_REDIS_CONNECTED:
        return None
    try:
        redis_client.execute_command('SELECT 1') # Проверяем подключение явно
        json_data = json.dumps(data) # Сериализуем данные Python в строку JSON
        redis_client.set(key, json_data, ex=timeout) # Устанавливаем ключ и время жизни
        return True
    except Exception as err:
        logger.error(f"Ошибка при сохранении данных в Redis: {err}")
        return False
    

def get_cache(key):
    """Получает данные из Redis (JSON-десериализует)."""
    if not IS_REDIS_CONNECTED:
        return None
    try:
        redis_client.execute_command('SELECT 1') # Проверяем БД перед чтением явно
        json_data = redis_client.get(key)
        if json_data:
            return json.loads(json_data) # Десериализуем строку JSON обратно в данные Python
        return None
    except Exception as err:
        logger.error(f"Ошибка при получении данных из Redis: {err}")
        return None
 

def clear_product_list_cache():
    """Удаляет все ключи кэша (продуктов) из базы данных №1."""
    if not IS_REDIS_CONNECTED:
        logger.error("Невозможно очистить кэш: Redis не подключен.")
        return 0
    try:
        # 1. Снова явно выбираем базу данных №1 (критически важно!)
        redis_client.execute_command('SELECT 1') 
        
        # 2. Ищем все ключи, которые начинаются с префикса вашего кэша
        # ВАЖНО: KEYS * может быть медленным на очень больших базах
        keys_to_delete = redis_client.keys("product_list:*") 
        
        if keys_to_delete:
            # 3. Удаляем найденные ключи
            deleted_count = redis_client.delete(*keys_to_delete)
            logger.info(f"Успешно удалено {deleted_count} ключей кэша продуктов.")
            return deleted_count
        
        logger.info("Не найдено ключей кэша для удаления.")
        return 0

    except Exception as err:
        logger.error(f"Ошибка при очистке кэша: {err}")
        return -1
    
