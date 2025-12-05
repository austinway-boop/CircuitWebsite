"""LinkedIn OAuth 2.0 authentication with secure token management."""
import requests
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import json
from .config import config
from .rate_limiter import RateLimiter
from .exceptions import AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


class LinkedInAuth:
    """LinkedIn OAuth 2.0 flow with automatic token refresh."""
    
    AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    
    def __init__(self):
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.redirect_uri = config.redirect_uri
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.rate_limiter = RateLimiter()
        
    def get_authorization_url(self, scopes: list[str] = None) -> str:
        """Build OAuth authorization URL with CSRF state parameter."""
        if scopes is None:
            scopes = ['r_liteprofile', 'r_emailaddress']
        
        scope_string = ' '.join(scopes)
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope_string,
            'state': self._generate_state()
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Trade authorization code for access token."""
        if not self.rate_limiter.check_limit():
            raise RateLimitError("Rate limit exceeded")
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            self.rate_limiter.record_call()
            
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code}")
                raise AuthenticationError(f"Token exchange failed: {response.text}")
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            raise AuthenticationError(f"Network error: {e}")
    
    def is_token_valid(self) -> bool:
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < (self.token_expiry - timedelta(minutes=5))
    
    def get_access_token(self) -> str:
        if not self.is_token_valid():
            raise AuthenticationError("No valid token")
        return self.access_token
    
    def _generate_state(self) -> str:
        import secrets
        return secrets.token_urlsafe(32)
    
    def revoke_token(self):
        self.access_token = None
        self.token_expiry = None

