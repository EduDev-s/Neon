from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import utils
import other.log.colors as colors
import other.log.logging as logging
from handlers.core import GetLessons
from keyboards.admins import __DELETE_SCHEDULE_WARN__
from keyboards.other import GenLesson, GenButtonBack, __BACK_IN_MAIN_MENU__

log = logging.logging(Name='INIT', Color=colors.purple)

__HOMEWORK__: InlineKeyboardMarkup = GenLesson(appstart_callback_data='lesson:show:', lessons=GetLessons())
__HOMEWORK__.inline_keyboard.append([__BACK_IN_MAIN_MENU__])
log.init('__HOMEWORK__' + ': OK')

__OFF_NOTIFICATIONS__ = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [InlineKeyboardButton(text='Да, я хочу отключить уведомления', callback_data='profile:notifications:off')],
    [InlineKeyboardButton(text='Нет, я хочу оставить уведомления', callback_data='profile')]
])
log.init('__OFF_NOTIFICATIONS__' + ': OK')

__SCHEDULE_RECESS__ = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Обновить', callback_data='schedule:recess')],
    [__BACK_IN_MAIN_MENU__]
])
log.init('__SCHEDULE_RECESS__' + ': OK')


async def GenStart(user_id: int) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    if (await utils.GetPermissions(user_id)).lessons.use:
        buttons.append([InlineKeyboardButton(text='Уроки 📚', callback_data='lessons')])

    if (await utils.GetPermissions(user_id)).schedule.use:
        buttons.append([InlineKeyboardButton(text='Расписание 📑', callback_data='schedule')])

    if (await utils.GetPermissions(user_id)).schedule_call.use:
        buttons.append([InlineKeyboardButton(text='Расписание звонков 🕝', callback_data='schedule:recess')])

    if (await utils.GetPermissions(user_id)).schedule_exam.use:
        buttons.append([InlineKeyboardButton(text='Расписание экзаменов 🎯', callback_data='schedule:exam')])

    if (
            (await utils.GetPermissions(user_id)).admin_panel.use.server_status or
            (await utils.GetPermissions(user_id)).admin_panel.use.newsletter or
            (await utils.GetPermissions(user_id)).admin_panel.use.role
            ):
        buttons.append([InlineKeyboardButton(text='Админ-панель‼️', callback_data='admin_panel')])

    buttons.append([InlineKeyboardButton(text='Профиль 👤', callback_data='profile')])

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)


async def GenLesson(user_id: int, lesson_id: str, url: str | None) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if (await utils.GetPermissions(user_id)).lessons.edit.homework:
        buttons.append([InlineKeyboardButton(text='❌ Удалить ❌', callback_data=f'lesson:delete_warn:{lesson_id}')])
    else:
        buttons.append([InlineKeyboardButton(text='⚠️ Неверные данные ⚠️', callback_data=f'lesson:nftadmins:{lesson_id}')])

    if url is not None:
        buttons.append([InlineKeyboardButton(text='ГДЗ', url=url)])

    buttons.append([GenButtonBack('lessons')])
    buttons.append([__BACK_IN_MAIN_MENU__])

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)


async def GenSchedule(user_id: int) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if (await utils.GetPermissions(user_id)).schedule.edit:
        buttons.append([__DELETE_SCHEDULE_WARN__])
    else:
        buttons.append([InlineKeyboardButton(text='⚠️ Расписание не верное или устаревшее ⚠️', callback_data='schedule:nftadmins')])

    buttons.append([__BACK_IN_MAIN_MENU__])

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)


async def GenProfile(isSendNotifications: bool) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if isSendNotifications:
        buttons.append([InlineKeyboardButton(text='Отключить уведомления', callback_data='profile:notifications:off_warn')])
    else:
        buttons.append([InlineKeyboardButton(text='Включить уведомления', callback_data='profile:notifications:on')])

    buttons.append([__BACK_IN_MAIN_MENU__])

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
