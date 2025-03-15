import time
import logging
from functools import wraps
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import Unauthorized, Forbidden, TooManyRequests
from itsdangerous import URLSafeTimedSerializer
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['TOKEN_EXPIRATION'] = 3600  # Token expiration time in seconds
app.config['RATE_LIMIT'] = 5  # Maximum requests allowed per time interval
app.config['RATE_LIMIT_INTERVAL'] = 60  # Time interval in seconds

# Logger setup
logging.basicConfig(level=logging.INFO)

# Token serializer
token_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# In-memory storage for rate limits
rate_limits = defaultdict(list)

# Sample user database
users = {
    "user1": "password123",
    "user2": "mypassword",
}

def generate_token(username):
    return token_serializer.dumps(username)

def verify_token(token):
    try:
        username = token_serializer.loads(token, max_age=app.config['TOKEN_EXPIRATION'])
        return username
    except Exception as e:
        app.logger.warning(f"Token verification failed: {e}")
        return None

def rate_limit_exceeded(username):
    current_time = time.time()
    # Clean up old timestamps
    rate_limits[username] = [timestamp for timestamp in rate_limits[username] if current_time - timestamp < app.config['RATE_LIMIT_INTERVAL']]
    
    # Check if rate limit exceeded
    if len(rate_limits[username]) >= app.config['RATE_LIMIT']:
        return True
    
    rate_limits[username].append(current_time)
    return False

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            raise Unauthorized('Token is missing')
        
        username = verify_token(token)
        if not username:
            raise Unauthorized('Invalid token')
        
        if rate_limit_exceeded(username):
            raise TooManyRequests('Rate limit exceeded')
        
        g.user = username
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(Unauthorized)
def handle_unauthorized(e):
    return jsonify(error=str(e)), 401

@app.errorhandler(Forbidden)
def handle_forbidden(e):
    return jsonify(error=str(e)), 403

@app.errorhandler(TooManyRequests)
def handle_too_many_requests(e):
    return jsonify(error=str(e)), 429

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    username = auth.get('username')
    password = auth.get('password')

    if users.get(username) == password:
        token = generate_token(username)
        return jsonify(token=token), 200
    else:
        return jsonify(error='Invalid credentials'), 401

@app.route('/secure-endpoint', methods=['GET'])
@auth_required
def secure_endpoint():
    return jsonify(message=f'Hello, {g.user}! You have accessed a secure endpoint.'), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify(status='API is running'), 200

@app.route('/logout', methods=['POST'])
@auth_required
def logout():
    # Logout logic can be added here (e.g., blacklisting the token)
    return jsonify(message=f'Goodbye, {g.user}!'), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)