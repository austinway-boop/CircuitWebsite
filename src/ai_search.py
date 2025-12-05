"""Profile search via Claude web search."""
import requests
import logging
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"


class ClaudeSearcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        
    def search_person(self, name: str, age: Optional[int] = None, location: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"Searching: {name}, age: {age}, location: {location}")
        
        current_year = datetime.now().year
        grad_year = (current_year - age + 22) if age else None
        grad_year_range = f"{grad_year-2} to {grad_year+2}" if grad_year else "unknown"
        
        # Expand location to broader area
        location_hints = ""
        if location:
            location_hints = f"""
Location given: {location}
NOTE: Location may be approximate. If they said "{location}", also search nearby cities, suburbs, 
and the broader metropolitan area. For example:
- "Austin" could mean Round Rock, Cedar Park, Pflugerville, or anywhere in Central Texas
- "San Francisco" could mean Bay Area, Oakland, San Jose, etc.
- Any city could mean surrounding suburbs or the metro area"""
        
        prompt = f"""You are a research assistant. Search the web THOROUGHLY to find information about this person.

PERSON TO FIND:
- Full Name: {name}
- Age: {age} years old
- Approximate graduation year: {grad_year_range}
{location_hints}

SEARCH STRATEGY (do ALL of these):
1. Search LinkedIn: "{name}" LinkedIn profile
2. Search with location: "{name}" {location if location else ''} university OR college
3. Search graduation records: "{name}" graduated {grad_year if grad_year else ''} university
4. Search social media: "{name}" education background
5. Try name variations (first name only, with middle initial, etc.)

WHAT TO FIND:
- College/University attended (MOST IMPORTANT)
- Degree earned
- Field of study
- Current career/job

After your thorough search, you MUST respond with this JSON:
{{
  "college": "University name - YOUR BEST GUESS based on all evidence, even if uncertain",
  "degree": "Degree type or your best guess",
  "field": "Field of study or your best guess",
  "career": "Current career or your best guess",
  "personality": "One personality trait that fits their profile",
  "confidence": 75,
  "source": "URL or 'inference from search results'",
  "reasoning": "Brief explanation of how you determined this"
}}

CRITICAL RULES:
1. You MUST provide a college prediction - make your BEST EDUCATED GUESS based on:
   - Their location (nearby universities)
   - Their age (graduation timeline)
   - Any partial info found
   - Common universities in their area
2. If you found NOTHING, still guess based on location/age demographics
3. Set confidence 10-30 for guesses, 40-70 for partial info, 80+ for confirmed finds
4. NEVER return null for college - always make a prediction"""

        try:
            logger.info("Calling Claude API with web search...")
            response = requests.post(
                ANTHROPIC_API_URL,
                headers=self.headers,
                json={
                    'model': CLAUDE_MODEL,
                    'max_tokens': 4096,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'tools': [{
                        'type': 'web_search_20250305',
                        'name': 'web_search',
                        'max_uses': 10
                    }]
                },
                timeout=90
            )
            
            logger.info(f"Claude API Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Claude response: {json.dumps(result, indent=2)[:1000]}")
                return self._parse_claude_response(result, name, age, location)
            else:
                logger.error(f"Claude error: {response.status_code} - {response.text[:500]}")
                return self._fallback_result(name, age, location)
                
        except Exception as e:
            logger.error(f"Claude exception: {e}", exc_info=True)
            return self._fallback_result(name, age, location)
    
    def _parse_claude_response(self, response: Dict, name: str, age: Optional[int], location: Optional[str]) -> Dict[str, Any]:
        content_blocks = response.get('content', [])
        
        # Find the final text response (after web searches)
        final_text = ""
        sources = []
        
        for block in content_blocks:
            if block.get('type') == 'text':
                final_text = block.get('text', '')
                # Check for citations
                citations = block.get('citations', [])
                for cite in citations:
                    sources.append(cite.get('url', ''))
            elif block.get('type') == 'web_search_tool_result':
                # Extract source URLs from search results
                results = block.get('content', [])
                if isinstance(results, list):
                    for r in results:
                        if r.get('type') == 'web_search_result':
                            sources.append(r.get('url', ''))
        
        logger.info(f"Final text: {final_text[:500]}")
        logger.info(f"Sources found: {sources}")
        
        # Try to extract JSON from the response
        return self._extract_json(final_text, sources, name, age, location)
    
    def _extract_json(self, text: str, sources: list, name: str, age: Optional[int], location: Optional[str]) -> Dict[str, Any]:
        cleaned = text.strip()
        cleaned = re.sub(r'^```json\s*\n?', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^```\s*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        
        try:
            # Find JSON object
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = cleaned[start:end]
                data = json.loads(json_str)
            else:
                data = json.loads(cleaned)
            
            college = data.get('college')
            # Only reject truly empty values - keep guesses
            if college and str(college).lower() in ['null', 'none', '', 'n/a']:
                college = None
            
            # If AI responded but gave no college, make inference from location
            if not college and location:
                college = self._infer_college_from_location(location)
                data['confidence'] = 15  # Low confidence for pure inference
            
            source_url = data.get('source') or (sources[0] if sources else None)
            
            return {
                'found': bool(college),
                'college': college or "Unable to determine",
                'degree': data.get('degree') or "Unknown",
                'field': data.get('field') or "Unknown",
                'career': data.get('career') or "Unknown",
                'personality': data.get('personality') or "Unknown",
                'confidence': int(data.get('confidence', 20)),
                'source': source_url,
                'reasoning': data.get('reasoning', ''),
                'raw_response': text
            }
            
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Text was: {cleaned[:300]}")
            # Still try to make a prediction from location if AI responded
            if location:
                return self._location_based_prediction(name, age, location, text)
            return self._fallback_result(name, age, location)
    
    def _infer_college_from_location(self, location: str) -> Optional[str]:
        """Infer most likely college based on location."""
        location_lower = location.lower()
        
        # Major city -> nearby flagship university mapping
        location_map = {
            'austin': 'University of Texas at Austin',
            'houston': 'University of Houston',
            'dallas': 'Southern Methodist University',
            'san antonio': 'University of Texas at San Antonio',
            'los angeles': 'UCLA',
            'san francisco': 'UC Berkeley',
            'new york': 'NYU',
            'boston': 'Boston University',
            'chicago': 'University of Chicago',
            'seattle': 'University of Washington',
            'denver': 'University of Colorado',
            'atlanta': 'Georgia Tech',
            'miami': 'University of Miami',
            'phoenix': 'Arizona State University',
            'portland': 'Portland State University',
            'san diego': 'UC San Diego',
        }
        
        for city, university in location_map.items():
            if city in location_lower:
                return university
        
        return None
    
    def _location_based_prediction(self, name: str, age: Optional[int], location: str, raw_text: str) -> Dict[str, Any]:
        """Make prediction based on location when JSON parsing fails but AI responded."""
        college = self._infer_college_from_location(location) or f"Local university near {location}"
        
        return {
            'found': True,
            'college': college,
            'degree': "Bachelor's degree",
            'field': "Unknown",
            'career': "Unknown",
            'personality': "Unknown",
            'confidence': 10,
            'source': 'inference from location',
            'reasoning': f'Based on location: {location}',
            'raw_response': raw_text
        }
    
    def _fallback_result(self, name: str, age: Optional[int], location: Optional[str]) -> Dict[str, Any]:
        """Only used when API completely fails - returns error state."""
        return {
            'found': False,
            'college': 'API Error - Could not process request',
            'degree': None,
            'field': None,
            'career': None,
            'personality': None,
            'confidence': 0,
            'source': None,
            'error': 'API request failed',
            'raw_response': None
        }


# Backwards compatibility
DeepSeekSearcher = ClaudeSearcher
