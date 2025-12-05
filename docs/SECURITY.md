# Security Documentation

This document describes the security measures implemented in the LinkedIn Profile Search application.

## Security Principles

This application follows industry best practices and secure coding standards:

1. **Never Trust User Input** - All inputs are validated and sanitized
2. **Defense in Depth** - Multiple layers of security
3. **Least Privilege** - Minimal permissions and API scopes
4. **Fail Securely** - Default deny with explicit allow
5. **Security by Design** - Built-in from the start

## Implemented Security Measures

### 1. Input Validation

**Location**: `src/validators.py`

All user inputs are strictly validated:

- **Name validation**:
  - Allowlist: Only letters, spaces, hyphens, apostrophes
  - Length limits: 2-100 characters
  - No numbers or special characters
  - Prevents SQL injection, XSS, command injection

- **Age validation**:
  - Type checking and conversion
  - Range validation: 13-120 years
  - Integer enforcement

- **Search limit validation**:
  - Maximum 100 results (cost control)
  - Minimum 1 result
  - Prevents resource exhaustion

### 2. Output Sanitization

**Location**: `src/validators.py`

All outputs are sanitized before display:

- Control character removal
- Whitespace trimming
- Prevents XSS attacks
- Prevents terminal injection

### 3. Rate Limiting

**Location**: `src/rate_limiter.py`

**CRITICAL for cost control and security:**

- Per-minute limits (default: 30 calls)
- Per-hour limits (default: 500 calls)
- Automatic call tracking and cleanup
- Prevents:
  - Infinite loops
  - Runaway processes
  - Excessive API costs
  - DoS attacks

### 4. Credential Management

**Location**: `src/config.py`

Secure secrets management:

- API credentials in `.env` file
- Never hardcoded
- Never committed to version control
- `.env` in `.gitignore`
- Placeholder detection and rejection
- Environment-specific configuration

### 5. OAuth 2.0 Authentication

**Location**: `src/auth.py`

Industry-standard authentication:

- OAuth 2.0 flow
- CSRF protection with state parameter
- Token expiry tracking
- Automatic token validation
- Secure token storage
- Token revocation support

### 6. Error Handling

**Location**: `src/exceptions.py`

Fail-secure error handling:

- Custom exception hierarchy
- No sensitive data in error messages
- Comprehensive logging
- Graceful degradation
- Clear user-facing messages

### 7. Logging and Monitoring

**Location**: All modules

Comprehensive audit trail:

- All API calls logged
- Authentication events logged
- Validation failures logged
- Rate limit events logged
- No sensitive data in logs (tokens, passwords)
- Log rotation ready

### 8. API Client Security

**Location**: `src/linkedin_client.py`

Secure API interactions:

- HTTPS only
- Request timeouts (prevents hanging)
- Rate limit enforcement
- Error handling for all responses
- No credentials in URLs
- Bearer token authentication

### 9. Configuration Validation

**Location**: `src/config.py`

Environment validation:

- Required fields enforcement
- Placeholder detection
- Production mode checks
- Debug mode restrictions
- Reasonable limit validation

## Threat Model

### Threats Addressed

1. **Injection Attacks**
   - SQL injection: ✅ Input validation blocks
   - XSS: ✅ Output sanitization prevents
   - Command injection: ✅ No shell execution of user input

2. **Authentication Attacks**
   - Credential theft: ✅ Environment variables, not committed
   - CSRF: ✅ State parameter in OAuth flow
   - Token theft: ✅ Short-lived tokens

3. **Resource Exhaustion**
   - Infinite loops: ✅ Rate limiting prevents
   - API quota exhaustion: ✅ Hard limits enforced
   - Memory exhaustion: ✅ Result limits enforced

4. **Information Disclosure**
   - Credentials in logs: ✅ Never logged
   - Error message leakage: ✅ Generic messages
   - Token exposure: ✅ Sanitized from output

5. **Cost Control**
   - Runaway API calls: ✅ Rate limiting
   - Excessive results: ✅ Hard limits
   - Loop prevention: ✅ Multiple safeguards

### Threats NOT Addressed

This application does NOT address:

- Physical security
- Network-layer attacks (DDoS, etc.)
- OS-level vulnerabilities
- Hardware attacks
- Social engineering

These should be addressed at infrastructure/deployment level.

## Testing

Security tests are included:

```bash
pytest tests/test_validators.py -v  # Input validation tests
pytest tests/test_rate_limiter.py -v  # Rate limiting tests
pytest tests/test_config.py -v  # Configuration tests
```

## Compliance

This application follows guidelines from:

- **OWASP** (Open Web Application Security Project)
  - Input validation
  - Output encoding
  - Authentication
  - Session management
  - Access control
  - Error handling

- **SAFECode** (Software Assurance Forum for Excellence in Code)
  - Secure design principles
  - Threat modeling
  - Coding standards
  - Testing

- **CWE/SANS Top 25** (Common Weakness Enumeration)
  - Injection prevention
  - Input validation
  - Resource management

## Deployment Recommendations

### Production Deployment

When deploying to production:

1. **Set environment to production**:
   ```
   APP_ENV=production
   DEBUG=false
   ```

2. **Use strong secrets**:
   - Never use example credentials
   - Rotate credentials regularly
   - Use a secrets manager if available

3. **Enable HTTPS only**:
   - Never run over HTTP in production
   - Use TLS 1.2 or higher

4. **Monitor logs**:
   - Set up log aggregation
   - Alert on authentication failures
   - Alert on rate limit hits

5. **Regular updates**:
   - Keep dependencies updated
   - Monitor security advisories
   - Apply patches promptly

6. **Principle of Least Privilege**:
   - Run with minimal permissions
   - Use dedicated service account
   - Restrict file system access

### Security Checklist

Before production deployment:

- [ ] `.env` file is NOT committed to git
- [ ] Production credentials are set
- [ ] DEBUG=false in production
- [ ] APP_ENV=production
- [ ] Rate limits are configured appropriately
- [ ] Logs directory has proper permissions
- [ ] HTTPS is enforced
- [ ] Dependencies are up to date
- [ ] Tests pass, including security tests
- [ ] Code has been reviewed

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. **DO NOT** share the vulnerability publicly
3. Contact the maintainer privately
4. Provide details about the vulnerability
5. Allow time for a fix before disclosure

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SAFECode Secure Development](https://safecode.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [LinkedIn API Security](https://docs.microsoft.com/en-us/linkedin/)

## Cost Control Measures

**CRITICAL**: This application implements multiple layers of cost control:

1. **Hard Limits**:
   - Maximum 30 API calls per minute
   - Maximum 500 API calls per hour
   - Maximum 100 results per search

2. **Loop Prevention**:
   - Rate limiter blocks excessive calls
   - Input validation prevents infinite loops
   - Maximum iterations enforced

3. **Cost Calculation**:
   - Default limits = ~360,000 calls/month max
   - LinkedIn API free tier = sufficient
   - Third-party services = review pricing

4. **Monitoring**:
   - API usage logged
   - Rate limit hits logged
   - Easy to track usage

**Formula**: `max_monthly_cost = (calls_per_hour × 24 × 30) × cost_per_call`

With default settings and LinkedIn free tier: **$0/month**

