import os
import re
from logging.config import fileConfig

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from alembic import context

load_dotenv(find_dotenv())

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    raise SyntaxError("Offline mode for Alembic is not supported!")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = os.getenv("DATABASE_URL")

    if url is None:
        raise ValueError("Could not find the DB url!")

    # Remove '+asyncpg' if found
    pattern = re.compile("(\+asyncpg)")
    if re.search(pattern, url):
        url = re.sub(pattern, "", url)

    engine = create_engine(url)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
