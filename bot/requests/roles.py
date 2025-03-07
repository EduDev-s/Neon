import httpx

from requests.async_client_wrapper import _wrapped_client

import requests.errors as errors
from other.PermissionsManager.models import Permissions
from requests.requests_data import RequestsData as RData
from other.PermissionsManager.PermissionsManager import PM


async def GetRole(
            user_id: int,
            role_id: int,
            requests_timeout: int = None
        ) -> dict[str, str | dict] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetRole',
            json=RData(user_id).data,
            params={
                'RoleID': role_id
            }
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def GetRoles(user_id: int,
                   requests_timeout: int = None
                   ) -> list[dict[str, str | dict]] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetRoles',
            json=RData(user_id).data,
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()['roles']

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def SetRole(
            user_id: int,
            role_id: int,
            user_ids: list[int],
            name: str,
            permissions: Permissions,
            requests_timeout: int = None
        ) -> dict[str, str | bytes] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='POST',
            url='SetRole',
            json=RData(user_id, {
                'RoleID': role_id,
                'user_ids': user_ids,
                'name': name,
                'permissions': PM.ClassToJSON(user_id, permissions)['permissions']
            }).data
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def UpdateRole(
            user_id: int,
            role_id: int,
            user_ids: list[int],
            name: str,
            permissions: Permissions,
            requests_timeout: int = None
        ) -> dict[str, str | bytes] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='POST',
            url='UpdateRole',
            json=RData(user_id, {
                'RoleID': role_id,
                'user_ids': user_ids,
                'name': name,
                'permissions': PM.ClassToJSON(user_id, permissions)['permissions']
            }).data
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def DeleteRole(
            user_id: int,
            role_id: int,
            requests_timeout: int = None
        ) -> dict[str, str | bytes] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='DELETE',
            url='DeleteRole',
            json=RData(user_id).data,
            params={
                'RoleID': role_id
            }
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error
