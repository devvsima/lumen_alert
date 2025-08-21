from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from database.connect import async_session
from database.services.tg_users import TgUser
from tgbot.business.alert_settings import AlertSettings
from tgbot.keyboards.inline.alert import alert_settings_ikb
from tgbot.routers import user_router as router
from utils.logging import logger


@router.message(Command("alert_settings"), StateFilter(None))
async def alert_settings_command(message: types.Message) -> None:
    """Показывает настройки уведомлений пользователя"""
    try:
        async with async_session() as session:
            user = await TgUser.get_by_id(session, message.from_user.id)

            if not user:
                await message.answer("❌ Пользователь не найден в базе данных.")
                return

            # Получаем настройки через новый класс
            settings = await AlertSettings.get_user_settings(session, message.from_user.id)

            settings_text = (
                "🔔 <b>Настройки уведомлений</b>\n\n"
                f"📥 Присоединение к каналу: {'✅' if settings['alert_on_join'] else '❌'}\n"
                f"📤 Покидание канала: {'✅' if settings['alert_on_leave'] else '❌'}\n"
                f"🔄 Переключение каналов: {'✅' if settings['alert_on_switch'] else '❌'}\n\n"
                f"🔔 Общие уведомления: {'✅' if user.is_alert else '❌'}\n\n"
                "💡 <i>Настройки сохраняются автоматически</i>"
            )

            # Создаем временный объект для клавиатуры
            class TempUser:
                def __init__(self, user, settings):
                    self.id = user.id
                    self.is_alert = user.is_alert
                    self.alert_on_join = settings['alert_on_join']
                    self.alert_on_leave = settings['alert_on_leave']
                    self.alert_on_switch = settings['alert_on_switch']

            temp_user = TempUser(user, settings)

            await message.answer(
                settings_text, reply_markup=alert_settings_ikb(temp_user), parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Error in alert_settings_command: {e}")
        await message.answer(f"❌ Ошибка при получении настроек: {str(e)}")


@router.callback_query(lambda c: c.data.startswith("toggle_join_"))
async def toggle_join_callback(callback: types.CallbackQuery):
    """Переключает настройку уведомлений о присоединении к каналу"""
    try:
        user_id = int(callback.data.split("_")[-1])

        # Проверяем, что пользователь может изменять только свои настройки
        if user_id != callback.from_user.id:
            await callback.answer("❌ Вы можете изменять только свои настройки!", show_alert=True)
            return

        async with async_session() as session:
            # Получаем пользователя и текущие настройки
            user = await TgUser.get_by_id(session, user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден!", show_alert=True)
                return

            current_settings = await AlertSettings.get_user_settings(session, user_id)
            current_value = current_settings['alert_on_join']
            new_value = not current_value
            
            logger.info(f"User {user_id}: changing alert_on_join from {current_value} to {new_value}")
            
            # Переключаем настройку
            success = await AlertSettings.update_user_settings(
                session, user_id, alert_on_join=new_value
            )
            
            if not success:
                await callback.answer("❌ Ошибка при обновлении настроек!", show_alert=True)
                return

            # Получаем обновленные настройки
            updated_settings = await AlertSettings.get_user_settings(session, user_id)
            actual_value = updated_settings['alert_on_join']
            
            logger.info(f"User {user_id}: actual value after update: {actual_value}")
            
            # Создаем временный объект пользователя для клавиатуры
            class TempUser:
                def __init__(self, user, settings):
                    self.id = user.id
                    self.is_alert = user.is_alert
                    self.alert_on_join = settings['alert_on_join']
                    self.alert_on_leave = settings['alert_on_leave']
                    self.alert_on_switch = settings['alert_on_switch']

            temp_user = TempUser(user, updated_settings)
            
            # Добавляем уникальный элемент - время и статус изменения
            import datetime
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            action = "включены" if actual_value else "выключены"

            settings_text = (
                "🔔 <b>Настройки уведомлений</b>\n\n"
                f"📥 Присоединение к каналу: {'✅' if updated_settings['alert_on_join'] else '❌'}\n"
                f"📤 Покидание канала: {'✅' if updated_settings['alert_on_leave'] else '❌'}\n"
                f"🔄 Переключение каналов: {'✅' if updated_settings['alert_on_switch'] else '❌'}\n\n"
                f"🔔 Общие уведомления: {'✅' if user.is_alert else '❌'}\n\n"
                f"🕐 Последнее действие: {current_time}\n"
                f"✨ Уведомления о присоединении {action}"
            )

            try:
                await callback.message.edit_text(
                    settings_text,
                    reply_markup=alert_settings_ikb(temp_user),
                    parse_mode="HTML"
                )
                await callback.answer(f"✅ Уведомления о присоединении {action}!")
            except Exception as edit_error:
                if "message is not modified" in str(edit_error).lower():
                    await callback.answer(f"✅ Уведомления о присоединении {action}!")
                else:
                    logger.error(f"Edit error: {edit_error}")
                    await callback.answer(f"✅ Уведомления о присоединении {action}!")

    except Exception as e:
        logger.error(f"Error in toggle_join_callback: {e}")
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("toggle_leave_"))
async def toggle_leave_callback(callback: types.CallbackQuery):
    """Переключает настройку уведомлений о покидании канала"""
    try:
        user_id = int(callback.data.split("_")[-1])

        if user_id != callback.from_user.id:
            await callback.answer("❌ Вы можете изменять только свои настройки!", show_alert=True)
            return

        async with async_session() as session:
            user = await TgUser.get_by_id(session, user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден!", show_alert=True)
                return

            current_value = getattr(user, 'alert_on_leave', False)
            new_value = not current_value

            success = await TgUser.update_alert_settings(
                session, user_id, alert_on_leave=new_value
            )
            
            if not success:
                await callback.answer("❌ Ошибка при обновлении настроек!", show_alert=True)
                return

            updated_user = await TgUser.get_by_id(session, user_id)
            
            import datetime
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            action = "включены" if new_value else "выключены"

            settings_text = (
                "🔔 <b>Настройки уведомлений</b>\n\n"
                f"📥 Присоединение к каналу: {'✅' if getattr(updated_user, 'alert_on_join', True) else '❌'}\n"
                f"📤 Покидание канала: {'✅' if getattr(updated_user, 'alert_on_leave', False) else '❌'}\n"
                f"🔄 Переключение каналов: {'✅' if getattr(updated_user, 'alert_on_switch', False) else '❌'}\n\n"
                f"🔔 Общие уведомления: {'✅' if updated_user.is_alert else '❌'}\n\n"
                f"🕐 Последнее действие: {current_time}\n"
                f"✨ Уведомления о покидании {action}"
            )

            try:
                await callback.message.edit_text(
                    settings_text,
                    reply_markup=alert_settings_ikb(updated_user),
                    parse_mode="HTML"
                )
                await callback.answer(f"✅ Уведомления о покидании {action}!")
            except Exception as edit_error:
                if "message is not modified" in str(edit_error).lower():
                    await callback.answer(f"✅ Уведомления о покидании {action}!")
                else:
                    await callback.message.answer(
                        settings_text,
                        reply_markup=alert_settings_ikb(updated_user),
                        parse_mode="HTML"
                    )
                    await callback.answer(f"✅ Уведомления о покидании {action}!")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("toggle_switch_"))
async def toggle_switch_callback(callback: types.CallbackQuery):
    """Переключает настройку уведомлений о переключении каналов"""
    try:
        user_id = int(callback.data.split("_")[-1])

        if user_id != callback.from_user.id:
            await callback.answer("❌ Вы можете изменять только свои настройки!", show_alert=True)
            return

        async with async_session() as session:
            user = await TgUser.get_by_id(session, user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден!", show_alert=True)
                return

            await TgUser.update_alert_settings(
                session, user_id, alert_on_switch=not user.alert_on_switch
            )

            updated_user = await TgUser.get_by_id(session, user_id)

            settings_text = (
                "🔔 <b>Настройки уведомлений</b>\n\n"
                f"📥 Присоединение к каналу: {'✅' if updated_user.alert_on_join else '❌'}\n"
                f"📤 Покидание канала: {'✅' if updated_user.alert_on_leave else '❌'}\n"
                f"🔄 Переключение каналов: {'✅' if updated_user.alert_on_switch else '❌'}\n\n"
                f"🔔 Общие уведомления: {'✅' if updated_user.is_alert else '❌'}"
            )

            await callback.message.edit_text(
                settings_text,
                reply_markup=alert_settings_ikb(updated_user),
                parse_mode="HTML"
            )
            await callback.answer("✅ Настройка обновлена!")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("toggle_all_"))
async def toggle_all_callback(callback: types.CallbackQuery):
    """Переключает общие уведомления"""
    try:
        user_id = int(callback.data.split("_")[-1])

        if user_id != callback.from_user.id:
            await callback.answer("❌ Вы можете изменять только свои настройки!", show_alert=True)
            return

        async with async_session() as session:
            user = await TgUser.get_by_id(session, user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден!", show_alert=True)
                return

            # Переключаем общую настройку
            new_is_alert = not user.is_alert
            await TgUser.update(session, user_id, is_alert=new_is_alert)

            updated_user = await TgUser.get_by_id(session, user_id)

            settings_text = (
                "🔔 <b>Настройки уведомлений</b>\n\n"
                f"📥 Присоединение к каналу: {'✅' if updated_user.alert_on_join else '❌'}\n"
                f"📤 Покидание канала: {'✅' if updated_user.alert_on_leave else '❌'}\n"
                f"🔄 Переключение каналов: {'✅' if updated_user.alert_on_switch else '❌'}\n\n"
                f"🔔 Общие уведомления: {'✅' if updated_user.is_alert else '❌'}"
            )

            await callback.message.edit_text(
                settings_text,
                reply_markup=alert_settings_ikb(updated_user),
                parse_mode="HTML"
            )
            await callback.answer("✅ Общие уведомления обновлены!")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("refresh_settings_"))
async def refresh_settings_callback(callback: types.CallbackQuery):
    """Обновляет отображение настроек"""
    try:
        user_id = int(callback.data.split("_")[-1])

        if user_id != callback.from_user.id:
            await callback.answer("❌ Вы можете просматривать только свои настройки!", show_alert=True)
            return

        async with async_session() as session:
            user = await TgUser.get_by_id(session, user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден!", show_alert=True)
                return

            import datetime
            current_time = datetime.datetime.now().strftime('%H:%M:%S')

            settings_text = (
                "🔔 <b>Настройки уведомлений</b>\n\n"
                f"📥 Присоединение к каналу: {'✅' if getattr(user, 'alert_on_join', True) else '❌'}\n"
                f"📤 Покидание канала: {'✅' if getattr(user, 'alert_on_leave', False) else '❌'}\n"
                f"🔄 Переключение каналов: {'✅' if getattr(user, 'alert_on_switch', False) else '❌'}\n\n"
                f"🔔 Общие уведомления: {'✅' if user.is_alert else '❌'}\n\n"
                f"🕐 Обновлено: {current_time}\n"
                "🔄 Настройки актуальны"
            )

            try:
                await callback.message.edit_text(
                    settings_text,
                    reply_markup=alert_settings_ikb(user),
                    parse_mode="HTML"
                )
                await callback.answer("🔄 Настройки обновлены!")
            except Exception as edit_error:
                if "message is not modified" in str(edit_error).lower():
                    await callback.answer("🔄 Настройки актуальны!")
                else:
                    await callback.message.answer(
                        settings_text,
                        reply_markup=alert_settings_ikb(user),
                        parse_mode="HTML"
                    )
                    await callback.answer("🔄 Настройки обновлены!")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
