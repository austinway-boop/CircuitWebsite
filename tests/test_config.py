"""
Tests for configuration management.
"""
import pytest
import os
from src.config import Config
from unittest.mock import patch


class TestConfig:
    """Test configuration loading and validation"""
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'test_client_id',
        'LINKEDIN_CLIENT_SECRET': 'test_client_secret',
        'LINKEDIN_REDIRECT_URI': 'http://localhost:8000/callback',
        'APP_ENV': 'development',
        'DEBUG': 'false',
        'LOG_LEVEL': 'INFO',
        'MAX_SEARCH_RESULTS': '10',
        'MAX_API_CALLS_PER_MINUTE': '30',
        'MAX_API_CALLS_PER_HOUR': '500'
    })
    def test_load_config(self):
        """Test that configuration loads correctly"""
        config = Config()
        
        assert config.client_id == 'test_client_id'
        assert config.client_secret == 'test_client_secret'
        assert config.redirect_uri == 'http://localhost:8000/callback'
        assert config.app_env == 'development'
        assert config.debug is False
        assert config.log_level == 'INFO'
        assert config.max_search_results == 10
        assert config.max_api_calls_per_minute == 30
        assert config.max_api_calls_per_hour == 500
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'test_id',
        'LINKEDIN_CLIENT_SECRET': 'test_secret'
    }, clear=True)
    def test_default_values(self):
        """Test that default values are used when not specified"""
        config = Config()
        
        assert config.redirect_uri == 'http://localhost:8000/callback'
        assert config.app_env == 'development'
        assert config.log_level == 'INFO'
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_SECRET': 'test_secret'
    }, clear=True)
    def test_missing_required_field(self):
        """Test that missing required fields raise errors"""
        with pytest.raises(ValueError, match="LINKEDIN_CLIENT_ID"):
            Config()
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'your_client_id_here',
        'LINKEDIN_CLIENT_SECRET': 'test_secret'
    })
    def test_placeholder_client_id_rejected(self):
        """Test that placeholder values are rejected"""
        with pytest.raises(ValueError, match="not configured properly"):
            Config()
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'test_id',
        'LINKEDIN_CLIENT_SECRET': 'test_secret',
        'APP_ENV': 'production',
        'DEBUG': 'true'
    })
    def test_production_debug_rejected(self):
        """Test that debug mode in production is rejected"""
        with pytest.raises(ValueError, match="DEBUG mode cannot be enabled in production"):
            Config()
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'test_id',
        'LINKEDIN_CLIENT_SECRET': 'test_secret',
        'APP_ENV': 'production'
    })
    def test_is_production(self):
        """Test production environment detection"""
        config = Config()
        assert config.is_production() is True
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'test_id',
        'LINKEDIN_CLIENT_SECRET': 'test_secret',
        'APP_ENV': 'development'
    })
    def test_is_not_production(self):
        """Test non-production environment detection"""
        config = Config()
        assert config.is_production() is False

