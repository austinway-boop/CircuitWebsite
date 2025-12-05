"""
Custom Exceptions
Defines all custom exceptions for the application.
"""


class LinkedInAPIError(Exception):
    """Base exception for LinkedIn API errors"""
    pass


class AuthenticationError(LinkedInAPIError):
    """Raised when authentication fails"""
    pass


class RateLimitError(LinkedInAPIError):
    """Raised when rate limit is exceeded"""
    pass


class ValidationError(LinkedInAPIError):
    """Raised when input validation fails"""
    pass


class SearchError(LinkedInAPIError):
    """Raised when person search fails"""
    pass


class DataRetrievalError(LinkedInAPIError):
    """Raised when data retrieval fails"""
    pass

