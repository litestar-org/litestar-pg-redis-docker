"""Async HTTP request client implementation built on `httpx`."""
from typing import Any

import httpx


class ClientException(Exception):
    """Base client exception."""


class HttpClient:
    """Base class for HTTP clients.

    ```python
    client = HttpClient()
    response = await client.request("GET", "/some/resource")
    assert response.status_code == 200
    ```
    """

    _client = httpx.AsyncClient()

    async def request(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Passes `*args`, `**kwargs` straight through to
        ``httpx.AsyncClient.request``, we  call `raise_for_status()` on the
        response and wrap any `HTTPX` error in a `ClientException`.

        Parameters
        ----------
        *args : Any
            Unpacked into `httpx.AsyncClient.request()`.
        **kwargs : Any
            Unpacked into `httpx.AsyncClient.request()`.

        Returns
        -------
        httpx.Response
            Return value of `httpx.AsyncClient.request()` after calling
            `httpx.Response.raise_for_status()`

        Raises
        ------
        ClientException
            Wraps any `httpx.HTTPError` arising from the request or response status check.
        """
        try:
            r = await self._client.request(*args, **kwargs)
            r.raise_for_status()
        except httpx.HTTPError as e:
            url = e.request.url
            raise ClientException(f"Client Error for '{url}'") from e
        return r

    def json(self, response: httpx.Response) -> Any:
        """
        Abstracts deserializing to allow for optional unwrapping of server response, e.g.,
        `{"data": []}`.

        Parameters
        ----------
        response : httpx.Response
            Response object, we call `.json()` on it.

        Returns
        -------
        Any
            The result of `httpx.Response.json()` after passing through `self.unwrap_json()`.
        """
        return self.unwrap_json(response.json())

    @staticmethod
    def unwrap_json(data: Any) -> Any:
        """Overwrite this method for pre-processing response data, for example
        unwrapping enveloped data.

        Parameters
        ----------
        data : Any
            Value returned from `response.json()`.

        Returns
        -------
        Any
            Pre-processed data, default is pass-through/no-op.
        """
        return data

    @classmethod
    async def close(cls) -> None:
        """Closes the underlying client transport and proxies."""
        await cls._client.aclose()
