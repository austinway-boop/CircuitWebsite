"""
LinkedIn Profile Scraper
Extracts username, education, work experience from LinkedIn profiles.
"""
import requests
import logging
import re
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """Scrape LinkedIn profiles for comprehensive information"""
    
    def __init__(self):
        self.session = requests.Session()
        # Use Slackbot user-agent - LinkedIn allows this for link previews
        self.session.headers.update({
            'User-Agent': 'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def scrape_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a LinkedIn profile for all information.
        
        Returns:
            Dictionary with username, education, jobs, and calculated age
        """
        try:
            logger.info(f"Scraping: {profile_url}")
            
            response = self.session.get(profile_url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {profile_url}: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'lxml')
            html_text = response.text
            
            # Extract all information
            username = self._extract_username(profile_url, soup)
            education = self._extract_full_education(soup, html_text)
            jobs = self._extract_jobs(soup, html_text)
            estimated_age = self._calculate_age_from_education(education)
            
            result = {
                'username': username,
                'education': education,
                'colleges': [edu['school'] for edu in education if edu.get('school')],
                'jobs': jobs,
                'estimated_age': estimated_age,
                'profile_url': response.url,
            }
            
            logger.info(f"Scraped: username={username}, education={len(education)}, jobs={len(jobs)}, age≈{estimated_age}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {profile_url}: {e}")
            return None
    
    def _extract_username(self, url: str, soup: BeautifulSoup) -> str:
        """Extract LinkedIn username"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if 'in' in path_parts:
            idx = path_parts.index('in')
            if idx + 1 < len(path_parts):
                return path_parts[idx + 1].split('?')[0].split('#')[0]
        
        return "Unknown"
    
    def _extract_full_education(self, soup: BeautifulSoup, html_text: str) -> List[Dict[str, Any]]:
        """Extract ALL education from JSON-LD structured data + regex fallback"""
        import json
        education_list = []
        json_ld_found = False
        
        # METHOD 1: Parse JSON-LD script tags properly
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                
                # Handle @graph structure
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'Person' and 'alumniOf' in item:
                            json_ld_found = True
                            for edu in item['alumniOf']:
                                school_name = edu.get('name', '').strip()
                                member = edu.get('member', {})
                                start = member.get('startDate', '')
                                end = member.get('endDate', '')
                                
                                start_year = int(start) if isinstance(start, int) or (isinstance(start, str) and start.isdigit()) else None
                                end_year = int(end) if isinstance(end, int) or (isinstance(end, str) and end.isdigit()) else None
                                
                                # Handle empty/hidden school names
                                if school_name and '***' not in school_name:
                                    education_list.append({
                                        'school': school_name,
                                        'degree': '',
                                        'field': '',
                                        'start_year': start_year,
                                        'end_year': end_year,
                                    })
                                else:
                                    # School name hidden - still record the years
                                    education_list.append({
                                        'school': '[School name hidden by LinkedIn]',
                                        'degree': '',
                                        'field': '',
                                        'start_year': start_year,
                                        'end_year': end_year,
                                    })
                                    
                # Handle direct alumniOf on Person
                elif data.get('@type') == 'Person' and 'alumniOf' in data:
                    json_ld_found = True
                    for edu in data['alumniOf']:
                        school_name = edu.get('name', '').strip()
                        member = edu.get('member', {})
                        start = member.get('startDate', '')
                        end = member.get('endDate', '')
                        
                        start_year = int(start) if isinstance(start, int) or (isinstance(start, str) and start.isdigit()) else None
                        end_year = int(end) if isinstance(end, int) or (isinstance(end, str) and end.isdigit()) else None
                        
                        if school_name and '***' not in school_name:
                            education_list.append({
                                'school': school_name,
                                'degree': '',
                                'field': '',
                                'start_year': start_year,
                                'end_year': end_year,
                            })
                        else:
                            education_list.append({
                                'school': '[School name hidden by LinkedIn]',
                                'degree': '',
                                'field': '',
                                'start_year': start_year,
                                'end_year': end_year,
                            })
            except (json.JSONDecodeError, TypeError, AttributeError):
                continue
        
        # METHOD 2: Regex fallback for visible text (ONLY if JSON-LD didn't work)
        if not json_ld_found:
            patterns = [
                r'([A-Z][a-zA-Z\s&\'\.]{5,50}(?:University|College|Institute|School)(?:\s+of\s+[A-Z][a-zA-Z\s&\'\.]{3,40})?)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_text)
                for school in matches:
                    school = school.strip()
                    if 10 < len(school) < 100 and 'LinkedIn' not in school:
                        education_list.append({
                            'school': school,
                            'degree': '',
                            'field': '',
                            'start_year': None,
                            'end_year': None,
                        })
        
        # Remove duplicates
        seen = set()
        unique_education = []
        for edu in education_list:
            school_key = edu['school'].lower()
            if school_key not in seen:
                seen.add(school_key)
                unique_education.append(edu)
        
        logger.info(f"Extracted {len(unique_education)} unique education entries")
        return unique_education
    
    def _extract_jobs(self, soup: BeautifulSoup, html_text: str) -> List[Dict[str, Any]]:
        """Extract work experience"""
        jobs = []
        
        # Pattern: Job title at Company
        job_pattern = re.compile(
            r'((?:[A-Z][a-z]+\s+){1,4}(?:Engineer|Manager|Director|Developer|Designer|Analyst|Consultant|Specialist|Lead|Officer|Executive|President|VP|CEO|CTO|CFO))'
            r'\s+at\s+'
            r'((?:[A-Z][a-z]+\s*){1,4}(?:Inc|LLC|Corp|Company|Ltd)?)',
            re.MULTILINE
        )
        
        for match in job_pattern.finditer(html_text):
            title = match.group(1).strip()
            company = match.group(2).strip()
            
            jobs.append({
                'title': title,
                'company': company,
                'start_year': None,
                'end_year': None,
            })
        
        # Pattern: Years at job
        year_pattern = re.compile(
            r'(\d{4})\s*[-–]\s*(\d{4}|Present)',
            re.MULTILINE
        )
        
        years = year_pattern.findall(html_text)
        for i, (start, end) in enumerate(years[:len(jobs)]):
            if i < len(jobs):
                jobs[i]['start_year'] = int(start) if start.isdigit() else None
                jobs[i]['end_year'] = int(end) if end.isdigit() else 2025 if end == 'Present' else None
        
        # Remove duplicates
        seen = set()
        unique_jobs = []
        for job in jobs:
            job_key = (job['title'].lower(), job['company'].lower())
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        return unique_jobs[:10]  # Limit to 10
    
    def _calculate_age_from_education(self, education: List[Dict[str, Any]]) -> Optional[int]:
        """Calculate estimated age from graduation year"""
        current_year = datetime.now().year
        
        # Find the most recent graduation year
        grad_years = [edu['end_year'] for edu in education if edu.get('end_year')]
        
        if not grad_years:
            return None
        
        # Most recent graduation
        latest_grad = max(grad_years)
        
        # Estimate: graduated at ~22 for bachelor's, ~24 for master's
        # Check if master's degree
        has_masters = any('master' in edu.get('degree', '').lower() or 'mba' in edu.get('degree', '').lower() 
                         for edu in education)
        
        grad_age = 24 if has_masters else 22
        estimated_age = current_year - latest_grad + grad_age
        
        return estimated_age if 18 <= estimated_age <= 100 else None
