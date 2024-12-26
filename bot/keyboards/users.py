from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import CheckForAdmin
import other.log.colors as colors
import other.log.logging as logging
from handlers.core import GetLessons
from keyboards.admins import __DELETE_SCHEDULE_WARN__
from keyboards.other import GenLesson, GenButtonBack, __BACK_IN_MAIN_MENU__

log = logging.logging(Name='INIT', Color=colors.purple)

__HOMEWORK__ = GenLesson(appstart_callback_data='lesson:show:', lessons=GetLessons())
__HOMEWORK__.inline_keyboard.append([__BACK_IN_MAIN_MENU__])
log.init('__HOMEWORK__' + ': OK')

__OFF__NOTIFICATIONS__ = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [InlineKeyboardButton(text='Да, я хочу отключить уведомления', callback_data='profile:notifications:off')],
    [InlineKeyboardButton(text='Нет, я хочу оставить уведомления', callback_data='profile')]
])
log.init('__OFF__NOTIFICATIONS__' + ': OK')


async def GenStart(user_id: int) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Уроки 📚', callback_data='lessons')],
        [InlineKeyboardButton(text='Расписание 📑', callback_data='schedule')],
        [InlineKeyboardButton(text='Расписание звонков 🕝', callback_data='schedule:recess')],
    ]

    if await CheckForAdmin(user_id):
        buttons.append([InlineKeyboardButton(text='Админ-панель‼️', callback_data='admin_panel')])

    buttons.append([InlineKeyboardButton(text='Профиль 👤', callback_data='profile')])

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)


async def GenLesson(user_id: int, lesson_id: str, url: str | None) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if await CheckForAdmin(user_id):
        buttons.append([
            InlineKeyboardButton(text='❌ Удалить ❌',
                                 callback_data=f'lesson:delete_warn:{lesson_id}')])
    else:
        buttons.append([InlineKeyboardButton(text='⚠️ Неверные данные ⚠️',
                                             callback_data=f'lesson:nftadmins:{lesson_id}')])
    
    if url != None: buttons.append([InlineKeyboardButton(text='ГДЗ', url=url)])
    
    buttons.append([GenButtonBack('lessons')])
    buttons.append([__BACK_IN_MAIN_MENU__])
    
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)


async def GenSchedule(user_id: int) -> InlineKeyboardMarkup:
    if await CheckForAdmin(user_id):
        buttons: list[list[InlineKeyboardButton]] = [
            [__DELETE_SCHEDULE_WARN__],
            [__BACK_IN_MAIN_MENU__]
        ]
    else:
        buttons: list[list[InlineKeyboardButton]] = [
            [InlineKeyboardButton(text='⚠️ Расписание не верное или устаревшее ⚠️', callback_data='schedule:nftadmins')],
            [__BACK_IN_MAIN_MENU__]
        ]
    
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)


async def GenProfile(isSendNotifications: bool) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if isSendNotifications: buttons.append([InlineKeyboardButton(text='Отключить уведомления', callback_data='profile:notifications:off_warn')])
    else: buttons.append([InlineKeyboardButton(text='Включить уведомления', callback_data='profile:notifications:on')])

    buttons.append([__BACK_IN_MAIN_MENU__])

    return InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
