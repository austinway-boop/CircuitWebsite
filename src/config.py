"""App configuration from environment."""
import os
import logging

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.app_env = os.getenv('APP_ENV', 'development')
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'DEBUG')
    
    def is_production(self) -> bool:
        return self.app_env == 'production'


config = Config()
