import httpx

from requests.async_client_wrapper import _wrapped_client

import requests.errors as errors
from requests.requests_data import RequestsData as RData


async def GetUser(
            user_id: int,
            requests_timeout: int = None
        ) -> dict[str, str | dict] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetUser',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            response_json = response.json()

            if response_json['user_id'] == user_id:
                return response_json

        elif response.status_code == httpx.codes.NOT_FOUND:
            raise errors.ResponseError(response_json)

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def GetAdmins(
            user_id: int,
            requests_timeout: int = None
        ) -> list[dict[dict, dict]] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetAdmins',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            response_json = response.json()
            return response_json

        elif response.status_code == httpx.codes.NOT_FOUND:
            raise errors.ResponseError(response_json)

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def GetUsers(
            user_id: int,
            requests_timeout: int = None
        ) -> dict[str, str | dict] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetUsers',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            response_json = response.json()
            return response_json['users']

        elif response.status_code == httpx.codes.NOT_FOUND:
            raise errors.ResponseError(response_json)

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def SetUser(
            user_id: int,
            username: str,
            first_name: str | None,
            last_name: str | None,
            send_notifications: bool,
            blocked_bot: bool,
            role_ids: list[int],
            requests_timeout: int = None
        ) -> None | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='POST',
            url='SetUser',
            json=RData(user_id, args={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'send_notifications': send_notifications,
                'blocked_bot': blocked_bot,
                'role_ids': role_ids
            }).data
        ))

        if response.status_code == httpx.codes.OK:
            return

        elif response.status_code == httpx.codes.NOT_FOUND:
            raise errors.ResponseError(response.json())

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def UpdateUser(
            user_id: int,
            username: str,
            first_name: str | None,
            last_name: str | None,
            send_notifications: bool,
            blocked_bot: bool,
            role_ids: list[int],
            requests_timeout: int = None
        ) -> None | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='POST',
            url='UpdateUser',
            json=RData(user_id, args={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'send_notifications': send_notifications,
                'blocked_bot': blocked_bot,
                'role_ids': role_ids
            }).data
        ))

        if response.status_code == httpx.codes.OK:
            return

        elif response.status_code == httpx.codes.NOT_FOUND:
            raise errors.ResponseError(response.json())

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error
