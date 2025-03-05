from datetime import datetime
from time import strftime, localtime
from dateutil.relativedelta import relativedelta

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import BufferedInputFile

import utils
import requests.schedule as rq_schedule
from handlers.core import log, GetRouter
from keyboards.other import __BACK_IN_MAIN_MENU__
from handlers.states.update_lesson import FormUpdate
from keyboards.users import GenSchedule, __SCHEDULE_RECESS__
from keyboards.admins import __DELETE_SCHEDULE__, __UPDATE_HOMEWORK_AND_PHOTO__

router = GetRouter()


@router.callback_query(F.data == 'schedule')
async def schedule(callback: CallbackQuery):
    if not (await utils.GetPermissions(callback.message.chat.id)).schedule.use:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    schedule = await rq_schedule.GetSchedule(callback.message.chat.id)

    if schedule == FileNotFoundError:
        log.info(user_id=str(callback.message.chat.id), msg='Schedule not found!')

        await callback.answer(text='‼️ ERROR: FILE NOT FOUND ‼️', show_alert=True)

        await utils.NotificationAdmins(text='Расписание не найдено.\nПожалуйста добавьте расписание !', bot=callback.bot,
                                       reply_markup=InlineKeyboardMarkup(row_width=1, inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
    else:
        await callback.bot.send_chat_action(callback.message.chat.id, action='upload_photo')
        await callback.bot.send_photo(
                callback.message.chat.id,
                photo=BufferedInputFile(file=schedule['file'], filename='schedule.png'),
                reply_markup=await GenSchedule(callback.message.chat.id)
            )


@router.message(F.photo)
async def schedule_add_from_photo(message: Message, state: FSMContext) -> None:
    if not (await utils.GetPermissions(message.chat.id)).schedule.edit:
        await utils.RQReporter(m=message)

    file = await message.bot.get_file(message.photo[-1].file_id)
    downloaded_file = await message.bot.download_file(file.file_path)

    if message.caption is not None:
        await message.answer('👇 Выберете предмет по которому хотите заменить Д/З', reply_markup=__UPDATE_HOMEWORK_AND_PHOTO__)
        await state.set_state(FormUpdate.select_lesson)

        await state.set_data({
            'homework': message.caption,
            'file': downloaded_file.read()
            })

    else:
        await rq_schedule.UpdateSchedule(message.chat.id, downloaded_file.read())

        await message.answer('⚠ Активирована система уведомлений . . .', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
        await utils.newsletter(message.chat.id, '⚠ Обновлено расписание.', True, message.bot)


@router.message(F.document)
async def schedule_add_from_file(message: Message, state: FSMContext) -> None:
    if not (await utils.GetPermissions(message.chat.id)).schedule.edit:
        await utils.RQReporter(m=message)

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

    if message.caption is not None:
        await message.answer('👇 Выберете предмет по которому хотите заменить Д/З', reply_markup=__UPDATE_HOMEWORK_AND_PHOTO__)
        await state.set_state(FormUpdate.select_lesson)

        await state.set_data({
            'homework': message.caption,
            'file': downloaded_file.read()
            })

        downloaded_file.close()
    else:
        await rq_schedule.UpdateSchedule(message.chat.id, downloaded_file.read())

        await message.answer('⚠ Активирована система уведомлений . . .', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
        await utils.newsletter(message.chat.id, '⚠ Обновлено расписание.', True, message.bot)


@router.callback_query(F.data.startswith('schedule:recess'))
async def schedule_recess(callback: CallbackQuery):
    if not (await utils.GetPermissions(callback.message.chat.id)).schedule_call.use:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    lessons: list[dict[str, str]] = await rq_schedule.GetScheduleCall(callback.message.chat.id)

    text: str = ''
    i: int = 0

    for lesson in lessons['schedule_call']:
        i += 1
        text += f'Урок {i}: {str(lesson['start_time']).replace('_', ':')} - {str(lesson['end_time']).replace('_', ':')}\n'

    current_time = float(strftime('%H.%M', localtime()))
    log.info(str(callback.message.chat.id), f'Current time: {current_time}')

    status, time_to_end = await utils.GetTimeToLesson(lessons['schedule_call'], current_time)

    try:
        if status == -1:
            await callback.message.edit_text(f'{text}\n\nБольше уроков на сегодня нет.', reply_markup=__SCHEDULE_RECESS__)
        else:
            if status == 0:
                status_text = 'урока'
            elif status == 1:
                status_text = 'перемены'
            else:
                status_text = 'ERROR'

            await callback.message.edit_text(f'{text}\n\nДо конца {status_text} осталось {time_to_end:.0f} минут', reply_markup=__SCHEDULE_RECESS__)
    except utils.TelegramBadRequest:
        await callback.answer("🔄 Обновлено")


@router.callback_query(F.data.startswith('schedule:exam'))
async def schedule_exam(callback: CallbackQuery):
    if not (await utils.GetPermissions(callback.message.chat.id)).schedule_exam.use:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    def format_output(name: str, target_date: datetime, current_date: datetime):
        delta = relativedelta(target_date, current_date)
        months = delta.years * 12 + delta.months
        days = delta.days
        formatted_date = target_date.strftime("%d.%m.%Y")
        return f"<b>{name}</b> осталось: {months} месяца {days} дня ({formatted_date})"

    schedule_exam: list[dict[str, datetime]] = (await rq_schedule.GetScheduleExam(callback.message.chat.id))['schedule_exam']

    current_date = datetime.now()
    text: str = ''
    log.debug(callback.message.chat.id, f'Current date: {current_date}')

    for item in schedule_exam:
        for name, date_str in item.items():
            format_text = format_output(name, datetime.strptime(date_str, "%Y:%m:%d"), current_date)
            log.debug(callback.message.chat.id, f'Text: {format_text}')
            text = text + format_text + '\n'

    await callback.message.edit_text(text,
        reply_markup=InlineKeyboardMarkup(row_width=1, inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))


@router.callback_query(F.data.startswith('schedule:nftadmins'))
async def schedule_nftadmins(callback: CallbackQuery) -> None:
    if not (await utils.GetPermissions(callback.message.chat.id)).schedule.use:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await utils.NotificationAdmins(
        f'⚠️ Пользователь: @{callback.from_user.username} [{callback.message.chat.id}] уведомил вас в неактуальности расписания',
        callback.message.bot,
        InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]])
    )

    await callback.message.answer('✅ Отчёт отправлен. Извините за неудобства.',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))


@router.callback_query(F.data.startswith('schedule:delete_warn'))
async def schedule_delete_warn(callback: CallbackQuery) -> None:

    if not (await utils.GetPermissions(callback.message.chat.id)).schedule.edit:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    await callback.message.answer(text='⚠ Вы уверены ?', reply_markup=__DELETE_SCHEDULE__)


@router.callback_query(F.data.startswith('schedule:delete'))
async def schedule_delete(callback: CallbackQuery) -> None:
    if not (await utils.GetPermissions(callback.message.chat.id)).schedule.edit:
        try:
            await utils.RQReporter(c=callback)
        except utils.AccessDeniedError:
            return

    if (await rq_schedule.GetSchedule(callback.message.chat.id)) == FileNotFoundError:
        await callback.answer(text='Ошибка: файл не найден.', show_alert=True)
    else:
        await rq_schedule.UpdateSchedule(callback.message.chat.id)
        await callback.message.edit_text('✅ Успешно !', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))
