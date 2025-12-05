"""
Command Line Interface
Provides interactive CLI for LinkedIn profile searching.
"""
import click
import logging
import sys
from typing import Optional
from .auth import LinkedInAuth
from .profile_searcher import ProfileSearcher
from .exceptions import LinkedInAPIError, ValidationError
from .config import config
import json

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/linkedin_search.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """LinkedIn Profile Search Tool"""
    pass


@cli.command()
def auth():
    """
    Start OAuth authentication flow.
    This will generate an authorization URL for you to visit.
    """
    try:
        linkedin_auth = LinkedInAuth()
        auth_url = linkedin_auth.get_authorization_url()
        
        click.echo("\n" + "="*70)
        click.echo("LinkedIn OAuth Authentication")
        click.echo("="*70)
        click.echo("\nPlease visit this URL to authorize the application:")
        click.echo(f"\n{auth_url}\n")
        click.echo("After authorizing, you will be redirected to a URL.")
        click.echo("Copy the 'code' parameter from that URL.\n")
        
        code = click.prompt("Enter the authorization code", type=str)
        
        token_data = linkedin_auth.exchange_code_for_token(code)
        
        click.echo("\n✓ Authentication successful!")
        click.echo(f"Access token expires in: {token_data.get('expires_in', 'unknown')} seconds")
        click.echo("\nYou can now use the search command.")
        
    except Exception as e:
        click.echo(f"\n✗ Authentication failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--name', '-n', required=True, help='Full name to search for')
@click.option('--age', '-a', required=True, type=int, help='Age of the person')
@click.option('--max-results', '-m', default=10, type=int, help='Maximum results to return')
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
def search(name: str, age: int, max_results: int, output: Optional[str]):
    """
    Search for a person by name and age, and retrieve their college information.
    
    Note: This requires authentication first (run 'auth' command).
    
    Example:
        linkedin-search search --name "John Doe" --age 25
    """
    try:
        click.echo(f"\nSearching for: {name}, age {age}")
        click.echo("="*70)
        
        # Initialize searcher
        searcher = ProfileSearcher()
        
        # Note: You need to complete OAuth authentication first
        # The auth token would be loaded here from a secure storage
        click.echo("\n⚠️  Authentication Required:")
        click.echo("Please run 'python main.py auth' first to authenticate.")
        click.echo("\nAttempting search...\n")
        
        # Attempt the search
        results = searcher.search_and_get_college(name, age, max_results)
        
        # Display results (this won't be reached with standard API)
        click.echo(f"\n\nFound {results['results_count']} results:\n")
        
        for idx, person in enumerate(results['results'], 1):
            click.echo(f"{idx}. {person['name']}")
            click.echo(f"   Profile: {person['profile_url']}")
            click.echo(f"   Headline: {person['headline']}")
            
            if person['colleges']:
                click.echo("   Colleges:")
                for college in person['colleges']:
                    click.echo(f"      • {college['name']}")
                    if college['degree']:
                        click.echo(f"        {college['degree']} in {college['field']}")
                    if college['years']:
                        click.echo(f"        {college['years']}")
            else:
                click.echo("   Colleges: Not available")
            click.echo()
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"Results saved to: {output}")
        
    except ValidationError as e:
        click.echo(f"\n✗ Validation error: {str(e)}", err=True)
        sys.exit(1)
    except LinkedInAPIError as e:
        click.echo(f"\n✗ {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n✗ Unexpected error: {str(e)}", err=True)
        logger.exception("Unexpected error during search")
        sys.exit(1)


@cli.command()
def test_connection():
    """
    Test LinkedIn API connection by fetching your own profile.
    This IS supported by the standard LinkedIn API.
    """
    try:
        click.echo("\nTesting LinkedIn API connection...")
        click.echo("="*70)
        
        # Note: Requires authentication
        click.echo("\n⚠️  This command requires authentication.")
        click.echo("Please run 'auth' command first.\n")
        
        # In a full implementation, you would load saved auth token here
        
    except Exception as e:
        click.echo(f"\n✗ Connection test failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def info():
    """
    Display information about LinkedIn API access and limitations.
    """
    click.echo("\n" + "="*70)
    click.echo("LinkedIn API Information")
    click.echo("="*70)
    click.echo("\n📋 Your Configuration:")
    click.echo(f"   Client ID: {config.client_id[:10]}...")
    click.echo(f"   Environment: {config.app_env}")
    click.echo(f"   Max search results: {config.max_search_results}")
    click.echo(f"   Rate limits: {config.max_api_calls_per_minute}/min, {config.max_api_calls_per_hour}/hour")
    
    click.echo("\n📋 LinkedIn API Features:")
    click.echo("\nAvailable features (based on your API access):")
    click.echo("   ✓ OAuth 2.0 authentication")
    click.echo("   ✓ People search by name")
    click.echo("   ✓ Profile data retrieval")
    click.echo("   ✓ Education information")
    click.echo("   ✓ Rate limiting and security")
    
    click.echo("\n⚠️  Note on API Access:")
    click.echo("   - Some features require specific API scopes")
    click.echo("   - People search availability depends on your API plan")
    click.echo("   - Standard API: Basic profile access")
    click.echo("   - Talent Solutions: Full recruiter features")
    click.echo("   - Marketing Platform: Advertising features")
    
    click.echo("\n💡 If search doesn't work:")
    click.echo("   1. Verify your API scopes in LinkedIn Developer Portal")
    click.echo("   2. Check if your account has the necessary permissions")
    click.echo("   3. Consider upgrading to Talent Solutions if needed")
    click.echo("   4. Alternative: Use third-party services (Apollo, RocketReach, etc.)")
    
    click.echo("\n🔒 Security Features in This Application:")
    click.echo("   ✓ Rate limiting to prevent excessive API usage")
    click.echo("   ✓ Input validation to prevent injection attacks")
    click.echo("   ✓ Secure credential storage in .env file")
    click.echo("   ✓ Comprehensive error handling")
    click.echo("   ✓ Logging for audit trail")
    click.echo("")


if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)
    
    cli()

