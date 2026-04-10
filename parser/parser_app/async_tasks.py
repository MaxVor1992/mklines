"""
Async Task Manager для асинхронного парсинга

Архитектура:
1. Пользователь создаёт задачу → получает task_id
2. Фоновый поток обрабатывает задачу
3. Пользователь проверяет статус → WAIT/DONE/ERROR
4. Пользователь забирает результат

Аналогично Arsenkin и XMLRiver delayed режиму.
"""

import uuid
import threading
import time
import logging
from datetime import datetime
from . import xmlriver

logger = logging.getLogger(__name__)

# Хранилище задач (in-memory)
# Структура: {task_id: {status, progress, result, error, created_at, ...}}
_tasks = {}
_tasks_lock = threading.Lock()


class TaskStatus:
    """Статусы задачи"""
    PENDING = "pending"       # Задача создана, ожидает обработки
    RUNNING = "running"       # Задача выполняется
    DONE = "done"             # Задача завершена успешно
    ERROR = "error"           # Задача завершена с ошибкой


def create_task(search_queries, engine, region, depth, repeats=1, device='desktop', docache=True):
    """
    Создать задачу парсинга.

    Args:
        search_queries: список поисковых запросов
        engine: "yandex" или "google"
        region: регион
        depth: глубина (ТОП-10/20/30)
        repeats: количество повторений
        device: устройство
        docache: кеширование

    Returns:
        task_id: str — идентификатор задачи
    """
    task_id = str(uuid.uuid4())[:12]  # Короткий ID

    with _tasks_lock:
        _tasks[task_id] = {
            'task_id': task_id,
            'status': TaskStatus.PENDING,
            'progress': 0,           # Процент выполнения (0-100)
            'processed': 0,          # Количество обработанных запросов
            'total': len(search_queries),
            'result': None,          # Результат (ParsingResult)
            'error': None,           # Текст ошибки
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'params': {
                'search_queries': search_queries,
                'engine': engine,
                'region': region,
                'depth': depth,
                'repeats': repeats,
                'device': device,
                'docache': docache,
            }
        }

    logger.info(f"Task created: {task_id} ({len(search_queries)} queries)")

    # Запускаем фоновую обработку
    thread = threading.Thread(target=_process_task, args=(task_id,), daemon=True)
    thread.start()

    return task_id


def get_task_status(task_id):
    """
    Получить статус задачи.

    Returns:
        dict со статусом или None если задача не найдена
    """
    with _tasks_lock:
        task = _tasks.get(task_id)
        if not task:
            return None

        return {
            'task_id': task['task_id'],
            'status': task['status'],
            'progress': task['progress'],
            'processed': task['processed'],
            'total': task['total'],
            'created_at': task['created_at'],
            'started_at': task['started_at'],
            'completed_at': task['completed_at'],
            'error': task['error'],
        }


def get_task_result(task_id):
    """
    Получить результат задачи.

    Returns:
        ParsingResult или None
    """
    with _tasks_lock:
        task = _tasks.get(task_id)
        if not task:
            return None

        if task['status'] != TaskStatus.DONE:
            return None

        return task['result']


def list_user_tasks(limit=20):
    """
    Список последних задач.

    Returns:
        list of dict
    """
    with _tasks_lock:
        tasks = list(_tasks.values())

    # Сортируем по created_at (новые первые)
    tasks.sort(key=lambda t: t['created_at'], reverse=True)

    # Возвращаем только статусы без результатов
    result = []
    for task in tasks[:limit]:
        result.append({
            'task_id': task['task_id'],
            'status': task['status'],
            'progress': task['progress'],
            'processed': task['processed'],
            'total': task['total'],
            'created_at': task['created_at'],
            'completed_at': task['completed_at'],
            'error': task['error'],
        })

    return result


def _process_task(task_id):
    """
    Фоновая обработка задачи.
    """
    with _tasks_lock:
        task = _tasks[task_id]
        task['status'] = TaskStatus.RUNNING
        task['started_at'] = datetime.now().isoformat()

    logger.info(f"Task {task_id} started processing")

    try:
        params = task['params']
        search_queries = params['search_queries']
        engine = params['engine']
        region = params['region']
        depth = params['depth']
        repeats = params['repeats']
        device = params['device']

        # Всегда используем отложенный режим для фоновой обработки
        parser = xmlriver.SearchParser(
            user_requests=search_queries,
            engine=engine,
            count=depth,
            repeats=repeats,
            region=str(region),
            docache=params['docache'],
            device=device,
            use_delayed_mode=True  # Forced delayed mode для background
        )

        # Обновляем прогресс в отдельном потоке
        progress_thread = threading.Thread(
            target=_update_progress,
            args=(task_id, search_queries),
            daemon=True
        )
        progress_thread.start()

        # Запускаем парсинг
        result = parser.run_parse()

        with _tasks_lock:
            task['status'] = TaskStatus.DONE
            task['progress'] = 100
            task['processed'] = len(search_queries)
            task['result'] = result
            task['completed_at'] = datetime.now().isoformat()

        logger.info(f"Task {task_id} completed: {len(result.result)} results")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)

        with _tasks_lock:
            task['status'] = TaskStatus.ERROR
            task['error'] = str(e)
            task['completed_at'] = datetime.now().isoformat()


def _update_progress(task_id, search_queries):
    """
    Периодическое обновление прогресса (пока парсинг выполняется).
    Останавливается когда статус DONE или ERROR.
    """
    import time

    while True:
        time.sleep(2)

        with _tasks_lock:
            task = _tasks.get(task_id)
            if not task or task['status'] in (TaskStatus.DONE, TaskStatus.ERROR):
                break

            # Приблизительный прогресс по количеству запросов
            # Точный прогресс обновляется из run_parse
            elapsed = time.time() - (datetime.fromisoformat(task['started_at']).timestamp() if task['started_at'] else time.time())
            # Эвристика: 1 запрос = ~5 сек
            estimated_total = len(search_queries) * 5
            progress = min(95, int((elapsed / max(estimated_total, 1)) * 100))

            task['progress'] = progress


def cleanup_old_tasks(max_age_seconds=3600):
    """
    Очистить старые задачи (старше max_age_seconds).
    Запускать периодически.
    """
    now = datetime.now()
    removed = 0

    with _tasks_lock:
        to_remove = []
        for task_id, task in _tasks.items():
            created = datetime.fromisoformat(task['created_at'])
            if (now - created).total_seconds() > max_age_seconds:
                to_remove.append(task_id)

        for task_id in to_remove:
            del _tasks[task_id]
            removed += 1

    if removed > 0:
        logger.info(f"Cleaned up {removed} old tasks")

    return removed
