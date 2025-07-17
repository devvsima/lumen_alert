from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from database.models import TgUserModel
from database.services import TgUser
from tgbot.filters.kb_filter import LangCallback
from tgbot.handlers.msg_text import msg_text
from tgbot.keyboards.inline.lang import lang_ikb
from tgbot.routers import user_router as router


@router.message(StateFilter(None), Command("language"))
@router.message(StateFilter(None), Command("lang"))
async def _lang(message: types.Message) -> None:
    """Отображает список доступных языков и позволяет выбрать предпочтительный"""
    await message.answer(msg_text.CHANGE_LANG, reply_markup=lang_ikb())


@router.callback_query(StateFilter(None), LangCallback.filter())
async def _change_lang(
    callback: types.CallbackQuery, callback_data: LangCallback, user: TgUserModel, session
) -> None:
    """Обрабатывает выбранный пользователем язык, и устанавливает его"""
    language = callback_data.lang
    await TgUser.update(
        session=session,
        id=user.id,
        language=language,
    )
    await callback.message.edit_text(msg_text.DONE_CHANGE_LANG(language))
