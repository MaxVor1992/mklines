"""
Модуль кэширования результатов парсинга
Кеш хранится 12 часов и сохраняется в файлах
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from logging import info, error

# Директория для кэша
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(_MODULE_DIR, 'cache')
CACHE_TTL = 12 * 3600  # 12 часов в секундах

# Создаём директорию для кэша
os.makedirs(CACHE_DIR, exist_ok=True)


def _generate_cache_key(search_queries, engine, region, depth, device='desktop'):
    """
    Генерирует уникальный ключ кэша на основе параметров запроса

    Args:
        search_queries: список поисковых запросов
        engine: поисковая система (11, 12, 13, 21, 22)
        region: регион
        depth: глубина поиска
        device: устройство (desktop, tablet, mobile)

    Returns:
        str: хэш-ключ кэша
    """
    # Создаём строку из всех параметров
    key_string = "|".join([
        ",".join(sorted(search_queries)),  # Сортируем для консистентности
        str(engine),
        str(region),
        str(depth),
        str(device)
    ])

    # Генерируем MD5 хэш
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()


def _get_cache_file(cache_key, user_id='anon'):
    """
    Возвращает путь к файлу кэша
    
    Args:
        cache_key: ключ кэша
        user_id: ID пользователя
    
    Returns:
        str: путь к файлу кэша
    """
    return os.path.join(CACHE_DIR, f"cache_{user_id}_{cache_key}.json")


def check_cache(search_queries, engine, region, depth, device='desktop', user_id='anon'):
    """
    Проверяет наличие валидного кэша

    Args:
        search_queries: список поисковых запросов
        engine: поисковая система
        region: регион
        depth: глубина поиска
        device: устройство (desktop, tablet, mobile)
        user_id: ID пользователя

    Returns:
        dict или None: результаты из кэша или None
    """
    try:
        cache_key = _generate_cache_key(search_queries, engine, region, depth, device)
        cache_file = _get_cache_file(cache_key, user_id)
        
        # Проверяем существование файла
        if not os.path.exists(cache_file):
            info(f"Cache miss: no cache file for key {cache_key[:8]}...")
            return None
        
        # Загружаем данные кэша
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Проверяем время жизни кэша
        cache_time = cache_data.get('timestamp', 0)
        current_time = time.time()
        
        if current_time - cache_time > CACHE_TTL:
            # Кеш устарел, удаляем
            info(f"Cache expired: {cache_key[:8]}... (age: {(current_time - cache_time) / 3600:.1f}h)")
            try:
                os.remove(cache_file)
            except Exception as e:
                error(f"Failed to remove expired cache: {e}")
            return None
        
        # Кеш валиден
        age_hours = (current_time - cache_time) / 3600
        info(f"Cache hit: {cache_key[:8]}... (age: {age_hours:.1f}h)")
        return cache_data.get('result')
        
    except Exception as e:
        error(f"Cache check error: {e}")
        return None


def save_to_cache(search_queries, engine, region, depth, result, device='desktop', user_id='anon'):
    """
    Сохраняет результат парсинга в кэш

    Args:
        search_queries: список поисковых запросов
        engine: поисковая система
        region: регион
        depth: глубина поиска
        result: результат парсинга (dict)
        device: устройство (desktop, tablet, mobile)
        user_id: ID пользователя
    """
    try:
        cache_key = _generate_cache_key(search_queries, engine, region, depth, device)
        cache_file = _get_cache_file(cache_key, user_id)
        
        # Формируем данные для кэша
        cache_data = {
            'timestamp': time.time(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'params': {
                'queries': search_queries,
                'engine': engine,
                'region': region,
                'depth': depth
            },
            'result': result
        }
        
        # Сохраняем в файл
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        info(f"Cache saved: {cache_key[:8]}... ({len(search_queries)} queries)")
        
    except Exception as e:
        error(f"Cache save error: {e}")


def clear_user_cache(user_id='anon'):
    """
    Очищает весь кеш пользователя
    
    Args:
        user_id: ID пользователя
    """
    try:
        count = 0
        for filename in os.listdir(CACHE_DIR):
            if filename.startswith(f"cache_{user_id}_"):
                filepath = os.path.join(CACHE_DIR, filename)
                os.remove(filepath)
                count += 1
        
        info(f"Cache cleared for user {user_id}: {count} files removed")
        return count
        
    except Exception as e:
        error(f"Cache clear error: {e}")
        return 0


def get_cache_stats(user_id='anon'):
    """
    Возвращает статистику кэша для пользователя
    
    Args:
        user_id: ID пользователя
    
    Returns:
        dict: статистика кэша
    """
    try:
        total_files = 0
        total_size = 0
        valid_files = 0
        expired_files = 0
        current_time = time.time()
        
        for filename in os.listdir(CACHE_DIR):
            if not filename.startswith(f"cache_{user_id}_"):
                continue
            
            filepath = os.path.join(CACHE_DIR, filename)
            total_files += 1
            total_size += os.path.getsize(filepath)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cache_time = cache_data.get('timestamp', 0)
                if current_time - cache_time <= CACHE_TTL:
                    valid_files += 1
                else:
                    expired_files += 1
            except:
                expired_files += 1
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'expired_files': expired_files,
            'total_size_kb': round(total_size / 1024, 2)
        }
        
    except Exception as e:
        error(f"Cache stats error: {e}")
        return {'total_files': 0, 'valid_files': 0, 'expired_files': 0, 'total_size_kb': 0}
