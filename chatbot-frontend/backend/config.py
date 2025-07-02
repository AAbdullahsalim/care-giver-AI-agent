import os
from typing import Optional

class Config:
    """Configuration settings for the application"""
    
    # API Keys
    GOOGLE_API_KEY: str = "AIzaSyCqnWZTKrOiFaHpidVF5oUeNz4k3joEVJ0"
    
    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # LangGraph Settings
    MAX_CONVERSATION_TURNS: int = 10
    MEMORY_TTL_HOURS: int = 24
    
    @classmethod
    def get_google_api_key(cls) -> str:
        """Get Google API key from environment or config"""
        return os.getenv("GOOGLE_API_KEY", cls.GOOGLE_API_KEY)
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.ENVIRONMENT == "development" 