import discord
from string import Formatter

from database.connect import async_session
from database.services.sources import DiscordSource
from dsbot.loader import dsbot
from tgbot.business.voice_update_dashboard import update_all_dashboards
from tgbot.loader import bot as telegram_bot


class ChannelAccessButton(discord.ui.Button):
    def __init__(self, guild_id: int, channel_id: int, name: str, enabled: bool):
        super().__init__(
            label=f"{'✅' if enabled else '🚫'} {name}",
            style=discord.ButtonStyle.success
            if enabled
            else discord.ButtonStyle.secondary,
            custom_id=f"channel_access:{guild_id}:{channel_id}",
        )
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.channel_name = name

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Только администратор сервера может изменять доступ к каналам.",
                ephemeral=True,
            )
            return

        async with async_session() as session:
            enabled = await DiscordSource.toggle_channel_access(
                session, self.guild_id, self.channel_id
            )

        if enabled is None:
            await interaction.response.send_message(
                "Канал больше не найден в базе данных.", ephemeral=True
            )
            return

        self.label = f"{'✅' if enabled else '🚫'} {self.channel_name}"
        self.style = (
            discord.ButtonStyle.success if enabled else discord.ButtonStyle.secondary
        )
        await interaction.response.edit_message(view=self.view)
        await update_all_dashboards()


class ChannelPageButton(discord.ui.Button):
    def __init__(self, direction: int, disabled: bool):
        super().__init__(
            label="⬅️ Назад" if direction < 0 else "Вперёд ➡️",
            style=discord.ButtonStyle.secondary,
            row=4,
            disabled=disabled,
        )
        self.direction = direction

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, ChannelAccessView):
            await interaction.response.send_message(
                "Не удалось обновить список каналов.", ephemeral=True
            )
            return
        view.page += self.direction
        view.render()
        await interaction.response.edit_message(view=view)


class ChannelAccessView(discord.ui.View):
    def __init__(self, guild_id: int, channels: list):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.channels = channels
        self.page = 0
        self.page_size = 20
        self.render()

    def render(self) -> None:
        self.clear_items()
        start = self.page * self.page_size
        end = start + self.page_size
        for channel in self.channels[start:end]:
            self.add_item(
                ChannelAccessButton(
                    guild_id=self.guild_id,
                    channel_id=channel.id,
                    name=channel.name,
                    enabled=channel.is_enabled,
                )
            )
        page_count = max(1, (len(self.channels) + self.page_size - 1) // self.page_size)
        self.add_item(ChannelPageButton(-1, self.page == 0))
        self.add_item(ChannelPageButton(1, self.page >= page_count - 1))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild is None or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Только администратор сервера может изменять доступ к каналам.",
                ephemeral=True,
            )
            return False
        return True


def _is_guild_admin(interaction: discord.Interaction) -> bool:
    return (
        interaction.guild is not None
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    )


@dsbot.tree.command(
    name="ignore-bots",
    description="Включить или выключить уведомления от Discord-ботов",
)
async def ignore_bots_command(interaction: discord.Interaction) -> None:
    if not _is_guild_admin(interaction):
        await interaction.response.send_message(
            "Эта команда доступна только администраторам Discord-сервера.",
            ephemeral=True,
        )
        return
    async with async_session() as session:
        settings = await DiscordSource.get_guild_settings(session, interaction.guild.id)
        if settings is None:
            await interaction.response.send_message("Настройки сервера ещё не готовы.", ephemeral=True)
            return
        updated = await DiscordSource.update_guild_settings(
            session, interaction.guild.id, ignore_bots=not settings.ignore_bots
        )
    state = "включено" if updated.ignore_bots else "выключено"
    await interaction.response.send_message(
        f"Игнорирование Discord-ботов {state}.", ephemeral=True
    )


class NotificationMessagesModal(discord.ui.Modal, title="Шаблоны уведомлений"):
    join = discord.ui.TextInput(label="Вход", max_length=500)
    leave = discord.ui.TextInput(label="Выход", max_length=500)
    switch = discord.ui.TextInput(label="Переход", max_length=500)

    def __init__(self, settings):
        super().__init__()
        self.join.default = settings.join_template
        self.leave.default = settings.leave_template
        self.switch.default = settings.switch_template

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not _is_guild_admin(interaction):
            await interaction.response.send_message(
                "Только администратор сервера может изменять шаблоны.",
                ephemeral=True,
            )
            return
        allowed_fields = {"user", "channel", "from_channel", "server"}
        for value in (self.join.value, self.leave.value, self.switch.value):
            fields = {field_name for _, field_name, _, _ in Formatter().parse(value) if field_name}
            if not fields.issubset(allowed_fields):
                await interaction.response.send_message(
                    "Используйте только переменные: {user}, {channel}, "
                    "{from_channel}, {server}.",
                    ephemeral=True,
                )
                return
        async with async_session() as session:
            await DiscordSource.update_guild_settings(
                session,
                interaction.guild.id,
                join_template=self.join.value,
                leave_template=self.leave.value,
                switch_template=self.switch.value,
            )
        await interaction.response.send_message("Шаблоны уведомлений сохранены.", ephemeral=True)


@dsbot.tree.command(
    name="notification-messages",
    description="Изменить шаблоны сообщений о голосовой активности",
)
async def notification_messages_command(interaction: discord.Interaction) -> None:
    if not _is_guild_admin(interaction):
        await interaction.response.send_message(
            "Эта команда доступна только администраторам Discord-сервера.",
            ephemeral=True,
        )
        return
    async with async_session() as session:
        settings = await DiscordSource.get_guild_settings(session, interaction.guild.id)
    if settings is None:
        await interaction.response.send_message("Настройки сервера ещё не готовы.", ephemeral=True)
        return
    await interaction.response.send_modal(NotificationMessagesModal(settings))


@dsbot.tree.command(
    name="notification-link",
    description="Получить ссылку для подписки на уведомления этого сервера",
)
async def notification_link_command(interaction: discord.Interaction) -> None:
    if not _is_guild_admin(interaction):
        await interaction.response.send_message(
            "Эта команда доступна только администраторам Discord-сервера.",
            ephemeral=True,
        )
        return
    bot_user = await telegram_bot.get_me()
    link = f"https://t.me/{bot_user.username}?start=guild_{interaction.guild.id}"
    await interaction.response.send_message(
        "Ссылка для подписки на уведомления этого сервера:\n"
        f"<{link}>\n\n"
        "Разместите её в описании или закреплённом сообщении Discord-сервера.",
        ephemeral=True,
    )


@dsbot.tree.command(
    name="notification-channels",
    description="Разрешить или запретить каналы для уведомлений",
)
async def notification_channels_command(interaction: discord.Interaction) -> None:
    if interaction.guild is None or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Эта команда доступна только администраторам Discord-сервера.",
            ephemeral=True,
        )
        return

    async with async_session() as session:
        voice_channels = [
            channel
            for channel in interaction.guild.channels
            if isinstance(channel, discord.VoiceChannel)
        ]
        await DiscordSource.sync_guild(
            session, interaction.guild.id, interaction.guild.name, voice_channels
        )
        channels = await DiscordSource.get_all_channels(session, interaction.guild.id)

    if not channels:
        await interaction.response.send_message(
            "На сервере пока нет голосовых каналов.", ephemeral=True
        )
        return

    await interaction.response.send_message(
        "Настройка каналов уведомлений.\n"
        "✅ — канал доступен для подписки и уведомлений.\n"
        "🚫 — уведомления из канала полностью запрещены.",
        view=ChannelAccessView(interaction.guild.id, channels),
        ephemeral=True,
    )
