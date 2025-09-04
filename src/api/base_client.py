from abc import ABC, abstractmethod

import aiohttp

from src.api.utils import retry_on_unauthorized


class BaseClient(ABC):
    """
    Base class for API clients.
    """

    def __init__(self, base_url: str, credentials: dict[str, str]):
        self._base_url = base_url
        self._credentials = credentials
        self._headers: dict[str, str] = {}

    @retry_on_unauthorized
    async def _post(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """
        Send an async POST request.
        """
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.post(endpoint, **kwargs) as response:
                return response

    @abstractmethod
    async def login(self) -> None:
        """
        Authenticate and set the Authorization header.
        """
        pass
