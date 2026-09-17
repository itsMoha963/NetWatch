from sqlalchemy import URL, create_engine

from sqlalchemy.orm import sessionmaker

from app.core.config import Settings

settings = Settings()

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.postgres_user,
    password=settings.postgres_password.get_secret_value(),
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)

engine = create_engine(database_url)

session_factory = sessionmaker(bind=engine)
