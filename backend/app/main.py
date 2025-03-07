import asyncio

import uvicorn
import nest_asyncio
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

import logging
import database.requests as rq
from other.config import config
from other.lessons import Lessons
import database.models as db_models

from handlers.roles import router as roles_router
from handlers.users import router as users_router
from handlers.lessons import router as lessons_router
from handlers.schedule import router as schedule_router
from handlers.admin_panel import router as admin_panel_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start() -> None:
    await db_models.init_db()
    await rq.SyncLessons(Lessons.lessons)
    await rq.SyncRoles()

    app = FastAPI(
        title=config.PROJECT_NAME
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )

    api_router = APIRouter()
    api_router.include_router(roles_router)
    api_router.include_router(users_router)
    api_router.include_router(lessons_router)
    api_router.include_router(schedule_router)
    api_router.include_router(admin_panel_router)

    app.include_router(api_router)

    uvicorn.run(app=app, host='0.0.0.0', port=config.BACKEND_PORT)


if __name__ == 'main':
    loop = asyncio.get_event_loop()
    nest_asyncio.apply(loop)

    asyncio.run(start())
