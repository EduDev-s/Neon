import hashlib
from datetime import datetime
from platform import system, python_version, release

import psutil
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile
)

import utils
from other.config import config
import requests.roles as rq_roles
import requests.users as rq_users
from handlers.core import log, GetRouter
import requests.admin_panel as rq_admin_panel
from handlers.states.role_edit import FormRoleEdit
from handlers.states.newsletter import FormNewsletter
from handlers.states.role_create import FormRoleCreate
from other.PermissionsManager.PermissionsManager import PM
from keyboards.other import GenButtonBack, __BACK_IN_MAIN_MENU__
from keyboards.admins import GenAdminPanel, __NEWSLETTER_WARN__, GenRoleMenu, GenRoleOpen, GenRoleEdit, GenRoleEditUsers


router = GetRouter()


@router.callback_query(F.data == 'admin_panel')
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    log.warn(callback.message.chat.id, 'Admin logged into the panel . . .')

    await callback.message.edit_text('🛠Вы в админ-панели!\nБудьте осторожны‼️', reply_markup=await GenAdminPanel(callback.message.chat.id))

    await state.clear()


@router.callback_query(F.data == 'admin_panel:newsletter_input')
async def admin_panel_newsletter_input(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.newsletter:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await callback.message.edit_text('Введите текст рассылки')
    await state.set_state(FormNewsletter.input_text)


@router.message(F.text, FormNewsletter.input_text)
async def admin_panel_form_newsletter_input_text(message: Message, state: FSMContext):
    if not (await utils.GetPermissions(message.chat.id)).admin_panel.use.newsletter:
        try:
            await utils.RQReporter(m=message)
        except utils.AccessDeniedError:
            return

    await message.answer(f'<b>‼️ВЫ ТОЧНО ХОТИТЕ ОТПРАВИТЬ СООБЩЕНИЕ ВСЕМ ПОЛЬЗОВАТЕЛЯМ⁉️</b>\nТЕКСТ СООБЩЕНИЯ:\n{message.text}',
                         reply_markup=__NEWSLETTER_WARN__)

    await state.set_state(FormNewsletter.warn)
    await state.set_data({'text': message.text})


@router.callback_query(F.data == 'admin_panel:newsletter', FormNewsletter.warn)
async def admin_panel_newsletter(callback: CallbackQuery, state: FSMContext):

    if not (await utils.GetPermissions(callback.message.chat.id)).admin:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await callback.message.edit_text('✅ Рассылка началась!', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [GenButtonBack('admin_panel')],
        [__BACK_IN_MAIN_MENU__]
    ]))

    await utils.newsletter(callback.message.chat.id, str((await state.get_data())['text']), False, callback.message.bot)


@router.callback_query(F.data == 'admin_panel:status_server')
async def admin_panel_status_server(callback: CallbackQuery):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.server_status:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    log.info(callback.message.chat.id, 'Admin requested a server status report, generation . . .')

    log.debug(callback.message.chat.id, 'Generating information about: SystemName')
    SystemName = str(system())

    log.debug(callback.message.chat.id, 'Generating information about: SystemRelease')
    SystemRelease = str(release())

    log.debug(callback.message.chat.id, 'Generating information about: PythonVersion')
    PythonVersion = str(python_version())

    # Загруженость
    # CPU
    log.debug(callback.message.chat.id, 'Generating information about: CPU')
    CPU = psutil.cpu_percent(interval=1)

    # Memory
    log.debug(callback.message.chat.id, 'Generating information about: Memory, Memory_Swap')
    Memory = psutil.virtual_memory()
    Memory_Swap = psutil.swap_memory()

    # Disks
    log.debug(callback.message.chat.id, 'Generating information about: Disks')
    Disks = psutil.disk_usage('/')

    # Network
    log.debug(callback.message.chat.id, 'Generating information about: Network')
    all_interf = psutil.net_if_addrs()
    Network: str = '\n'

    for interf in all_interf:
        Network = f'{Network}- {interf}: {all_interf[interf][0][1]}\n'

    report = f'OS: {SystemName} {SystemRelease}\nPython: {PythonVersion}\n\nЗагруженость:\n\nCPU: {CPU}%\nMemory: {Memory.percent}%\nMemory Swap: {Memory_Swap.percent}%\nDisks: {Disks.percent}%\nNetwork: {Network}'

    log.info(callback.message.chat.id, 'Successfully !')

    await callback.message.edit_text(report, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[GenButtonBack('admin_panel')], [__BACK_IN_MAIN_MENU__]]))

    log.info(callback.message.chat.id, 'Report Sent !')


@router.callback_query(F.data == 'admin_panel:role')
async def admin_panel_role(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await state.clear()

    await callback.message.edit_text('👇 Выберите роль', reply_markup=(await GenRoleMenu(callback.message.chat.id)))


@router.callback_query(F.data.startswith('admin_panel:role:open:'))
async def admin_panel_role_open(callback: CallbackQuery):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role_id: int = int(callback.data.replace('admin_panel:role:open:', ''))
    role = await rq_roles.GetRole(callback.message.chat.id, role_id, 60)
    users = '' if role['users'] != [] else '❌'

    for user in role['users']:
        users += f'\'{user['first_name']}\'' + ' [ @' + str(user['username']) + (' ], ' if user['user_id'] != role['users'][-1]['user_id'] else ' ]')

    await callback.message.edit_text(f'ID роли: <code>{role['role_id']}</code>\nНазвание роли: {role['name']}\nПользователи с этой ролью: {users}\nРазрешения:\n{utils.get_permissions(role['permissions'])}', reply_markup=(await GenRoleOpen(role_id)))


@router.callback_query(F.data == 'admin_panel:role:create')
async def admin_panel_role_create(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await callback.message.edit_text(f'➡️ Введите ID роли которую хотите создать. ID - это уникальный индикатор роли. Занятые ID: {[role['role_id'] for role in (await rq_roles.GetRoles(callback.message.chat.id))]}',
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [GenButtonBack('admin_panel:role')],
                                         [__BACK_IN_MAIN_MENU__]
                                         ]
        ))

    await state.set_state(FormRoleCreate.input_id)


@router.message(F.text, FormRoleCreate.input_id)
async def admin_panel_role_create_input_id(message: Message, state: FSMContext):
    if not (await utils.GetPermissions(message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(m=message)
        except utils.AccessDeniedError:
            return

    if not message.text.isdigit() or len(message.text) > 5:
        await message.answer('‼️ Некорректные входные данные!\n\n➡️ Введите ID')

        await state.set_state(FormRoleCreate.input_id)

        return

    await state.set_data({
        'role_id': int(message.text)
    })

    await message.answer('✅ ID роли успешно сохранено!\n\n➡️ Введите название роли которую хотите создать. В названии можно использовать HTML тэги!',
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [GenButtonBack('admin_panel:role')],
                             [__BACK_IN_MAIN_MENU__]
                             ]))

    await state.set_state(FormRoleCreate.input_name)


@router.message(F.text, FormRoleCreate.input_name)
async def admin_panel_role_create_input_name(message: Message, state: FSMContext):
    if not (await utils.GetPermissions(message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(m=message)
        except utils.AccessDeniedError:
            return

    if len(message.text) > 255:
        message.answer('‼️ Некорректные входные данные!\n\n➡️ Введите название')

        state.set_state(FormRoleCreate.input_name)

        return

    await rq_roles.SetRole(
        message.chat.id,
        int((await state.get_data())['role_id']),
        [],
        str(message.text),
        PM.DefaultPermissions
    )

    await message.answer('✅ Роль успешно создана!', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'Перейти к роли [{(await state.get_data())['role_id']}] ➡️',
                                  callback_data=f'admin_panel:role:open:{(await state.get_data())['role_id']}')],
            [GenButtonBack('admin_panel:role')],
            [__BACK_IN_MAIN_MENU__]
        ]))

    await state.clear()


@router.callback_query(F.data.startswith('admin_panel:role:edit:') and F.data.split(':')[-1].isdigit())
async def admin_panel_role_edit(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role_id = int(callback.data.replace('admin_panel:role:edit:', ''))

    if role_id == config.ID_ROLE_OWNER and role_id == config.ID_ROLE_DEFAULT:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role = await rq_roles.GetRole(
        callback.message.chat.id,
        role_id,
        60
    )

    users = '' if role['users'] != [] else '❌'
    for user in role['users']:
        users += f'\'{user['first_name']}\'' + ' [ @' + str(user['username']) + ' ], ' if user['user_id'] != role['users'][-1]['user_id'] else ' ]'

    await callback.message.edit_text(
        f'‼️ Вы в редакторе роли \'{role['name']}\' [{role_id}]\n\nПользователи с этой ролью: {users}\nРазрешения:\n{utils.get_permissions(role['permissions'])}',
        reply_markup=await GenRoleEdit(role)
    )


@router.callback_query(F.data.startswith('admin_panel:role:edit:') and F.data.endswith(':name'))
async def admin_panel_role_edit_name(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role_id = int(callback.data.split(':')[-2])

    if role_id == config.ID_ROLE_OWNER and role_id == config.ID_ROLE_DEFAULT:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await callback.message.edit_text(
        f'➡️ Введите новое название для роли [{role_id}]',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [GenButtonBack(f'admin_panel:role:edit:{role_id}')],
            [__BACK_IN_MAIN_MENU__]
        ])
    )

    await state.set_state(FormRoleEdit.input_name)
    await state.set_data({
        'role_id': role_id
    })


@router.message(F.text, FormRoleEdit.input_name)
async def admin_panel_role_edit_name_input(message: Message, state: FSMContext):
    if not (await utils.GetPermissions(message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(m=message)
        except utils.AccessDeniedError:
            return

    if len(message.text) > 255:
        message.answer(f'‼️ Некорректные входные данные!\n\n➡️ Введите новое имя для роли [{(await state.get_data())['role_id']}]')

        state.set_state(FormRoleCreate.input_name)

        return

    role_id = int((await state.get_data())['role_id'])
    role = await rq_roles.GetRole(message.chat.id, role_id)

    await rq_roles.UpdateRole(
        message.chat.id,
        role_id,
        [user['user_id'] for user in role['users']],
        str(message.text),
        PM.JSONToClass(message.chat.id, {'permissions': role['permissions']})
    )

    await message.answer('✅ Роль успешно обновлена!', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [GenButtonBack(f'admin_panel:role:edit:{role_id}')],
            [__BACK_IN_MAIN_MENU__]
        ]))

    await state.clear()


@router.callback_query(F.data.startswith('admin_panel:role:edit:') and F.data.endswith(':users'))
async def admin_panel_role_edit_users_menu(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role_id = int(callback.data.split(':')[-2])

    if role_id == config.ID_ROLE_OWNER and role_id == config.ID_ROLE_DEFAULT:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role = await rq_roles.GetRole(callback.message.chat.id, role_id)

    await callback.message.edit_text(
        '➡️ Выберите действие',
        reply_markup=await GenRoleEditUsers(role)
    )

    await state.set_state(FormRoleEdit.edit_users)
    await state.set_data({
        'role_id': role_id
    })


@router.callback_query(F.data.endswith('delete'), FormRoleEdit.edit_users)
async def admin_panel_role_edit_users_delete(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role_id = int(callback.data.split(':')[-4])
    user_delete_id = int(callback.data.split(':')[-2])

    if role_id == config.ID_ROLE_OWNER and role_id == config.ID_ROLE_DEFAULT:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role = await rq_roles.GetRole(callback.message.chat.id, role_id)
    new_user_ids_list: list[int] = []

    for user in role['users']:
        if user['user_id'] != user_delete_id:
            new_user_ids_list.append(user['user_id'])

    await rq_roles.UpdateRole(
        callback.message.chat.id,
        role_id,
        new_user_ids_list,
        role['name'],
        PM.JSONToClass(callback.message.chat.id, {'permissions': role['permissions']})
    )

    try:
        await callback.bot.send_message(
            user_delete_id,
            f'⚠️ С вас снята роль \'{role['name']}\'',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]])
        )
    except (TelegramForbiddenError, TelegramBadRequest):
        log.warn(str(user_delete_id), f'User {user_delete_id} has blocked the bot!')

    role = await rq_roles.GetRole(callback.message.chat.id, role_id)

    await callback.message.edit_text(
        '➡️ Выберите действие',
        reply_markup=await GenRoleEditUsers(role)
    )

    await state.set_state(FormRoleEdit.edit_users)
    await state.set_data({
        'role_id': role_id
    })


@router.callback_query(F.data.endswith(':users:add'), FormRoleEdit.edit_users)
async def admin_panel_role_edit_users(callback: CallbackQuery, state: FSMContext):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    role_id = int(callback.data.split(':')[-3])

    if role_id == config.ID_ROLE_OWNER and role_id == config.ID_ROLE_DEFAULT:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await callback.message.edit_text(
        '➡️ Введите TelegramID или Username пользователя (Без \'@\')\n\n❗️ Этот пользователь должен пользоваться ботом',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [GenButtonBack(f'admin_panel:role:edit:{role_id}:users')],
            [__BACK_IN_MAIN_MENU__]
        ])
    )

    await state.set_state(FormRoleEdit.input_user_id_or_username)
    await state.set_data({
        'role_id': role_id
    })


@router.message(F.text, FormRoleEdit.input_user_id_or_username)
async def admin_panel_role_edit_users_input_user_id_or_username(message: Message, state: FSMContext):
    if not (await utils.GetPermissions(message.chat.id)).admin_panel.use.role:
        try:
            await utils.RQReporter(m=message)
        except utils.AccessDeniedError:
            return

    role_id = int((await state.get_data())['role_id'])

    if role_id == config.ID_ROLE_OWNER and role_id == config.ID_ROLE_DEFAULT:
        try:
            await utils.RQReporter(m=message)
        except utils.AccessDeniedError:
            return

    users = await rq_users.GetUsers(message.chat.id)
    isExists = False
    user_id = None

    for user in users:
        if str(user['user_id']) == str(message.text) or str(user['username']) == str(message.text):
            isExists = True
            user_id = user['user_id']

            break

    if not isExists:
        await message.answer(
            f'❌ Пользователь {message.text} не найден!\n\n➡️ Введите TelegramID или Username ещё раз',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [GenButtonBack(f'admin_panel:role:edit:{role_id}:users')],
                [__BACK_IN_MAIN_MENU__]
            ])
        )

        return

    role = await rq_roles.GetRole(message.chat.id, role_id)

    user_ids: list[int] = [user['user_id'] for user in role['users']]
    try:
        user_ids.remove(user_id)

        await message.answer(
            f'❌ У пользователя {message.text} уже есть эта роль!',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [GenButtonBack(f'admin_panel:role:edit:{role_id}:users')],
                [__BACK_IN_MAIN_MENU__]
            ])
        )

        await state.clear()

        return
    except ValueError:
        pass

    try:
        await message.bot.send_message(
            user_id,
            f'⚠️ Вам добавлена роль \'{role['name']}\'',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]])
        )
    except (TelegramForbiddenError, TelegramBadRequest):
        await message.answer(
            f'❌ Пользователь {message.text} заблокировал бота!',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [GenButtonBack(f'admin_panel:role:edit:{role_id}:users')],
                [__BACK_IN_MAIN_MENU__]
            ])
        )

        await state.clear()

        return

    user_ids = [user['user_id'] for user in role['users']]
    user_ids.append(user_id)

    await rq_roles.UpdateRole(
        message.chat.id,
        role_id,
        user_ids,
        role['name'],
        PM.JSONToClass(message.chat.id, {'permissions': role['permissions']})
    )

    await message.answer(
        f'✅ Пользователю \'{message.text}\' добавлена роль \'{role['name']}\'',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [GenButtonBack(f'admin_panel:role:edit:{role_id}:users')],
            [__BACK_IN_MAIN_MENU__]
        ])
    )


@router.callback_query(F.data == 'admin_panel:database_backup')
async def admin_panel_database_backup(callback: CallbackQuery):
    if not (await utils.GetPermissions(callback.message.chat.id)).admin_panel.use.database_backup:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await callback.message.edit_text(
        '⚙️ Начато резервное копирование базы данных',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[])
    )

    backup = await rq_admin_panel.CreateDatabaseBackup(callback.message.chat.id)

    bif = BufferedInputFile(backup, filename=f'B-DB!ENC-K!{callback.message.chat.id}!{datetime.now().strftime('%d.%m.%Y_%H-%M-%S')}.dump.enc')

    await callback.message.edit_text(
        '⚙️ Выгружаю бэкап',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[])
    )

    await callback.bot.send_chat_action(callback.message.chat.id, 'upload_document')

    await callback.bot.send_document(
        chat_id=callback.message.chat.id,
        document=bif,
        protect_content=True,
        caption=f'SHA256: {hashlib.sha256(backup).hexdigest()}\nMD5: {hashlib.md5(backup).hexdigest()}'
    )

    await callback.message.edit_text(
        '✅ Резервное копирование успешно завершено!',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]])
    )
