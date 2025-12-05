"""
LinkedIn API Client
Handles all interactions with LinkedIn API including people search and profile data.
"""
import requests
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from .auth import LinkedInAuth
from .exceptions import SearchError, DataRetrievalError, RateLimitError
from .validators import InputValidator
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class LinkedInClient:
    """
    LinkedIn API client with rate limiting and error handling.
    """
    
    # LinkedIn API v2 base URL
    API_BASE = "https://api.linkedin.com/v2"
    
    def __init__(self, auth: LinkedInAuth):
        """
        Initialize LinkedIn client.
        
        Args:
            auth: Authenticated LinkedIn auth instance
        """
        self.auth = auth
        self.rate_limiter = RateLimiter()
        self.validator = InputValidator()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to LinkedIn API with rate limiting.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            
        Returns:
            API response data
            
        Raises:
            RateLimitError: If rate limit exceeded
            DataRetrievalError: If request fails
        """
        # Check and record rate limit
        if not self.rate_limiter.check_limit():
            raise RateLimitError("Rate limit exceeded. Please wait before making more requests.")
        
        self.rate_limiter.record_call()
        
        # Get access token
        token = self.auth.get_access_token()
        
        # Prepare request
        url = f"{self.API_BASE}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            logger.info(f"Making {method} request to {endpoint}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            
            if response.status_code == 429:
                raise RateLimitError("LinkedIn API rate limit exceeded")
            
            if response.status_code >= 400:
                logger.error(f"API error {response.status_code}: {response.text}")
                raise DataRetrievalError(
                    f"API request failed with status {response.status_code}: {response.text}"
                )
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            raise DataRetrievalError(f"Network error: {str(e)}")
    
    def get_my_profile(self) -> Dict[str, Any]:
        """
        Get the authenticated user's profile.
        This is available in the standard LinkedIn API.
        
        Returns:
            User profile data
        """
        try:
            profile = self._make_request('GET', '/me')
            logger.info("Successfully retrieved user profile")
            return profile
        except Exception as e:
            logger.error(f"Failed to retrieve profile: {str(e)}")
            raise DataRetrievalError(f"Failed to retrieve profile: {str(e)}")
    
    def search_people(
        self,
        name: str,
        age: Optional[int] = None,
        location: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for people by name, age, and location - return their profile links.
        
        Args:
            name: Person's name to search for
            age: Person's age (optional)
            location: Person's location (optional)
            limit: Maximum results to return
            
        Returns:
            List of matches with name and profile URL
        """
        # Validate inputs
        name = self.validator.validate_name(name)
        if age is not None:
            age = self.validator.validate_age(age)
        limit = self.validator.validate_search_limit(limit)
        
        logger.info(f"Searching: {name}, age: {age}, location: {location}")
        
        try:
            # Build search parameters
            params = {
                'keywords': name,
                'count': limit,
                'start': 0
            }
            
            if location:
                params['location'] = location
            
            # Try different API endpoints
            endpoints = [
                'people-search',
                'peopleSearch', 
                'people',
                'search/people',
            ]
            
            results = []
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = self._make_request('GET', endpoint, params=params)
                    
                    # Extract results from response
                    if 'elements' in response:
                        results = response['elements']
                        break
                    elif 'people' in response:
                        results = response['people']
                        break
                    elif isinstance(response, list):
                        results = response
                        break
                        
                except DataRetrievalError as e:
                    logger.debug(f"{endpoint} failed: {str(e)}")
                    continue
            
            if not results:
                logger.warning("No results found - API may not support people search")
                return []
            
            # Return simple list with name and profile link
            matches = []
            for person in results[:limit]:
                profile_url = (
                    person.get('publicProfileUrl') or 
                    person.get('profile_url') or
                    person.get('url') or
                    f"https://linkedin.com/in/{person.get('vanityName', '')}" if person.get('vanityName') else ''
                )
                
                matches.append({
                    'name': self._extract_name(person),
                    'profile_url': profile_url,
                    'location': person.get('location', {}).get('name', '') if isinstance(person.get('location'), dict) else person.get('location', ''),
                    'headline': person.get('headline', ''),
                })
            
            logger.info(f"Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise SearchError(f"Search failed: {str(e)}")
    
    def _extract_name(self, person_data: Dict[str, Any]) -> str:
        """Extract person's name from various possible structures"""
        # Try different name structures
        if 'name' in person_data:
            return person_data['name']
        
        if 'firstName' in person_data and 'lastName' in person_data:
            first = person_data.get('firstName', '')
            last = person_data.get('lastName', '')
            return f"{first} {last}".strip()
        
        if 'localizedFirstName' in person_data and 'localizedLastName' in person_data:
            first = person_data.get('localizedFirstName', '')
            last = person_data.get('localizedLastName', '')
            return f"{first} {last}".strip()
        
        return 'Unknown'
    
    def get_person_education(self, person_id: str) -> List[Dict[str, Any]]:
        """
        Get education information for a person.
        
        Args:
            person_id: LinkedIn person ID or 'me' for authenticated user
            
        Returns:
            List of education entries
            
        Raises:
            DataRetrievalError: If retrieval fails
        """
        try:
            # Try different endpoint formats
            endpoints = [
                f'people/{person_id}/educations',
                f'people/{person_id}/education',
                f'v2/people/{person_id}/educations',
                f'people/{person_id}?projection=(education)',
            ]
            
            for endpoint in endpoints:
                try:
                    logger.debug(f"Trying education endpoint: {endpoint}")
                    education = self._make_request('GET', endpoint)
                    
                    # Handle different response structures
                    if 'elements' in education:
                        logger.info(f"Retrieved {len(education['elements'])} education entries for {person_id}")
                        return education['elements']
                    elif 'education' in education:
                        logger.info(f"Retrieved education data for {person_id}")
                        return education['education'] if isinstance(education['education'], list) else [education['education']]
                    elif isinstance(education, list):
                        logger.info(f"Retrieved {len(education)} education entries for {person_id}")
                        return education
                        
                except DataRetrievalError as e:
                    logger.debug(f"Endpoint {endpoint} failed: {str(e)}")
                    continue
            
            # If we get here, all endpoints failed
            logger.warning(f"Could not retrieve education data for {person_id}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve education: {str(e)}")
            raise DataRetrievalError(f"Failed to retrieve education data: {str(e)}")
    
    def get_my_education(self) -> List[Dict[str, Any]]:
        """
        Get education information for the authenticated user.
        This IS available in standard LinkedIn API.
        
        Returns:
            List of education entries with college information
        """
        return self.get_person_education('me')
    
    def extract_college_name(self, education_entry: Dict[str, Any]) -> Optional[str]:
        """
        Extract college/university name from education entry.
        
        Args:
            education_entry: Education data from LinkedIn API
            
        Returns:
            College name or None
        """
        # LinkedIn API structure for education varies
        # Common fields: schoolName, school.name, etc.
        
        if 'schoolName' in education_entry:
            return self.validator.sanitize_output(education_entry['schoolName'])
        
        if 'school' in education_entry:
            school = education_entry['school']
            if isinstance(school, dict) and 'name' in school:
                return self.validator.sanitize_output(school['name'])
        
        return None

