import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# импорт Metdata и моделей, чтобы Alembic видел таблицы
from app.db.base import Base
from app.models.address import Address  # noqa
from app.models.request import Request  # noqa

config = context.config

# Берём sync-URL из окружения (или дефолт)
db_url_sync = os.getenv("DATABASE_URL_SYNC", "postgresql+psycopg://mixlab:password@db:5432/mixlabdb")
# Проставляем в конфиг именно sqlalchemy.url
config.set_main_option("sqlalchemy.url", db_url_sync)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",            # ВАЖНО: ищем sqlalchemy.url
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
