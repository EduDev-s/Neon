import httpx

from requests.async_client_wrapper import _wrapped_client

import requests.errors as errors
from requests.requests_data import RequestsData as RData


async def GetLessons(
            user_id: int,
            requests_timeout: int = None
        ) -> list[dict[str, str | bytes]] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetLessons',
            json=RData(user_id).data
        ))

        if response.status_code == httpx.codes.OK:
            response_json = response.json()
            for lesson in response_json:
                lesson['photo'] = bytes(lesson['photo']) if lesson['photo'] is not None else None

            return response_json

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def GetLesson(
            user_id: int,
            lesson_id: str,
            requests_timeout: int = None
        ) -> dict[str, str | bytes] | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='GET',
            url='GetLesson',
            json=RData(user_id).data,
            params={'lesson_id': lesson_id}
        ))

        if response.status_code == httpx.codes.OK:
            response_json = response.json()
            response_json['photo'] = bytes(response_json['photo']) if response_json['photo'] is not None else None

            return response_json

        elif response.status_code == httpx.codes.NOT_FOUND:
            raise errors.ResponseError(response_json)

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error


async def UpdateLesson(
            user_id: int,
            lessons_id: str,
            homework: str | None = None,
            photo: bytes | None = None,
            url: str | None = None,
            requests_timeout: int = None
        ) -> None | errors.ResponseError | httpx.HTTPStatusError:
    requester = _wrapped_client.make_requester(requests_timeout)

    try:
        response: httpx.Response = await requester(_wrapped_client.client.build_request(
            method='POST',
            url='UpdateLesson',
            json=RData(user_id, args={
                'lessons_id': lessons_id,
                'homework': homework,
                'photo': list(photo) if photo is not None else None,
                'url': url
            }).data
        ))

        if response.status_code == httpx.codes.OK:
            return

    except httpx.HTTPStatusError as http_status_error:
        raise http_status_error
