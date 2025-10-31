import time
from functools import wraps

from limits import RateLimitItem, storage, strategies

limits_storage = storage.MemoryStorage()
limiter = strategies.FixedWindowRateLimiter(limits_storage)

def job_limiter(rate_limit: RateLimitItem, waiting_time: int = 0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if limiter:
                while not limiter.test(rate_limit, func.__name__):
                    # time.sleep(0.05)
                    print("waiting....")
            result = func(*args, **kwargs)
            if waiting_time > 0:
                print("The waiting time is:", waiting_time)
                # time.sleep(waiting_time)

            return result

        return wrapper

    return decorator
