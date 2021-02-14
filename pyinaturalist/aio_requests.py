from typing import Dict

from aiohttp import ClientResponse, ClientSession

from pyinaturalist.constants import INAT_NODE_API_BASE_URL

# from pyinaturalist.forge_utils import copy_signature


class APIClient:
    def __init__(self, base_url: str, session: ClientSession = None):
        self.base_url = base_url
        self.session = session or ClientSession()

    async def request(
        self,
        method: str,
        url: str,
        params: Dict = None,
        headers: Dict = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.session.request(method, url, params=params, headers=headers, **kwargs)

    async def delete(self, url: str, **kwargs) -> ClientResponse:
        return await self.request('DELETE', url, **kwargs)

    async def get(self, url: str, **kwargs) -> ClientResponse:
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs) -> ClientResponse:
        return await self.request('POST', url, **kwargs)

    async def put(self, url: str, **kwargs) -> ClientResponse:
        return await self.request('PUT', url, **kwargs)


class APIV1Client(APIClient):
    def __init__(self, session: ClientSession = None):
        super().__init__(INAT_NODE_API_BASE_URL, session)

    def get_observations(self):
        pass
