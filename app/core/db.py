from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.database_url)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # noqa

Base = declarative_base()
