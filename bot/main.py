import asyncio


from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties


from other.config import config

import other.log.colors as colors
from other.log.logging import logging

import handlers.core as core

import handlers.menu
import handlers.start  # noqa: F401
import handlers.lessons  # noqa: F401
import handlers.profile  # noqa: F401
import handlers.schedule  # noqa: F401
import handlers.admin_panel  # noqa: F401
import handlers.update_lesson  # noqa: F401

from keyboards.other import __BACK_IN_MAIN_MENU__

from utils import NotificationAdmins


async def main() -> None:
    log = logging(Name='MAIN', Color=colors.green)

    bot: Bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher(storage=MemoryStorage())

    dp.include_router(core.GetRouter())

    log.info(user_id=None, msg='The bot is running !')
    await NotificationAdmins(f'⚠️ Бот запущен!\n\n⚙️ Release: {config.RELEASE}', bot, InlineKeyboardMarkup(inline_keyboard=[[__BACK_IN_MAIN_MENU__]]))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, polling_timeout=60)


if __name__ == '__main__':
    asyncio.run(main())
