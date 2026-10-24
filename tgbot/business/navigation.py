from aiogram import types


async def edit_navigation_message(
    message: types.Message,
    text: str,
    **kwargs,
) -> types.Message:
    if message.photo:
        return await message.edit_caption(caption=text, **kwargs)
    return await message.edit_text(text, **kwargs)
