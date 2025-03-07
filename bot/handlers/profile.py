from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

import utils
import requests.users as rq_users
from handlers.core import GetRouter
from keyboards.other import GenButtonBack, __BACK_IN_MAIN_MENU__
from keyboards.users import GenProfile, __OFF_NOTIFICATIONS__


router = GetRouter()


@router.callback_query(F.data == 'profile')
async def profile(callback: CallbackQuery):
    await utils.CheckAuthUser(callback.message, callback.message.bot)

    user = await rq_users.GetUser(callback.message.chat.id)
    roles: str = ''

    if user['send_notifications']:
        notifications_status = '✅'
    else:
        notifications_status = '❌'

    if (await utils.GetPermissions(callback.message.chat.id)).admin:
        isAdmin = '✅'
    else:
        isAdmin = '❌'

    for role in user['roles']:
        roles += f'- {role['name']}\n'

    await callback.message.edit_text(f'Имя: {user['first_name']}\nНикнейм : @{user['username']}\nTELEGRAM-ID: <code>{user['user_id']}</code>\n\nУведомления: {notifications_status}\nПрава администратора: {isAdmin}\n\nРоли:\n{roles}',
                                     reply_markup=await GenProfile(user['send_notifications']))


@router.callback_query(F.data == 'profile:notifications:off_warn')
async def profile_notifications_off_warn(callback: CallbackQuery):
    await utils.CheckAuthUser(callback.message, callback.message.bot)

    await callback.message.edit_text('Вы уверены ?\n\n*Если вы отключите уведомления вы не будете получать сообщения об обновлении домашнего задания и расписания. Сюда НЕ входит рассылка от администраторов бота.', reply_markup=__OFF_NOTIFICATIONS__)


@router.callback_query(F.data == 'profile:notifications:off')
async def profile_notifications_off(callback: CallbackQuery):
    await utils.CheckAuthUser(callback.message, callback.message.bot)

    user = await rq_users.GetUser(callback.message.chat.id)
    await rq_users.UpdateUser(
        callback.message.chat.id,
        callback.from_user.username,
        callback.from_user.first_name,
        callback.from_user.last_name,
        False,
        False,
        [role['role_id'] for role in user['roles']]
    )

    await callback.message.edit_text('✅ Успешно! Вы больше не будете получать уведомления.',
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[GenButtonBack('profile')], [__BACK_IN_MAIN_MENU__]]))


@router.callback_query(F.data == 'profile:notifications:on')
async def profile_notifications_on(callback: CallbackQuery):
    await utils.CheckAuthUser(callback.message, callback.message.bot)

    user = await rq_users.GetUser(callback.message.chat.id)
    await rq_users.UpdateUser(
        callback.message.chat.id,
        callback.from_user.username,
        callback.from_user.first_name,
        callback.from_user.last_name,
        False,
        True,
        [role['role_id'] for role in user['roles']]
    )

    await callback.message.edit_text('✅ Успешно! Вы будете получать уведомления.',
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[GenButtonBack('profile')], [__BACK_IN_MAIN_MENU__]]))
