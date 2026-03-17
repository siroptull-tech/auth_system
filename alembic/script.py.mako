from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
import logging

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    logger = logging.getLogger('alembic.env')
else:
    logger = logging.getLogger(__name__)
