# Usage Guide

## Quick Start

### 1. Installation

First, install dependencies:

```bash
# Using the setup script (recommended)
./scripts/setup.sh

# Or manually
pip install -r requirements.txt
mkdir -p logs docs
```

### 2. Configuration

Create a `.env` file with your LinkedIn credentials. The configuration should include:

- **Client ID**: `your-linkedin-client-id`
- **Client Secret**: `your-linkedin-client-secret`
- **Rate Limits**: 30 calls/min, 500 calls/hour
- **Environment**: Development mode

### 3. Understanding LinkedIn API Limitations

⚠️ **IMPORTANT**: Before you start, understand what this application can and cannot do.

**With standard LinkedIn API access (what you have):**

✅ **You CAN**:
- Authenticate with LinkedIn
- Access your own profile
- Get your own education information
- Manage your own connections

❌ **You CANNOT**:
- Search for other people by name
- Access other people's profiles
- Get other people's education information

**Why?** LinkedIn restricted their API in recent years. People search is no longer available in the standard API.

### 4. What You Need for People Search

To actually search for people and get their college information, you need ONE of these:

#### Option 1: LinkedIn Talent Solutions API (Official)
- **For**: Recruiters and HR professionals
- **Cost**: Paid subscription (contact LinkedIn sales)
- **Approval**: Requires LinkedIn approval
- **Access**: Full people search and profile data

#### Option 2: Third-Party Data Services
Popular options:
- **Apollo.io** - Sales intelligence platform
- **RocketReach** - Contact information database
- **Hunter.io** - Email finder and verification
- **Clearbit** - Business intelligence
- **ZoomInfo** - B2B contact database

**Important**: Review pricing and terms of service for each.

#### Option 3: LinkedIn Sales Navigator (Web Interface)
- **For**: Manual searching
- **Cost**: ~$80-100/month
- **Access**: Via LinkedIn's web interface (no API)

## Using This Application

### View Configuration and Limitations

```bash
python main.py info
```

This displays your current configuration and explains API limitations.

### Test Your Setup

```bash
python main.py test-connection
```

This will test your LinkedIn API connection (after authentication).

### Start OAuth Authentication

```bash
python main.py auth
```

This will:
1. Generate an authorization URL
2. Prompt you to visit the URL in your browser
3. Ask you to authorize the application
4. Request the authorization code from the redirect URL

**Note**: You'll need to set up a redirect URL handler or manually copy the code from the redirect.

### Attempt to Search (Will Show Limitation Message)

```bash
python main.py search --name "John Doe" --age 25
```

This will show a clear message explaining that people search is not available with standard API access.

### Get Your Own Education Information

While you can't search for others, you CAN get your own information:

```python
from src.auth import LinkedInAuth
from src.profile_searcher import ProfileSearcher

# Authenticate (you'll need to complete OAuth flow)
auth = LinkedInAuth()
# ... complete OAuth flow ...

# Get your education
searcher = ProfileSearcher()
searcher.authenticate(auth)
colleges = searcher.get_my_college()
print(f"Your colleges: {colleges}")
```

## Alternative Workflows

### Workflow 1: Using Third-Party APIs

If you sign up for a third-party service like Apollo or RocketReach:

1. Get their API credentials
2. Modify `src/linkedin_client.py` to use their API instead
3. Update the search methods to use their endpoints

Example structure for Apollo.io:

```python
import requests

def search_apollo(name, age):
    api_key = "your_apollo_key"
    url = "https://api.apollo.io/v1/people/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "q_person_name": name,
        # ... other filters
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

### Workflow 2: Manual Research + This Tool

1. Use LinkedIn Sales Navigator (web) to find people
2. Get their public profile URL
3. Use this application to store/manage the data
4. Process education information

### Workflow 3: Export Your Connections

1. Export your LinkedIn connections (Settings > Data Privacy > Download Data)
2. Import the CSV into this application
3. Process the education data for your connections only

## Running Tests

Verify everything works correctly:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Security Best Practices

### Never Commit Secrets

Your `.env` file is already in `.gitignore`, but double-check:

```bash
# Verify .env is ignored
git status
# Should NOT show .env file
```

### Rotate Credentials

Periodically rotate your LinkedIn API credentials:
1. Generate new credentials in LinkedIn Developer Portal
2. Update `.env` file
3. Restart the application

### Monitor Usage

Check your API usage regularly:

```bash
# View logs
tail -f logs/linkedin_search.log

# Check rate limit stats in application
# The rate limiter logs usage every 10 calls
```

### Production Deployment

If deploying to production:

1. Update `.env`:
   ```
   APP_ENV=production
   DEBUG=false
   LOG_LEVEL=WARNING
   ```

2. Use environment variables instead of `.env` file
3. Set up proper logging infrastructure
4. Enable monitoring and alerting
5. Use HTTPS only

## Troubleshooting

### "Rate limit exceeded"

Wait a few minutes. The limits are:
- 30 calls per minute
- 500 calls per hour

You can adjust these in `.env` if needed.

### "No valid access token"

Run the authentication flow:
```bash
python main.py auth
```

### "People search not available"

This is expected. See "Understanding LinkedIn API Limitations" above.

### Import errors

Make sure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Permission errors on logs/

Create the directory:
```bash
mkdir -p logs
chmod 755 logs
```

## Example: Complete Workflow

Here's a complete example of using the application:

```bash
# 1. View your configuration
python main.py info

# 2. Start authentication
python main.py auth
# Follow the prompts...

# 3. Try a search (will show limitations)
python main.py search --name "John Doe" --age 25

# Output will explain you need special API access
```

## Git Setup

To commit your code:

```bash
# Configure git (if not already done)
git config user.email "your@email.com"
git config user.name "Your Name"

# Commit the code
git add .
git commit -m "Initial setup of LinkedIn search application"
```

## Next Steps

1. **Decide on your approach**:
   - Do you need to search for arbitrary people?
   - Or just want to work with your own data/connections?

2. **If you need people search**:
   - Research third-party APIs
   - Compare pricing and features
   - Sign up for a service
   - Integrate with this codebase

3. **If working with your own data**:
   - Complete the OAuth flow
   - Test accessing your own profile
   - Export your connections
   - Build features on top of this foundation

## Support

For questions about:
- **This application**: Review code comments and documentation
- **LinkedIn API**: See [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- **Third-party services**: Contact their support teams

## Cost Estimation

With current configuration:
- **LinkedIn API**: Free (for basic access)
- **This application**: $0/month
- **Rate limits**: 30/min, 500/hour = max ~360K/month

If using third-party services:
- **Apollo.io**: ~$49-149/month
- **RocketReach**: ~$39-199/month
- **LinkedIn Sales Navigator**: ~$80-135/month

Always check current pricing before signing up.

