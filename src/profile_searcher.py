"""
Profile Search Service
High-level service for searching LinkedIn profiles and extracting education data.
"""
import logging
from typing import Optional, Dict, Any, List
from .linkedin_client import LinkedInClient
from .auth import LinkedInAuth
from .validators import InputValidator
from .exceptions import ValidationError, SearchError, DataRetrievalError

logger = logging.getLogger(__name__)


class ProfileSearcher:
    """
    High-level service for LinkedIn profile searches.
    Coordinates authentication, search, and data extraction.
    """
    
    def __init__(self):
        """Initialize the profile searcher"""
        self.validator = InputValidator()
        self.auth: Optional[LinkedInAuth] = None
        self.client: Optional[LinkedInClient] = None
    
    def authenticate(self, auth: LinkedInAuth):
        """
        Set authenticated LinkedIn client.
        
        Args:
            auth: Authenticated LinkedInAuth instance
        """
        self.auth = auth
        self.client = LinkedInClient(auth)
        logger.info("Profile searcher authenticated")
    
    def search_person(
        self,
        name: str,
        age: int,
        location: Optional[str] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for a person by name, age, and location - get their profile link.
        
        Args:
            name: Person's full name
            age: Person's age
            location: Person's location (optional)
            max_results: Maximum number of results
            
        Returns:
            Dictionary with search results and profile links
        """
        if not self.client:
            raise SearchError("Not authenticated. Please authenticate first.")
        
        # Validate inputs
        name = self.validator.validate_name(name)
        age = self.validator.validate_age(age)
        max_results = self.validator.validate_search_limit(max_results)
        
        logger.info(f"Searching: {name}, {age} years old, location: {location}")
        
        try:
            # Search for people
            matches = self.client.search_people(name, age, location, max_results)
            
            return {
                'query': {
                    'name': name,
                    'age': age,
                    'location': location
                },
                'results_count': len(matches),
                'results': matches
            }
            
        except SearchError as e:
            logger.error(f"Search failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise SearchError(f"Search failed: {str(e)}")
    
    # Keep the old method name for compatibility
    def search_and_get_college(self, name: str, age: int, max_results: int = 10):
        """Legacy method - calls search_person"""
        return self.search_person(name, age, None, max_results)
    
    def get_my_college(self) -> List[str]:
        """
        Get colleges for the authenticated user.
        This IS available in standard LinkedIn API.
        
        Returns:
            List of college names
        """
        if not self.client:
            raise SearchError("Not authenticated. Please authenticate first.")
        
        try:
            education = self.client.get_my_education()
            
            colleges = []
            for edu in education:
                college = self.client.extract_college_name(edu)
                if college:
                    colleges.append(college)
            
            logger.info(f"Found {len(colleges)} colleges for authenticated user")
            return colleges
            
        except DataRetrievalError as e:
            logger.error(f"Failed to retrieve education: {str(e)}")
            raise

