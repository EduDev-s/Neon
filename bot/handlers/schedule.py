import aiofiles
from datetime import datetime
from time import strftime, localtime

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import BufferedInputFile

from config import config
import database.requests as rq
from keyboards.users import GenSchedule
from handlers.core import log, GetRouter
from keyboards.other import __BACK_IN_MAIN_MENU__
from handlers.states.update_lesson import FormUpdate
from keyboards.admins import __DELETE_SCHEDULE__, __UPDATE_HOMEWORK_AND_PHOTO__
from utils import CheckForAdmin, RQReporter, NotificationAdmins, newsletter, GetTimeToLesson


router = GetRouter()


@router.callback_query(F.data == 'schedule')
async def schedule(callback: CallbackQuery):
    log.info(str(callback.message.chat.id), msg=f'Received \'[{callback.data}]\'')

    schedule = await rq.GetSchedule(callback.message.chat.id)

    if schedule == FileNotFoundError:
        log.info(user_id=str(callback.message.chat.id), msg='Schedule not found!')
    
        await callback.answer(text='‼️ ERROR: FILE NOT FOUND ‼️', show_alert=True)

        await NotificationAdmins(text='Расписание не найдено.\nПожалуйста добавьте расписание !', bot=callback.bot,
            reply_markup=InlineKeyboardMarkup(row_width=1, inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
    else:
        await callback.bot.send_chat_action(callback.message.chat.id, action='upload_photo')
        await callback.bot.send_photo(
                callback.message.chat.id,
                photo=BufferedInputFile(file=schedule.photo, filename='schedule.png'),
                reply_markup=await GenSchedule(callback.message.chat.id)
            )


@router.message(F.photo)
async def schedule_add_from_photo(message: Message, state: FSMContext) -> None:
    if await CheckForAdmin(message.chat.id):
        file = await message.bot.get_file(message.photo[-1].file_id)
        downloaded_file = await message.bot.download_file(file.file_path)

        if message.caption != None:
            await message.answer('👇 Выберете предмет по которому хотите заменить Д/З', reply_markup=__UPDATE_HOMEWORK_AND_PHOTO__)
            await state.set_state(FormUpdate.select_lesson)

            await state.set_data({
                'homework': message.caption,
                'photo': downloaded_file.read()
                })
            
            downloaded_file.close()

        else:
            await rq.UpdateSchedule(message.chat.id, downloaded_file.read())

            await message.answer('⚠ Активирована система уведомлений . . .', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
            await newsletter(message.chat.id, '⚠ Обновлено расписание.', True, message.bot)


@router.message(F.document)
async def schedule_add_from_file(message: Message, state: FSMContext) -> None:
    if await CheckForAdmin(message.chat.id):
        if not message.document.thumbnail.file_size * 0.000001 <= 1:
            await message.answer('❌ Файл слишком большой! Максимальный размер 1Mb!',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
            return

        if message.document.mime_type != 'image/jpeg' and message.document.mime_type != 'image/png':
            await message.answer('❌ Неподдерживаемый формат! Отправляйте фото в формате jpeg / jpg / png',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
            return

        file = await message.bot.get_file(message.document.file_id)
        downloaded_file = await message.bot.download_file(file.file_path)

        if message.caption != None:
            await message.answer('👇 Выберете предмет по которому хотите заменить Д/З', reply_markup=__UPDATE_HOMEWORK_AND_PHOTO__)
            await state.set_state(FormUpdate.select_lesson)


            await state.set_data({
                'homework': message.caption,
                'photo': downloaded_file.read()
                })
            
            downloaded_file.close()
        else:
            await rq.UpdateSchedule(message.chat.id, downloaded_file.read())

            await message.answer('⚠ Активирована система уведомлений . . .', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
            await newsletter(message.chat.id, '⚠ Обновлено расписание.', True, message.bot)


@router.callback_query(F.data.startswith('schedule:recess'))
async def schedule_recess(callback: CallbackQuery):
    log.info(str(callback.message.chat.id), msg=f'Received \'[{callback.data}]\'')

    if datetime.isoweekday(datetime.now()) < 5 or datetime.isoweekday(datetime.now()) > 5:
        lessons = [
                {'start_time': '8.00', 'end_time': '8.45'},
                {'start_time': '8.55', 'end_time': '9.40'},
                {'start_time': '10.00', 'end_time': '10.45'},
                {'start_time': '11.05', 'end_time': '11.45'},
                {'start_time': '11.55', 'end_time': '12.35'},
                {'start_time': '12.45', 'end_time': '13.25'},
                {'start_time': '13.30', 'end_time': '14.10'},
                {'start_time': '14.15', 'end_time': '14.55'}
            ]
        
        text: str = ''
        i: int = 0

        for lesson in lessons:
            i += 1
            text += f'Урок {i}: {str(lesson['start_time']).replace('_', ':')} - {str(lesson['end_time']).replace('_', ':')}\n'
    elif datetime.isoweekday(datetime.now()) == 5:
        lessons = [
            {'start_time': '8.00', 'end_time': '8.45'},
            {'start_time': '8.55', 'end_time': '9.40'},
            {'start_time': '10.00', 'end_time': '10.45'},
            {'start_time': '11.05', 'end_time': '11.45'},
            {'start_time': '11.55', 'end_time': '12.35'},
            {'start_time': '12.45', 'end_time': '13.25'},
            {'start_time': '13.30', 'end_time': '14.10'},
            {'start_time': '14.15', 'end_time': '14.55'}
        ]

        text: str = '⚠️ Расписание на пятницу\n'
        i: int = 0

        for lesson in lessons:
            i += 1
            text += f'Урок {i}: {str(lesson['start_time']).replace('.', ':')} - {str(lesson['end_time']).replace('.', ':')}\n'

    current_time = float(strftime('%H.%M', localtime()))
    log.info(str(callback.message.chat.id), f'Current time: {current_time}')

    status, time_to_end = await GetTimeToLesson(lessons, current_time)

    if status == -1:
        await callback.message.edit_text(f'{text}\n\nБольше уроков на сегодня нет.',
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
    else:
        if status == 0: status_text = 'урока'
        elif status == 1: status_text = 'перемены'
        else: status_text = 'ERROR'

        await callback.message.edit_text(f'{text}\n\nДо конца {status_text} осталось {time_to_end:.0f} минут', 
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))


@router.callback_query(F.data.startswith('schedule:nftadmins'))
async def schedule_delete_warn(callback: CallbackQuery) -> None:
    log.info(str(callback.message.chat.id), msg=f'Received \'[{callback.data}]\'')

    if not await CheckForAdmin(callback.message.chat.id):
        user = await rq.GetUser(callback.message.chat.id, callback.message.chat.id)

        await NotificationAdmins(
            f'⚠️ Пользователь: {user.username} [{user.user_id}] уведомил вас в неактуальности расписания',
            callback.message.bot,
            InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]])
        )

        await callback.message.answer('✅ Отчёт отправлен. Извините за неудобства.',
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
    else: await RQReporter(callback)


@router.callback_query(F.data.startswith('schedule:delete_warn'))
async def schedule_delete_warn(callback: CallbackQuery) -> None:
    log.info(str(callback.message.chat.id), msg=f'Received \'[{callback.data}]\'')
    
    if await CheckForAdmin(callback.message.chat.id): await callback.message.answer(text='⚠ Вы уверены ?', reply_markup=__DELETE_SCHEDULE__)
    else: await RQReporter(callback)


@router.callback_query(F.data.startswith('schedule:delete'))
async def schedule_delete(callback: CallbackQuery) -> None:
    log.info(str(callback.message.chat.id), msg=f'Received \'[{callback.data}]\'')

    if await CheckForAdmin(callback.message.chat.id):
        if (await rq.GetSchedule(callback.message.chat.id)).photo != None:
            await rq.UpdateSchedule(callback.message.chat.id, None)
            await callback.message.edit_text('✅ Успешно !', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
        else: await callback.answer(text='Ошибка: файл не найден.', show_alert=True)
    else: RQReporter(callback)
