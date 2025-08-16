from core.bot.command import add_commands
from core.bot.handler import add_handlers
from core.build import build
from core.logger import get_logger
from core.settings import settings
from telegram.ext import Application, ApplicationBuilder

logger = get_logger(__name__)


def run():
    """Run the application."""
    app: Application = (
        ApplicationBuilder()
        .token(settings.model_extra["TG_BOT_TOKEN"])
        .post_init(add_commands)
        .build()
    )
    add_handlers(app)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    build()
    run()
