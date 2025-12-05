"""Circuit demo web app. Flow: signup -> game1 -> game2 -> game3 -> reveal"""
import os
import logging
import secrets
import threading
import hashlib
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from typing import Optional, Dict, Any

from .ai_search import ClaudeSearcher as DeepSeekSearcher
from .config import config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Prediction cache
MAX_CACHE = 1000
predictions_cache: Dict[str, Dict[str, Any]] = {}
cache_lock = threading.Lock()


def get_api_key():
    return os.getenv('ANTHROPIC_API_KEY')


def sanitize(text: str) -> str:
    for char in ['<', '>', '"', "'", '&', '\\', '\x00']:
        text = text.replace(char, '')
    return text.strip()[:200]


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:16]


def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def cleanup_cache():
    with cache_lock:
        if len(predictions_cache) > MAX_CACHE:
            items = list(predictions_cache.items())
            for key, _ in items[:100]:
                del predictions_cache[key]


def store_prediction(token_hash: str, prediction: Dict[str, Any]):
    cleanup_cache()
    with cache_lock:
        predictions_cache[token_hash] = prediction


def get_prediction(token_hash: str) -> Optional[Dict[str, Any]]:
    with cache_lock:
        return predictions_cache.get(token_hash)


def start_background_prediction(token_hash: str, name: str, age: int, location: str):
    def run():
        try:
            api_key = get_api_key()
            if not api_key:
                logger.error("No API key!")
                store_prediction(token_hash, {
                    'college': 'API key not set',
                    'career': 'Unknown',
                    'personality': 'Unknown',
                    'confidence': 0,
                    'error': 'ANTHROPIC_API_KEY not set'
                })
                return
            
            logger.info(f"Starting prediction for {name}...")
            searcher = DeepSeekSearcher(api_key)
            result = searcher.search_person(name, age, location)
            store_prediction(token_hash, result)
            logger.info(f"Prediction complete: {result.get('college')}, confidence: {result.get('confidence')}")
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            store_prediction(token_hash, {
                'college': 'Error',
                'career': 'Unknown', 
                'personality': 'Unknown',
                'confidence': 0,
                'error': str(e)
            })
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()


@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://api.fontshare.com; "
        "font-src 'self' https://cdn.fontshare.com; "
        "connect-src 'self' http://ip-api.com"
    )
    return response


@app.route('/')
def index():
    return redirect(url_for('circuit_index'))


@app.route('/circuit')
def circuit_index():
    return render_template('circuit_index.html')


@app.route('/circuit/demo')
def circuit_demo():
    return render_template('circuit_demo.html')


@app.route('/circuit/about')
def circuit_about():
    return render_template('circuit_about.html')


@app.route('/circuit/how-it-works')
def circuit_how_it_works():
    return render_template('circuit_how_it_works.html')


@app.route('/circuit/research')
def circuit_research():
    return render_template('circuit_research.html')


@app.route('/circuit/careers')
def circuit_careers():
    return render_template('circuit_careers.html')


@app.route('/circuit/contact')
def circuit_contact():
    return render_template('circuit_contact.html')


@app.route('/circuit/safety')
def circuit_safety():
    return render_template('circuit_safety.html')


@app.route('/circuit/guidelines')
def circuit_guidelines():
    return render_template('circuit_guidelines.html')


@app.route('/circuit/help')
def circuit_help():
    return render_template('circuit_help.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    try:
        first_name = sanitize(request.form.get('first_name', '').strip())
        last_name = sanitize(request.form.get('last_name', '').strip())
        dob_str = request.form.get('dob', '').strip()
        location = sanitize(request.form.get('location', '').strip())
        agree_terms = request.form.get('agree_terms')
        confirm_age = request.form.get('confirm_age')
        
        # Validate
        if not first_name or len(first_name) < 1:
            flash('Please enter your first name.', 'error')
            return render_template('signup.html')
        
        if not last_name or len(last_name) < 1:
            flash('Please enter your last name.', 'error')
            return render_template('signup.html')
        
        if not dob_str:
            flash('Please enter your date of birth.', 'error')
            return render_template('signup.html')
        
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            age = calculate_age(dob)
            if age < 18:
                flash('You must be at least 18 years old.', 'error')
                return render_template('signup.html')
            if age > 120:
                flash('Please enter a valid date of birth.', 'error')
                return render_template('signup.html')
        except ValueError:
            flash('Please enter a valid date of birth.', 'error')
            return render_template('signup.html')
        
        if not location or len(location) < 3:
            flash('Location is required.', 'error')
            return render_template('signup.html')
        
        if not agree_terms:
            flash('You must agree to the Terms of Service.', 'error')
            return render_template('signup.html')
        
        if not confirm_age:
            flash('You must confirm you are at least 18 years old.', 'error')
            return render_template('signup.html')
        
        # Combine name
        full_name = f"{first_name} {last_name}"
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        token_hash = hash_token(session_token)
        
        session['user_data'] = {
            'name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'location': location
        }
        session['session_token'] = session_token
        session['games_completed'] = 0
        session.permanent = True
        
        # Start prediction in background
        start_background_prediction(token_hash, full_name, age, location)
        
        logger.info(f"User signed up: {full_name}, age {age}")
        return redirect(url_for('game1'))
        
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        flash('An error occurred.', 'error')
        return render_template('signup.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/game/1')
def game1():
    # Allow game access - session will be created if needed
    if 'user_data' not in session:
        session['user_data'] = {'name': 'Demo User', 'first_name': 'Demo', 'age': 20, 'location': 'Unknown'}
        session['session_token'] = secrets.token_urlsafe(16)
        session['games_completed'] = 0
        session.permanent = True
    return render_template('game1.html', game_num=1, session_token=session.get('session_token', ''))


@app.route('/game/1/complete', methods=['POST'])
def game1_complete():
    session['games_completed'] = 1
    session.modified = True
    return redirect(url_for('game2'))


@app.route('/game/2')
def game2():
    if 'user_data' not in session:
        return redirect(url_for('game1'))
    return render_template('game2.html', game_num=2, session_token=session.get('session_token', ''))


@app.route('/game/2/complete', methods=['POST'])
def game2_complete():
    session['games_completed'] = 2
    session.modified = True
    return redirect(url_for('game3'))


@app.route('/game/3')
def game3():
    if 'user_data' not in session:
        return redirect(url_for('game1'))
    return render_template('game3.html', game_num=3, session_token=session.get('session_token', ''))


@app.route('/game/3/complete', methods=['POST'])
def game3_complete():
    session['games_completed'] = 3
    session.modified = True
    return redirect(url_for('reveal'))


@app.route('/reveal')
def reveal():
    if 'user_data' not in session:
        session['user_data'] = {'name': 'Demo User', 'first_name': 'Demo', 'age': 20, 'location': 'Unknown'}
        session['session_token'] = secrets.token_urlsafe(16)
    
    user_data = session['user_data']
    token_hash = hash_token(session.get('session_token', ''))
    first_name = user_data.get('first_name', user_data.get('name', 'User').split()[0])
    
    # Wait for prediction (max 5 seconds)
    import time
    prediction = None
    for _ in range(10):
        prediction = get_prediction(token_hash)
        if prediction:
            break
        time.sleep(0.5)
    
    if not prediction:
        prediction = {
            'college': 'Demo Mode - No prediction available',
            'career': 'Unknown',
            'personality': 'Unknown',
            'confidence': 0
        }
    
    return render_template('reveal.html',
                         prediction=prediction,
                         user_name=first_name,
                         session_token=session.get('session_token', ''))


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    return redirect(url_for('complete'))


@app.route('/complete')
def complete():
    return render_template('complete.html')


@app.route('/log-result', methods=['POST'])
def log_result():
    return jsonify({'status': 'ok'})


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'api_key_set': bool(get_api_key())
    })


@app.route('/test')
def test_page():
    return render_template('test_search.html')


@app.route('/api/test-search', methods=['POST'])
def api_test_search():
    data = request.get_json()
    name = data.get('name', '')
    age = data.get('age')
    location = data.get('location', '')
    
    api_key = get_api_key()
    if not api_key:
        return jsonify({'error': 'No API key'}), 500
    
    searcher = DeepSeekSearcher(api_key)
    result = searcher.search_person(name, age, location)
    
    return jsonify(result)


def run_app(host='127.0.0.1', port=2404, debug=False):
    logger.info(f"Starting blackmagic on {host}:{port}")
    
    api_key = get_api_key()
    if api_key:
        logger.info(f"API key: {api_key[:10]}...")
    else:
        logger.warning("No ANTHROPIC_API_KEY set!")
    
    os.makedirs('logs', exist_ok=True)
    os.makedirs('flask_session', exist_ok=True)
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_app(debug=True)
