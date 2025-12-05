"""
Tests for authentication.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.auth import LinkedInAuth
from src.exceptions import AuthenticationError


class TestLinkedInAuth:
    """Test LinkedIn authentication"""
    
    def test_initialization(self):
        """Test that auth initializes correctly"""
        auth = LinkedInAuth()
        
        assert auth.access_token is None
        assert auth.token_expiry is None
        assert auth.client_id is not None
        assert auth.client_secret is not None
    
    def test_get_authorization_url(self):
        """Test authorization URL generation"""
        auth = LinkedInAuth()
        
        url = auth.get_authorization_url()
        
        assert "https://www.linkedin.com/oauth/v2/authorization" in url
        assert "client_id" in url
        assert "redirect_uri" in url
        assert "scope" in url
        assert "state" in url
    
    def test_get_authorization_url_with_scopes(self):
        """Test authorization URL with custom scopes"""
        auth = LinkedInAuth()
        
        scopes = ['r_liteprofile', 'r_emailaddress', 'w_member_social']
        url = auth.get_authorization_url(scopes)
        
        assert "r_liteprofile" in url
        assert "r_emailaddress" in url
        assert "w_member_social" in url
    
    def test_is_token_valid_no_token(self):
        """Test token validation when no token exists"""
        auth = LinkedInAuth()
        
        assert auth.is_token_valid() is False
    
    def test_is_token_valid_expired(self):
        """Test token validation when token is expired"""
        auth = LinkedInAuth()
        auth.access_token = "test_token"
        auth.token_expiry = datetime.now() - timedelta(hours=1)
        
        assert auth.is_token_valid() is False
    
    def test_is_token_valid_valid_token(self):
        """Test token validation when token is valid"""
        auth = LinkedInAuth()
        auth.access_token = "test_token"
        auth.token_expiry = datetime.now() + timedelta(hours=1)
        
        assert auth.is_token_valid() is True
    
    def test_get_access_token_no_token(self):
        """Test getting access token when none exists"""
        auth = LinkedInAuth()
        
        with pytest.raises(AuthenticationError, match="No valid access token"):
            auth.get_access_token()
    
    def test_get_access_token_valid(self):
        """Test getting valid access token"""
        auth = LinkedInAuth()
        auth.access_token = "test_token"
        auth.token_expiry = datetime.now() + timedelta(hours=1)
        
        token = auth.get_access_token()
        assert token == "test_token"
    
    def test_revoke_token(self):
        """Test token revocation"""
        auth = LinkedInAuth()
        auth.access_token = "test_token"
        auth.token_expiry = datetime.now() + timedelta(hours=1)
        
        auth.revoke_token()
        
        assert auth.access_token is None
        assert auth.token_expiry is None
    
    def test_generate_state(self):
        """Test state parameter generation for CSRF protection"""
        auth = LinkedInAuth()
        
        state1 = auth._generate_state()
        state2 = auth._generate_state()
        
        # States should be different (random)
        assert state1 != state2
        
        # States should be reasonable length
        assert len(state1) > 20

