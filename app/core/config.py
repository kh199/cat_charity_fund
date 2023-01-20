import logging
from typing import Optional

from pydantic import BaseSettings, EmailStr

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'secret'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
