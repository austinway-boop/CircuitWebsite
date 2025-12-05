# LinkedIn API Alternatives

Since LinkedIn's standard API doesn't support people search, here are your alternatives for finding people and their education information.

## Official LinkedIn Solutions

### 1. LinkedIn Talent Solutions API

**Best for**: Recruiters, HR departments, talent acquisition teams

**Features**:
- Full people search by name, location, company, etc.
- Access to detailed profiles
- Education history
- Work history
- Skills and endorsements

**Pricing**: Enterprise pricing (contact LinkedIn sales)

**Requirements**:
- LinkedIn approval required
- Business use case verification
- Typically $10,000+ annually

**How to get it**:
1. Visit [LinkedIn Talent Solutions](https://business.linkedin.com/talent-solutions)
2. Contact sales team
3. Discuss your use case
4. Go through approval process

**API Documentation**: Available after approval

---

### 2. LinkedIn Marketing Developer Platform

**Best for**: Marketing agencies, advertisers

**Features**:
- Limited profile access
- Company data
- Ad targeting capabilities
- Analytics

**Pricing**: Varies based on ad spend and usage

**Requirements**:
- Marketing partner application
- LinkedIn approval
- Minimum ad spend requirements

**Note**: Less suitable for people search compared to Talent Solutions

---

### 3. LinkedIn Sales Navigator (No API)

**Best for**: Manual research, sales teams

**Features**:
- Advanced people search
- Lead recommendations
- InMail messaging
- Save leads and accounts
- **Note**: Web interface only, no API

**Pricing**:
- Core: ~$80/month
- Advanced: ~$135/month
- Advanced Plus: Custom pricing

**Limitations**:
- Manual use only (no programmatic access)
- Export limits
- No bulk operations

**How to integrate with this application**:
1. Use Sales Navigator to find people manually
2. Export results to CSV
3. Import CSV into this application for processing

---

## Third-Party Data Services

### 1. Apollo.io ⭐ RECOMMENDED

**Best for**: B2B contact data, comprehensive search

**Features**:
- 250M+ contacts
- Company and people search
- Email finder
- Phone numbers
- Job titles and education
- API access

**Pricing**:
- Free: 50 email credits/month
- Basic: $49/user/month
- Professional: $99/user/month
- Organization: $149/user/month

**API**:
- RESTful API
- Good documentation
- Python SDK available

**Example Integration**:
```python
import requests

def search_apollo(name, age=None):
    api_key = "YOUR_APOLLO_KEY"
    url = "https://api.apollo.io/v1/people/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "q_keywords": name,
        "page": 1,
        "per_page": 10
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

**Pros**:
- Comprehensive data
- Good API
- Reasonable pricing
- Free tier available

**Cons**:
- Data accuracy varies
- Credit-based system

**Website**: https://www.apollo.io

---

### 2. RocketReach

**Best for**: Email and phone number discovery

**Features**:
- 700M+ professionals
- Email verification
- Phone numbers
- Social profiles
- Education and work history
- API access

**Pricing**:
- Essentials: $39/month (80 lookups)
- Pro: $99/month (200 lookups)
- Ultimate: $199/month (500 lookups)

**API**:
- RESTful API
- Lookup and search endpoints

**Example**:
```python
import requests

def search_rocketreach(name, current_employer=None):
    api_key = "YOUR_RR_KEY"
    url = "https://api.rocketreach.co/v2/api/search"
    
    params = {
        "name": name,
        "current_employer": current_employer,
        "api_key": api_key
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

**Pros**:
- Large database
- Good email accuracy
- Simple API

**Cons**:
- More expensive per lookup
- Limited free tier

**Website**: https://rocketreach.co

---

### 3. Hunter.io

**Best for**: Email finding and verification

**Features**:
- Email finder by name + domain
- Email verification
- Domain search
- API access

**Pricing**:
- Free: 25 searches/month
- Starter: $49/month (500 searches)
- Growth: $99/month (2,500 searches)
- Business: $199/month (10,000 searches)

**API**:
- Simple RESTful API
- Good documentation

**Example**:
```python
import requests

def find_email_hunter(first_name, last_name, domain):
    api_key = "YOUR_HUNTER_KEY"
    url = "https://api.hunter.io/v2/email-finder"
    
    params = {
        "domain": domain,
        "first_name": first_name,
        "last_name": last_name,
        "api_key": api_key
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

**Pros**:
- Excellent email finding
- High accuracy
- Good free tier
- Simple to use

**Cons**:
- Requires company domain
- Limited profile data
- No education info

**Website**: https://hunter.io

---

### 4. Clearbit

**Best for**: B2B enrichment, company data

**Features**:
- Person and company enrichment
- Email to person data
- Reveal (anonymous traffic identification)
- API access

**Pricing**:
- Contact for pricing
- Typically $99-999/month

**API**:
- RESTful API
- Real-time enrichment

**Pros**:
- High-quality data
- Real-time enrichment
- Good for SaaS products

**Cons**:
- Expensive
- No free tier
- Better for companies than individuals

**Website**: https://clearbit.com

---

### 5. ZoomInfo

**Best for**: Enterprise B2B contact data

**Features**:
- 100M+ business contacts
- Company information
- Org charts
- Intent data
- API access

**Pricing**:
- Contact for pricing
- Enterprise-level (typically $10,000+/year)

**API**:
- Comprehensive API
- SOAP and REST

**Pros**:
- Most comprehensive B2B data
- High accuracy
- Great for enterprises

**Cons**:
- Very expensive
- Overkill for small projects
- Complex pricing

**Website**: https://www.zoominfo.com

---

## Comparison Table

| Service | Cost/Month | Free Tier | Education Data | API Quality | Best For |
|---------|-----------|-----------|----------------|-------------|----------|
| **LinkedIn Talent Solutions** | $1000+ | No | ✅ Excellent | ⭐⭐⭐⭐⭐ | Recruiters |
| **LinkedIn Sales Nav** | $80-135 | Trial | ✅ Good | ❌ No API | Manual research |
| **Apollo.io** | $0-149 | ✅ 50/mo | ✅ Good | ⭐⭐⭐⭐ | General use |
| **RocketReach** | $39-199 | Limited | ✅ Good | ⭐⭐⭐ | Contact finding |
| **Hunter.io** | $0-199 | ✅ 25/mo | ❌ No | ⭐⭐⭐⭐ | Email only |
| **Clearbit** | $99-999 | No | ⚠️ Limited | ⭐⭐⭐⭐ | Enrichment |
| **ZoomInfo** | $10k+ | No | ✅ Good | ⭐⭐⭐⭐⭐ | Enterprise |

---

## Recommendation for Your Use Case

**Goal**: Enter name + age, find person, get their college

### Best Option: Apollo.io

**Why**:
1. ✅ Has free tier (50 searches/month)
2. ✅ Good education data coverage
3. ✅ Simple API
4. ✅ Affordable paid plans
5. ✅ Can filter/search by various criteria

**How to integrate**:

1. Sign up at https://www.apollo.io
2. Get API key from dashboard
3. Update this application's code:

```python
# src/apollo_client.py
import requests
from .validators import InputValidator

class ApolloClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.validator = InputValidator()
    
    def search_people(self, name, age=None, limit=10):
        # Validate inputs
        name = self.validator.validate_name(name)
        if age:
            age = self.validator.validate_age(age)
        
        url = f"{self.base_url}/people/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "q_keywords": name,
            "page": 1,
            "per_page": limit
        }
        
        # Estimate graduation year from age if provided
        if age:
            current_year = 2025
            birth_year = current_year - age
            grad_year = birth_year + 22  # Typical graduation age
            # Apollo allows filtering by education years
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def extract_education(self, person_data):
        """Extract college information from Apollo person data"""
        colleges = []
        
        if 'education' in person_data:
            for edu in person_data['education']:
                college = {
                    'name': edu.get('school_name', ''),
                    'degree': edu.get('degree', ''),
                    'major': edu.get('major', ''),
                    'start_year': edu.get('start_date', ''),
                    'end_year': edu.get('end_date', '')
                }
                colleges.append(college)
        
        return colleges
```

4. Update `.env`:
```
APOLLO_API_KEY=your_apollo_key_here
```

5. Use in your application:
```python
from src.apollo_client import ApolloClient

apollo = ApolloClient(api_key="your_key")
results = apollo.search_people("John Doe", age=25)

for person in results['people']:
    colleges = apollo.extract_education(person)
    print(f"{person['name']}: {colleges}")
```

---

## Legal and Ethical Considerations

### Data Privacy

⚠️ **Important**: When using any data service:

1. **GDPR Compliance** (if targeting EU residents)
   - Ensure service is GDPR compliant
   - Have legal basis for processing
   - Respect right to erasure

2. **CCPA Compliance** (if targeting California)
   - Similar to GDPR requirements
   - Disclosure and opt-out rights

3. **Terms of Service**
   - Read and comply with each service's ToS
   - Don't scrape or violate rate limits
   - Respect data usage restrictions

### Best Practices

1. **Only collect necessary data**
2. **Store data securely** (this app already does this)
3. **Delete data when no longer needed**
4. **Get consent when required**
5. **Be transparent about data sources**

---

## Implementation Checklist

To switch to a third-party service:

- [ ] Choose a service (recommend Apollo.io)
- [ ] Sign up and get API key
- [ ] Review pricing and limits
- [ ] Read API documentation
- [ ] Add API key to `.env`
- [ ] Create new client module (e.g., `apollo_client.py`)
- [ ] Update `profile_searcher.py` to use new client
- [ ] Test with sample searches
- [ ] Update rate limits in `.env` based on service limits
- [ ] Review legal/ToS requirements
- [ ] Implement data retention policies
- [ ] Update documentation
- [ ] Test thoroughly before production use

---

## Sample Code: Complete Integration

Here's a complete example integrating Apollo.io with this application:

```python
# src/apollo_client.py
import requests
from typing import List, Dict, Any, Optional
from .validators import InputValidator
from .rate_limiter import RateLimiter
from .exceptions import SearchError, DataRetrievalError

class ApolloClient:
    """Apollo.io API client for people search"""
    
    API_BASE = "https://api.apollo.io/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.validator = InputValidator()
        self.rate_limiter = RateLimiter()
    
    def search_by_name_and_age(
        self,
        name: str,
        age: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for people by name and age.
        Returns list of matches with education data.
        """
        # Validate inputs
        name = self.validator.validate_name(name)
        age = self.validator.validate_age(age)
        limit = self.validator.validate_search_limit(limit)
        
        # Check rate limit
        if not self.rate_limiter.check_limit():
            raise SearchError("Rate limit exceeded")
        
        # Estimate graduation year from age
        current_year = 2025
        birth_year = current_year - age
        estimated_grad_year = birth_year + 22
        
        # Make API request
        url = f"{self.API_BASE}/people/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        
        payload = {
            "q_keywords": name,
            "page": 1,
            "per_page": limit,
            "education_end_date": f"{estimated_grad_year - 2},{estimated_grad_year + 2}"
        }
        
        try:
            self.rate_limiter.record_call()
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise DataRetrievalError(
                    f"Apollo API error: {response.status_code}"
                )
            
            data = response.json()
            
            # Extract and format results
            results = []
            for person in data.get('people', []):
                results.append({
                    'name': person.get('name', ''),
                    'title': person.get('title', ''),
                    'company': person.get('organization_name', ''),
                    'linkedin_url': person.get('linkedin_url', ''),
                    'colleges': self._extract_colleges(person)
                })
            
            return results
            
        except requests.RequestException as e:
            raise DataRetrievalError(f"Network error: {str(e)}")
    
    def _extract_colleges(self, person: Dict) -> List[Dict]:
        """Extract college information from person data"""
        colleges = []
        
        for edu in person.get('education', []):
            college = {
                'name': edu.get('school_name', ''),
                'degree': edu.get('degree', ''),
                'major': edu.get('major', ''),
                'years': f"{edu.get('start_date', '')}-{edu.get('end_date', '')}"
            }
            
            # Only add if we have a school name
            if college['name']:
                colleges.append(college)
        
        return colleges

# Usage in main.py or CLI
if __name__ == '__main__':
    from src.apollo_client import ApolloClient
    import os
    
    api_key = os.getenv('APOLLO_API_KEY')
    apollo = ApolloClient(api_key)
    
    results = apollo.search_by_name_and_age("John Doe", 25)
    
    for person in results:
        print(f"\n{person['name']}")
        print(f"Title: {person['title']}")
        print(f"Company: {person['company']}")
        print("Colleges:")
        for college in person['colleges']:
            print(f"  • {college['name']} - {college['degree']}")
```

---

## Questions?

If you have questions about which service to choose or how to integrate, consider:

1. **Budget**: Apollo.io has free tier, others vary
2. **Data quality**: LinkedIn Talent Solutions > Apollo > others
3. **Ease of integration**: Hunter/Apollo are simplest
4. **Your use case**: Recruiting? Marketing? Research?

Choose based on your specific needs and budget.

