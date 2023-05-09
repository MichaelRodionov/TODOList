from django.core.management.base import BaseCommand

from bot.tg.bot_session import BotSession


# ----------------------------------------------------------------
# command class
class Command(BaseCommand):

    help = 'Run telegram bot'

    def handle(self, *args, **options) -> None:
        """Create session with bot and start bot"""
        bot = BotSession()
        bot.run_bot()
