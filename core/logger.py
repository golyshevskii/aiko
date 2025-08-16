import logging
import time


def get_logger(name: str, level: int | None = None) -> logging.Logger:
    """Get a custom logger."""
    if level is None:
        from core.settings import settings

        level = settings.LOG_LEVEL

    logger = logging.getLogger(name)
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s:%(lineno)d | %(levelname)s: %(message)s"
    )
    formatter.converter = time.gmtime

    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    return logger
