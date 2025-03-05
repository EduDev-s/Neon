from fastapi.responses import JSONResponse, Response
from fastapi import APIRouter, Request, status

import utils
import database.requests as rq
from other.config import config
from handlers.bodies.core import Core
from handlers.bodies.edit_schedule import Body as EditScheduleBody


router = APIRouter(tags=['Schedule'])


@router.get('/GetSchedule', summary='Get schedule')
async def GetSchedule(body: Core, request: Request):
    if (await utils.CheckUserID(body.UserID, body.UserID)) is not None:
        return await utils.CheckUserID(body.UserID, body.UserID)
    if not (await utils.GetPermissions(body.UserID)).schedule.use:
        return await utils.Error403(request, body.UserID)

    schedule = await rq.GetSchedule(body.UserID)

    if isinstance(schedule, rq.Schedule):
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            'id': schedule.id,
            'file': list(schedule.file)
        })
    elif schedule == FileNotFoundError:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    elif schedule == Exception:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            'status': 'fail',
            'details': str(Exception)
        })


@router.get('/GetScheduleCall', summary='Get schedule call')
async def GetScheduleCall(body: Core, request: Request):
    if (await utils.CheckUserID(body.UserID, body.UserID)) is not None:
        return await utils.CheckUserID(body.UserID, body.UserID)
    if not (await utils.GetPermissions(body.UserID)).schedule_call.use:
        return await utils.Error403(request, body.UserID)

    return JSONResponse(status_code=status.HTTP_200_OK, content={'schedule_call': config.SCHEDULE_CALL})


@router.get('/GetScheduleExam', summary='Get schedule exams')
async def GetScheduleExam(body: Core, request: Request):
    if (await utils.CheckUserID(body.UserID, body.UserID)) is not None:
        return await utils.CheckUserID(body.UserID, body.UserID)
    if not (await utils.GetPermissions(body.UserID)).schedule_exam.use:
        return await utils.Error403(request, body.UserID)

    return JSONResponse(status_code=status.HTTP_200_OK, content={'schedule_exam': config.SCHEDULE_EXAM})


@router.post('/UpdateSchedule', summary='Set lessons')
async def UpdateSchedule(body: EditScheduleBody, request: Request):
    if (await utils.CheckUserID(body.UserID, body.UserID)) is not None:
        return await utils.CheckUserID(body.UserID, body.UserID)
    if not (await utils.GetPermissions(body.UserID)).schedule.edit:
        return await utils.Error403(request, body.UserID)

    await rq.UpdateSchedule(
        body.UserID,
        bytes(body.file) if body.file is not None else None
    )

    return JSONResponse(status_code=status.HTTP_200_OK, content={
            'status': 'success',
            'details': None
        })
