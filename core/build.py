import time

from core.db.init import init_db
from core.settings import settings
from halo import Halo


def show_logo():
    """Show logo on startup."""
    logo = """
  ▄▄▄       ██▓ ██ ▄█▀ ▒█████  
 ▒████▄    ▓██▒ ██▄█▒ ▒██▒  ██▒
 ▒██  ▀█▄  ▒██▒▓███▄░ ▒██░  ██▒
 ░██▄▄▄▄██ ░██░▓██ █▄ ▒██   ██░
  ▓█   ▓██▒░██░▒██▒ █▄░ ████▓▒░
  ▒▒   ▓▒█░░▓  ▒ ▒▒ ▓▒░ ▒░▒░▒░ 
   ▒   ▒▒ ░ ▒ ░░ ░▒ ▒░  ░ ▒ ▒░ 
   ░   ▒    ▒ ░░ ░░ ░ ░ ░ ░ ▒  
       ░  ░ ▒ ░░  ░       ░ ░  
"""
    print(logo)
    time.sleep(0.1)


def check_env():
    """Check if all required environment variables are set."""
    vars = ("TG_BOT_TOKEN", "DATABASE_URI", "OPENAI_API_KEY")
    for var in vars:
        if var not in settings.model_extra:
            raise ValueError(f"Environment variable {var} is not set.")


def build():
    """Build the application."""
    with Halo(
        text=f"Building {settings.APP_TITLE}.{settings.APP_VERSION}...", spinner="dots"
    ) as spinner:
        try:
            check_env()
        except Exception:
            spinner.fail("Environment check failed.")
            raise

        spinner.start("Initializing database...")
        try:
            init_db()
            spinner.succeed("Database initialized.")
        except Exception:
            spinner.fail("Database initialization failed.")
            raise

        spinner.succeed(f"Build completed! Call Aiko at {settings.APP_URL}")

    show_logo()


if __name__ == "__main__":
    build()
