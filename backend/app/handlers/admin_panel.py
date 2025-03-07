from base64 import b64encode

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

import utils
import database.requests as rq
from handlers.bodies.core import Core

router = APIRouter(tags=['Admin panel'])


@router.get('/CreateDatabaseBackup', summary='Creates a backup copy of the database')
async def GetUser(body: Core):
    if (await utils.CheckUserID(body.UserID, body.UserID)) is not None:
        return await utils.CheckUserID(body.UserID, body.UserID)

    try:
        backup_data = await rq.Backup(body.UserID)
        encrypted = utils.GetFernet().encrypt(backup_data.encode())
        return JSONResponse(status_code=status.HTTP_200_OK, content=b64encode(encrypted).decode("utf-8"))

    except Exception as Error:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            'status': 'fail',
            'details': str(Error)
        })
