from config import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from .models import Base
from utils.logger import logger

# Create async engine
engine = create_async_engine(
    f"mssql+aioodbc:///?odbc_connect={quote_plus(settings.DB_CONN_STR)}",
    pool_size=10,          # Increased from 5
    max_overflow=20,       # Increased from 10
    pool_timeout=60,       # Increased from 30
    pool_pre_ping=True,    # Add connection health check
    pool_recycle=3600      # Recycle connections after an hour
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Function to create tables
async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Function to get DB session
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
