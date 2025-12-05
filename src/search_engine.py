"""
LinkedIn Profile Search Engine
Uses DeepSeek AI to find comprehensive information about people.
"""
import logging
from typing import List, Dict, Any, Optional
from .validators import InputValidator
from .rate_limiter import RateLimiter
from .ai_search import DeepSeekSearcher

logger = logging.getLogger(__name__)

# DeepSeek API Key
DEEPSEEK_API_KEY = "sk-d7ccebc4335b4e11a7f8f14dd191e7c5"


class LinkedInSearchEngine:
    """
    Search for LinkedIn profiles and person information using DeepSeek AI.
    """
    
    def __init__(self):
        self.validator = InputValidator()
        self.rate_limiter = RateLimiter()
        self.ai_searcher = DeepSeekSearcher(DEEPSEEK_API_KEY)
    
    def search_linkedin_profile(
        self,
        name: str,
        age: Optional[int] = None,
        location: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for LinkedIn profiles using DeepSeek AI.
        
        Args:
            name: Person's name
            age: Person's age (used to estimate graduation year)
            location: Person's location
            limit: Maximum results
            
        Returns:
            List of potential LinkedIn profile matches with comprehensive info
        """
        # Validate inputs
        name = self.validator.validate_name(name)
        if age:
            age = self.validator.validate_age(age)
        
        logger.info(f"AI Searching for: {name}, age: {age}, location: {location}")
        
        # Use AI to search for the person
        ai_result = self.ai_searcher.search_person(name, age, location)
        
        # Return the results
        return ai_result.get('results', [])
    
    def get_search_metadata(
        self,
        name: str,
        age: Optional[int] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get full search results including metadata.
        
        Returns complete AI response with confidence levels and alternatives.
        """
        name = self.validator.validate_name(name)
        if age:
            age = self.validator.validate_age(age)
        
        return self.ai_searcher.search_person(name, age, location)
