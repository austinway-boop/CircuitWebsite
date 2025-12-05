"""
Tests for input validation.
SECURITY: Testing validation is critical to prevent injection attacks.
"""
import pytest
from src.validators import InputValidator
from src.exceptions import ValidationError


class TestNameValidation:
    """Test name validation with various inputs"""
    
    def test_valid_names(self):
        """Test valid name inputs"""
        validator = InputValidator()
        
        # Valid names
        assert validator.validate_name("John Doe") == "John Doe"
        assert validator.validate_name("Mary-Jane Smith") == "Mary-Jane Smith"
        assert validator.validate_name("O'Brien") == "O'Brien"
        assert validator.validate_name("Jean-Luc Picard") == "Jean-Luc Picard"
    
    def test_name_whitespace_trimming(self):
        """Test that whitespace is trimmed"""
        validator = InputValidator()
        assert validator.validate_name("  John Doe  ") == "John Doe"
    
    def test_empty_name(self):
        """Test that empty names are rejected"""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="cannot be empty"):
            validator.validate_name("")
        with pytest.raises(ValidationError, match="cannot be empty"):
            validator.validate_name("   ")
    
    def test_short_name(self):
        """Test that very short names are rejected"""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="at least 2 characters"):
            validator.validate_name("A")
    
    def test_long_name(self):
        """Test that very long names are rejected"""
        validator = InputValidator()
        long_name = "A" * 101
        with pytest.raises(ValidationError, match="less than 100 characters"):
            validator.validate_name(long_name)
    
    def test_invalid_characters(self):
        """Test that names with invalid characters are rejected"""
        validator = InputValidator()
        
        # Numbers
        with pytest.raises(ValidationError, match="invalid characters"):
            validator.validate_name("John123")
        
        # Special characters
        with pytest.raises(ValidationError, match="invalid characters"):
            validator.validate_name("John@Doe")
        
        # Symbols
        with pytest.raises(ValidationError, match="invalid characters"):
            validator.validate_name("John$Doe")
    
    def test_sql_injection_attempt(self):
        """Test that SQL injection attempts are blocked"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_name("John'; DROP TABLE users; --")
    
    def test_xss_attempt(self):
        """Test that XSS attempts are blocked"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_name("<script>alert('xss')</script>")


class TestAgeValidation:
    """Test age validation"""
    
    def test_valid_ages(self):
        """Test valid age inputs"""
        validator = InputValidator()
        
        assert validator.validate_age(18) == 18
        assert validator.validate_age(25) == 25
        assert validator.validate_age(65) == 65
        assert validator.validate_age(100) == 100
    
    def test_age_boundaries(self):
        """Test age boundary values"""
        validator = InputValidator()
        
        # Minimum age
        assert validator.validate_age(13) == 13
        
        # Maximum age
        assert validator.validate_age(120) == 120
    
    def test_age_too_young(self):
        """Test that ages below minimum are rejected"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError, match="at least 13"):
            validator.validate_age(12)
        
        with pytest.raises(ValidationError, match="at least 13"):
            validator.validate_age(5)
    
    def test_age_too_old(self):
        """Test that ages above maximum are rejected"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError, match="less than 120"):
            validator.validate_age(121)
        
        with pytest.raises(ValidationError, match="less than 120"):
            validator.validate_age(200)
    
    def test_age_string_conversion(self):
        """Test that string ages are converted"""
        validator = InputValidator()
        
        assert validator.validate_age("25") == 25
    
    def test_age_invalid_type(self):
        """Test that invalid types are rejected"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError, match="must be a number"):
            validator.validate_age("twenty")
        
        with pytest.raises(ValidationError, match="must be a number"):
            validator.validate_age(None)


class TestSearchLimitValidation:
    """Test search limit validation"""
    
    def test_valid_limits(self):
        """Test valid limit values"""
        validator = InputValidator()
        
        assert validator.validate_search_limit(1) == 1
        assert validator.validate_search_limit(10) == 10
        assert validator.validate_search_limit(50) == 50
        assert validator.validate_search_limit(100) == 100
    
    def test_limit_too_low(self):
        """Test that limits below 1 are rejected"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError, match="at least 1"):
            validator.validate_search_limit(0)
        
        with pytest.raises(ValidationError, match="at least 1"):
            validator.validate_search_limit(-1)
    
    def test_limit_too_high(self):
        """Test that limits above 100 are rejected (cost control)"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError, match="cannot exceed 100"):
            validator.validate_search_limit(101)
        
        with pytest.raises(ValidationError, match="cannot exceed 100"):
            validator.validate_search_limit(1000)


class TestOutputSanitization:
    """Test output sanitization"""
    
    def test_sanitize_normal_text(self):
        """Test that normal text passes through"""
        validator = InputValidator()
        
        assert validator.sanitize_output("Hello World") == "Hello World"
        assert validator.sanitize_output("Test 123") == "Test 123"
    
    def test_sanitize_none(self):
        """Test that None is handled"""
        validator = InputValidator()
        
        assert validator.sanitize_output(None) == ""
    
    def test_sanitize_control_characters(self):
        """Test that control characters are removed"""
        validator = InputValidator()
        
        # Control characters should be removed
        result = validator.sanitize_output("Hello\x00World")
        assert "\x00" not in result
    
    def test_sanitize_whitespace(self):
        """Test that excess whitespace is trimmed"""
        validator = InputValidator()
        
        assert validator.sanitize_output("  Test  ") == "Test"

