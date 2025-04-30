import logging
from .settings import settings

def setup_logging():
    """
    Sets up the logging configuration.
    """

    # set handler depending on whether is running in Docker or not
    handler = logging.StreamHandler() if settings.DOCKERIZED else logging.FileHandler("app.log")

    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[handler],
    )
    logger = logging.getLogger(__name__)
    return logger

LOG = setup_logging()
