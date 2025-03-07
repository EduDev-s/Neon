import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor

from xml.dom import NotFoundErr
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from other.config import config
from database.models import async_session, log
from database.models import User, Role, user_role, Lesson, Schedule
from other.PermissionsManager.models import Permissions
from other.PermissionsManager.PermissionsManager import PM


async def __SaveData(user_id: int | None, session: AsyncSession) -> None:
    log.debug(user_id, 'Saving data to db')

    await session.flush()
    await session.commit()


async def SyncLessons(lessons: list[list[str]]):
    log.init('Starting sync lessons')

    async with async_session() as session:
        try:
            # Get the list of existing lesson IDs
            existing_lesson: list[Lesson] = (await session.scalars(select(Lesson))).all()
            existing_lesson_ids: list[str] = []

            for lesson in existing_lesson:
                existing_lesson_ids.append(lesson.lesson_id)

            # Create new lesson IDs
            for lesson in lessons:
                if lesson[0] not in existing_lesson_ids:
                    log.init(f'Subject \'{lesson[0]}\' not found in the Lessons table')

                    session.add(Lesson(lesson_id=lesson[0], photo=None))
                    log.init(f'Subject \'{lesson[0]}\' added in the Lessons table')

            # Delete lessons that are not in the provided list
            for lesson_id in existing_lesson_ids:
                deleting = True

                for lesson in lessons:
                    if lesson_id == lesson[0]:
                        deleting = False

                if deleting:
                    await session.delete(await session.scalar(select(Lesson).where(Lesson.lesson_id == lesson_id)))

                    log.init(f'The field \'{lesson_id}\' from the Lessons table is removed')

            # Save the changes
            await __SaveData(None, session)
        except Exception as Error:
            log.error(None, str(Error))


async def SyncRoles():
    log.init('Starting sync roles')

    async with async_session() as session:
        try:
            log.debug(None, f'Getting \'{config.TG_ID_OWNER}\' is started')
            user = await GetUser(None, config.TG_ID_OWNER)

            if user == AttributeError:
                log.warn(None, f'Getting \'{config.TG_ID_OWNER}\' is not complied')

                log.info(None, f'Adding user \'{config.TG_ID_OWNER}\'')
                await SetUser(config.TG_ID_OWNER, config.TG_USERNAME_OWNER, config.TG_FIRST_NAME_OWNER, config.TG_LAST_NAME_OWNER, False, [])
            else:
                log.debug(None, f'Getting \'{config.TG_ID_OWNER}\' is complied')

            log.debug(None, 'Getting role owner is started')
            role: Role = await GetRole(None, config.ID_ROLE_OWNER)
            log.debug(None, 'Getting role owner is complied')

            if role != AttributeError:
                user_ids = []
                for user in role.users:
                    user_ids.append(user.user_id)

                await UpdateRole(user_id=None, role_id=config.ID_ROLE_OWNER, user_ids=user_ids, name=role.name, permissions=PM.OwnerPermissions)
            else:
                await SetRole(user_id=None, role_id=config.ID_ROLE_OWNER, user_ids=[config.TG_ID_OWNER], name=config.NAME_ROLE_OWNER, permissions=PM.OwnerPermissions)

            log.debug(None, 'Getting role default is started')
            role: Role = await GetRole(None, config.ID_ROLE_DEFAULT)
            log.debug(None, 'Getting role default is complied')

            if role != AttributeError:
                user_ids = []
                for user in role.users:
                    user_ids.append(user.user_id)

                await UpdateRole(user_id=None, role_id=config.ID_ROLE_DEFAULT, user_ids=user_ids, name=role.name, permissions=PM.DefaultPermissions)
            else:
                await SetRole(user_id=None, role_id=config.ID_ROLE_DEFAULT, user_ids=[], name=config.NAME_ROLE_DEFAULT, permissions=PM.DefaultPermissions)

            await __SaveData(None, session)
        except Exception as Error:
            log.error(None, str(Error))


async def Backup(user_id: int | None) -> str | Exception:
    try:
        log.warn(user_id, f'User {user_id} began backup database')

        url = make_url(config.POSTGRES_URL)
        host = url.host
        port = url.port
        database = url.database
        username = url.username
        password = url.password

        command = [
            'pg_dump',
            '-h', host,
            '-p', str(port),
            '-U', username,
            '-d', database,
            '-Fp'
        ]

        # Запускаем синхронный процесс в отдельном потоке
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            process = await loop.run_in_executor(
                pool,
                lambda: subprocess.run(
                    command,
                    env={'PGPASSWORD': password},
                    capture_output=True,
                    text=True
                )
            )

        if process.returncode == 0:
            log.warn(user_id, 'Backup completed')
            return process.stdout
        else:
            error = process.stderr.strip()
            log.error(user_id, f'Backup failed: {error}')
            raise Exception(f'Backup failed: {error}')

    except Exception as error:
        log.error(user_id, f'Backup error: {str(error)}')
        raise error


# SETTING


async def SetUser(user_id: int, username: str, first_name: str, last_name: str, blocked_bot: bool = False, roles: list[Role] = []) -> None | IntegrityError | Exception:
    log.info(user_id, 'Setting User')

    async with async_session() as session:
        try:
            session.add(User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                send_notifications=True,
                blocked_bot=blocked_bot,
                roles=roles
            ))

            await __SaveData(user_id, session)
            return

        except IntegrityError as Error:
            log.error(user_id, f'ERROR: {Error.orig} REQUESTS: {Error.statement}')
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def SetRole(user_id: int, role_id: int, user_ids: list[int], name: str, permissions: Permissions):
    log.info(user_id, f'Setting role \'{name}\'')

    async with async_session() as session:
        try:
            log.debug(user_id, f'Starting GetUsers {user_ids}')
            users: list[User] = []

            for user_id_ in user_ids:
                users.append(await GetUser(user_id, user_id_))

            session.add(instance=Role(
                role_id=role_id,
                name=name,
                permissions=PM.ClassToJSON(user_id, permissions),
                users=users
            ))

            await __SaveData(user_id, session)
            return

        except IntegrityError as Error:
            log.error(user_id, f'ERROR: {Error.orig} REQUESTS: {Error.statement}')
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def SetSendNotifications(user_id: int, send_notifications: bool) -> None | AttributeError | Exception:
    log.info(user_id, f'Setting SendNotifications \'{send_notifications}\'')

    async with async_session() as session:
        try:
            (await session.scalar(select(User).where(User.user_id == user_id))).send_notifications = send_notifications

            await __SaveData(user_id, session)
            return

        except AttributeError as Error:
            log.error(user_id, str(Error))
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


# GETTING


async def GetUser(user_id: int, rq_user_id: int) -> User | AttributeError | Exception:
    log.info(user_id, f'Getting User: \'{rq_user_id}\'')

    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.user_id == rq_user_id))

            if user is None:
                log.warn(user_id, f'User \'{rq_user_id}\' not found!')
                return AttributeError
            else:
                return user

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def GetUsers(user_id: int) -> list[User] | Exception:
    log.info(user_id, 'Getting Users . . .')

    async with async_session() as session:
        try:
            return (await session.scalars(select(User))).unique().all()

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def GetRole(user_id: int, role_id: int) -> Role | AttributeError | Exception:
    log.info(user_id, f'Getting Role: \'{role_id}\'')

    async with async_session() as session:
        try:
            role = await session.scalar(select(Role).where(Role.role_id == role_id))

            if role is None:
                log.warn(user_id, f'Role \'{role_id}\' not found!')
                return AttributeError
            else:
                return role

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def GetRoles(user_id: int) -> list[Role] | Exception:
    log.info(user_id, 'Getting Users . . .')

    async with async_session() as session:
        try:
            return (await session.scalars(select(Role))).unique().all()

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def GetLesson(user_id: int, lesson_id: str) -> Lesson | AttributeError | Exception:
    log.info(user_id, f'Getting Lesson: \'{lesson_id}\'')

    async with async_session() as session:
        try:
            return (await session.scalar(select(Lesson).where(Lesson.lesson_id == lesson_id)))

        except AttributeError as Error:
            log.error(user_id, str(Error))
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def GetLessons(user_id: int) -> list[Lesson] | AttributeError | Exception:
    log.info(user_id, 'Getting Lessons')

    async with async_session() as session:
        try:
            return (await session.scalars(select(Lesson))).all()

        except AttributeError as Error:
            log.error(user_id, str(Error))
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def GetSchedule(user_id: int) -> Schedule | FileNotFoundError | Exception:
    log.info(user_id, f'Getting Schedule: \'{user_id}\'')

    async with async_session() as session:
        try:
            schedule = await session.scalar(select(Schedule).where(Schedule.id == 1))

            if schedule is None or schedule.file is None:
                log.warn(user_id, 'Schedule not found!')
                return FileNotFoundError
            else:
                return schedule

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


# Updating


async def UpdateLesson(user_id: int,
                       lesson_id: str,
                       homework: str | None = None,
                       photo: bool | None = None,
                       url: str | None = None
                       ) -> None | AttributeError | Exception:
    log.info(user_id, f'Setting Lesson: \'{lesson_id}\' / homework: \'{homework}\' / photo: \'{photo}\' / url: \'{url}\'')

    async with async_session() as session:
        try:
            lesson: Lesson = await session.scalar(select(Lesson).where(Lesson.lesson_id == lesson_id))

            lesson.homework = homework
            lesson.photo = photo
            lesson.url = url

            await __SaveData(user_id, session)
            return

        except AttributeError as Error:
            log.error(user_id, str(Error))
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def UpdateUser(user_id: int, username: str, first_name: str, last_name: str, send_notifications: bool, blocked_bot: bool = False, role_ids: list[int] = [config.ID_ROLE_DEFAULT]) -> None | IndexError | IntegrityError | Exception:
    log.info(user_id, 'Updating User')

    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.user_id == user_id))

            if user is None:
                log.error(user_id, f'USER: {user_id} NOT FOUNT')
                return IndexError

            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.send_notifications = send_notifications
            user.blocked_bot = blocked_bot
            user.roles = (await session.scalars(select(Role).filter(Role.role_id.in_(role_ids)))).unique().all()

            await __SaveData(user_id, session)
            return

        except IntegrityError as Error:
            log.error(user_id, f'ERROR: {Error.orig} REQUESTS: {Error.statement}')
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def UpdateSchedule(user_id: int, photo: bytes | None) -> None | IndentationError | Exception:
    log.info(user_id, 'Updating User')

    async with async_session() as session:
        try:
            schedule = await session.scalar(select(Schedule).where(Schedule.id == 1))

            if schedule is None:
                log.error(user_id, 'SCHEDULE NOT FOUNT')

                session.add(Schedule(
                    id=1
                ))
                await __SaveData(user_id, session)

                return (await UpdateSchedule(user_id, photo))

            schedule.file = photo

            await __SaveData(user_id, session)
            return

        except IntegrityError as Error:
            log.error(user_id, f'ERROR: {Error.orig} REQUESTS: {Error.statement}')
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def UpdateRole(user_id, role_id: int, user_ids: list[int], name: str, permissions: Permissions) -> None | NotFoundErr | ArithmeticError | IntegrityError | Exception:
    log.info(user_id, f'Updating Role: \'{name}\' [{role_id}]')

    async with async_session() as session:
        try:
            role = await session.scalar(select(Role).where(Role.role_id == role_id))

            if role is None:
                log.error(user_id, 'ROLE NOT FOUNT')
                return NotFoundErr

            users: list[User] = []
            for user_id_ in user_ids:
                user = await GetUser(user_id, user_id_)

                if user == AttributeError:
                    return ArithmeticError
                else:
                    users.append(await session.merge(user))

            role.users = users
            role.name = name
            role.permissions = PM.ClassToJSON(user_id, permissions)

            await __SaveData(user_id, session)
            return

        except IntegrityError as Error:
            log.error(user_id, f'ERROR: {Error.orig} REQUESTS: {Error.statement}')
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


# DELETING


async def DeleteUser(user_id: int, user: User) -> None | AttributeError | Exception:
    log.warn(user_id, f'Deleting User: {user.user_id}')

    async with async_session() as session:
        try:
            await session.delete(user)

            await __SaveData(user_id, session)
            return

        except AttributeError as Error:
            log.error(user_id, str(Error))
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error


async def DeleteRole(user_id: int, role: Role) -> None | AttributeError | Exception:
    log.warn(user_id, f'Deleting Role: {role.role_id}')

    async with async_session() as session:
        try:
            await session.execute(user_role.delete().where(user_role.c.role_id == role.id))  # DONT CHANGE !!!
            await session.delete(role)

            await __SaveData(user_id, session)
            return

        except AttributeError as Error:
            log.error(user_id, str(Error))
            return Error

        except Exception as Error:
            log.error(user_id, str(Error))
            return Error
