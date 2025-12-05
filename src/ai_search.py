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
        
        prompt = f"""Search the web for information about this person and find their educational background:

Name: {name}
Age: {age}
Location: {location}
Likely college graduation year: ~{grad_year}

Search for "{name}" on LinkedIn, university records, or any public profiles to find:
1. What college/university did they attend?
2. What degree did they earn?
3. What is their current job/career?

After searching, respond with ONLY this JSON format:
{{
  "college": "The actual university name found, or null if not found",
  "degree": "Degree type if found (BS, BA, MS, etc), or null",
  "field": "Field of study if found, or null",
  "career": "Current job/career if found, or null",
  "personality": "One word trait based on their profile, or null",
  "confidence": 85,
  "source": "URL where you found the info, or null"
}}

IMPORTANT:
- Only report information you actually found from web search
- Do NOT guess or make up information
- Return null for fields you couldn't find
- Set confidence to 0 if you found nothing about this person"""

        try:
            logger.info("Calling Claude API with web search...")
            response = requests.post(
                ANTHROPIC_API_URL,
                headers=self.headers,
                json={
                    'model': CLAUDE_MODEL,
                    'max_tokens': 2048,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'tools': [{
                        'type': 'web_search_20250305',
                        'name': 'web_search',
                        'max_uses': 5
                    }]
                },
                timeout=60
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
            if college and str(college).lower() in ['null', 'none', 'unknown', '', 'n/a']:
                college = None
            
            source_url = data.get('source') or (sources[0] if sources else None)
            
            return {
                'found': bool(college),
                'college': college,
                'degree': data.get('degree'),
                'field': data.get('field'),
                'career': data.get('career'),
                'personality': data.get('personality'),
                'confidence': int(data.get('confidence', 0)) if college else 0,
                'source': source_url,
                'raw_response': text
            }
            
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Text was: {cleaned[:300]}")
            return self._fallback_result(name, age, location)
    
    def _fallback_result(self, name: str, age: Optional[int], location: Optional[str]) -> Dict[str, Any]:
        return {
            'found': False,
            'college': None,
            'degree': None,
            'field': None,
            'career': None,
            'personality': None,
            'confidence': 0,
            'source': None,
            'raw_response': None
        }


# Backwards compatibility
DeepSeekSearcher = ClaudeSearcher
