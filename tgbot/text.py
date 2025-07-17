from tgbot.loader import _


class MessageText:
    @property
    def WELCOME(self):
        return _("""
👋, <a href='tg://user?id={user_id}'>{name}</a>

This is a Telegram bot for the Discord server <a href="{url}">Lumen</a>.
Notifications about activity in voice channels will be sent here 👀
""")

    @property
    def INFO(self):
        return _("Bot Info:")

    @property
    def INVITE_FRIENDS(self):
        return _(
            "Invited users: <b>{}</b>\n\nLink for friends:\n<code>https://t.me/{}?start={}</code>"
        )

    @property
    def ADMIN_WELCOME(self):
        return _("You're the administrator!")

    @property
    def CHANGE_LANG(self):
        return _("Select the language you want to switch to: 🌐")

    def DONE_CHANGE_LANG(self, language: str):
        return _("Your language has been successfully changed! ✅", locale=language)


message_text = MessageText()
