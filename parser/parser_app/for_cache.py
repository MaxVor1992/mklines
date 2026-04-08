from functools import lru_cache, wraps
from datetime import datetime, timedelta
from flask_login import current_user

# to use: @timed_lru_cache(10)

def timed_lru_cache(seconds: int = 12 * 3600, maxsize: int = 9512, docache=True):
    def wrapper_cache(func):
        if docache:
            func = lru_cache(maxsize=maxsize)(func)
            func.lifetime = timedelta(seconds=seconds)
            func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if not docache:
                return func(*args, **kwargs)

            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache
