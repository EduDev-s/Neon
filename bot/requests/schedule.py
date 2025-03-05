import httpx

import requests.errors as errors
from requests.async_client_wrapper import _wrapped_client
from requests.RequestsData import RequestsData as RData


async def GetSchedule(
            user_id: int,
            requests_timeout: int = None
        ) -> dict[str, str | bytes] | FileNotFoundError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetSchedule',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            response_json = response.json()
            response_json['file'] = bytes(response_json['file'])

            return response_json

        elif response.status_code == httpx.codes.NO_CONTENT:
            return FileNotFoundError

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def UpdateSchedule(
            user_id: int,
            file: bytes | None = None,
            requests_timeout: int = None
        ) -> list[dict[dict, dict]] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='POST',
            url='UpdateSchedule',
            json=RData(user_id, {
                'file': list(file) if file is not None else None
            }).data,
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def GetScheduleCall(
            user_id: int,
            requests_timeout: int = None
        ) -> dict[str, str | dict] | FileNotFoundError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetScheduleCall',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def GetScheduleExam(
            user_id: int,
            requests_timeout: int = None
        ) -> dict[str, str | dict] | FileNotFoundError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetScheduleExam',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            return response.json()

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error
