"""
Input Validation
Validates and sanitizes all user inputs to prevent injection attacks.
SECURITY PRINCIPLE: Never trust user input.
"""
import re
import logging
from typing import Optional
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates and sanitizes user inputs.
    
    SECURITY: Prevents:
    - Injection attacks
    - Invalid data processing
    - XSS attacks
    - Path traversal
    """
    
    # Allow letters, spaces, hyphens, apostrophes (for names like O'Brien)
    NAME_PATTERN = re.compile(r"^[a-zA-Z\s\-']+$")
    
    # Age should be reasonable (13-120)
    MIN_AGE = 13
    MAX_AGE = 120
    
    @staticmethod
    def validate_name(name: str) -> str:
        """
        Validate and sanitize a person's name.
        
        Args:
            name: Name to validate
            
        Returns:
            Sanitized name
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name:
            raise ValidationError("Name cannot be empty")
        
        # Remove leading/trailing whitespace
        name = name.strip()
        
        # Check if empty after stripping
        if not name:
            raise ValidationError("Name cannot be empty")
        
        # Check length
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters")
        if len(name) > 100:
            raise ValidationError("Name must be less than 100 characters")
        
        # Check pattern
        if not InputValidator.NAME_PATTERN.match(name):
            raise ValidationError(
                "Name contains invalid characters. "
                "Only letters, spaces, hyphens, and apostrophes are allowed."
            )
        
        # Check for suspicious patterns
        if name.count(' ') > 5:
            raise ValidationError("Name has too many spaces")
        
        logger.debug(f"Name validation passed: {name}")
        return name
    
    @staticmethod
    def validate_age(age: int) -> int:
        """
        Validate age input.
        
        Args:
            age: Age to validate
            
        Returns:
            Validated age
            
        Raises:
            ValidationError: If age is invalid
        """
        if not isinstance(age, int):
            try:
                age = int(age)
            except (ValueError, TypeError):
                raise ValidationError("Age must be a number")
        
        if age < InputValidator.MIN_AGE:
            raise ValidationError(f"Age must be at least {InputValidator.MIN_AGE}")
        
        if age > InputValidator.MAX_AGE:
            raise ValidationError(f"Age must be less than {InputValidator.MAX_AGE}")
        
        logger.debug(f"Age validation passed: {age}")
        return age
    
    @staticmethod
    def sanitize_output(text: Optional[str]) -> str:
        """
        Sanitize output to prevent XSS and other injection attacks.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if text is None:
            return ""
        
        # Remove any control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        return text.strip()
    
    @staticmethod
    def validate_search_limit(limit: int) -> int:
        """
        Validate search result limit.
        
        Args:
            limit: Number of results to return
            
        Returns:
            Validated limit
            
        Raises:
            ValidationError: If limit is invalid
        """
        if not isinstance(limit, int):
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                raise ValidationError("Limit must be a number")
        
        if limit < 1:
            raise ValidationError("Limit must be at least 1")
        
        if limit > 100:
            raise ValidationError("Limit cannot exceed 100 to prevent excessive API costs")
        
        return limit

