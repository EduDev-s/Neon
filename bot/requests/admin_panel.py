from base64 import b64decode

import httpx

from requests.async_client_wrapper import _wrapped_client

import requests.errors as errors
from requests.requests_data import RequestsData as RData


async def CreateDatabaseBackup(
            user_id: int,
            requests_timeout: int = None
        ) -> bytes | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='CreateDatabaseBackup',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            binary_data = b64decode(str(response.json()).encode("utf-8"))

            return binary_data

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error
