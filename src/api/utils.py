from functools import wraps
import httpx


def retry_on_unauthorized(func):
    """
    Async decorator to retry a function if it raises a 401 Unauthorized error.
    """

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        response: httpx.Response = await func(self, *args, **kwargs)
        if response.status_code == 401:
            await self.login()
            response = await func(self, *args, **kwargs)
        response.raise_for_status()
        return response

    return wrapper
