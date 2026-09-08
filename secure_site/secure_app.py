from flask import Flask, render_template, request, redirect, session, abort
import mysql.connector
import bcrypt
import re
import secrets
import logging
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "a3f8#kL9!mZ2@qR7$nX4&wV6"  # SECURE: strong random secret key

# SECURE: Cookie protection
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# SECURE: Logging setup
logging.basicConfig(
    filename='security.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="babamama",  # your MySQL password
        database="smartnest_secure"
    )

# SECURE: File Upload — strict validation
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB max

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── HOME ──────────────────────────────────────────
@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")  # safe, no user input
    products = cursor.fetchall()
    return render_template('home.html', products=products)

# ── LOGIN ─────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # SECURE FIX A07: Brute force protection
        if 'failed_attempts' not in session:
            session['failed_attempts'] = 0

        if session['failed_attempts'] >= 5:
            error = "Too many failed attempts. Try again later."
            logging.warning(f"Brute force detected for: {username}")
            return render_template('login.html', error=error)

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # SECURE FIX A03: Parameterized query
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # SECURE FIX A02: bcrypt password check
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['failed_attempts'] = 0
            session['user_id'] = user['id']
            session['user'] = user['username']
            session['role'] = user['role']
            session['csrf_token'] = secrets.token_hex(32)
            logging.info(f"Successful login: {username}")
            return redirect('/')
        else:
            session['failed_attempts'] += 1
            remaining = 5 - session['failed_attempts']
            error = f"Invalid credentials. {remaining} attempts remaining."
            logging.warning(f"Failed login for: {username}")

    return render_template('login.html', error=error)

# ── REGISTER ──────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']

        # SECURE FIX 3: Input validation
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            error = "Username must be 3-20 characters, letters/numbers only."
            return render_template('register.html', error=error)

        if len(password) < 8:
            error = "Password must be at least 8 characters."
            return render_template('register.html', error=error)

        # SECURE FIX 4: Hash password with bcrypt before storing
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')",
            (username, email, hashed.decode('utf-8'))
        )
        db.commit()
        return redirect('/login')

    return render_template('register.html', error=error)

# ── LOGOUT ────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# SECURE: CSRF token protected
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect('/login')

    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)

    message = None
    error = None

    if request.method == 'POST':
        token_from_form = request.form.get('csrf_token', '')
        token_from_session = session.get('csrf_token', '')

        # SECURE FIX: Validate CSRF token
        if not secrets.compare_digest(token_from_form, token_from_session):
            error = "CSRF Attack Detected! Invalid token — request blocked."
            logging.warning(f"CSRF attack blocked for: {session.get('user')}")
        else:
            new_password = request.form['new_password']

            if len(new_password) < 8:
                error = "Password must be at least 8 characters."
            else:
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                db = get_db()
                cursor = db.cursor()
                cursor.execute("UPDATE users SET password=%s WHERE username=%s",
                               (hashed.decode('utf-8'), session['user']))
                db.commit()
                session['csrf_token'] = secrets.token_hex(32)
                message = "Password changed successfully!"
                logging.info(f"Password changed for: {session.get('user')}")

    elif request.method == 'GET' and request.args.get('new_password'):
        error = "Invalid request! GET method not allowed."
        logging.warning(f"GET CSRF attempt blocked for: {session.get('user')}")

    return render_template('change_password.html',
                           message=message,
                           error=error,
                           csrf_token=session.get('csrf_token'))


# SECURE: Path Traversal fixed
@app.route('/product-image')
def product_image():
    filename = request.args.get('file', '')

    # SECURE FIX: Validate filename — no ../ allowed
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        logging.warning(f"Path traversal attempt: {filename}")
        return render_template('file_viewer.html',
                               filename=filename,
                               content='Access Denied! Path traversal detected.')

    # SECURE FIX: Only allow image extensions
    allowed = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(filename.endswith(ext) for ext in allowed):
        return render_template('file_viewer.html',
                               filename=filename,
                               content='Access Denied! Only image files allowed.')

    # SECURE FIX: Use safe base directory
    base_dir = os.path.abspath('static')
    filepath  = os.path.abspath(os.path.join(base_dir, filename))

    # SECURE FIX: Make sure final path is still inside static/
    if not filepath.startswith(base_dir):
        logging.warning(f"Path traversal blocked: {filepath}")
        return render_template('file_viewer.html',
                               filename=filename,
                               content='Access Denied! Outside allowed directory.')

    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return render_template('file_viewer.html',
                               filename=filename,
                               content=content)
    except Exception:
        return render_template('file_viewer.html',
                               filename=filename,
                               content='File not found!')

# ── PROFILE ───────────────────────────────────────
@app.route('/profile/<int:user_id>')
def profile(user_id):
    # SECURE FIX 5: IDOR fixed — only allow access to YOUR OWN profile
    if 'user_id' not in session:
        return redirect('/login')

    if session['user_id'] != user_id and session.get('role') != 'admin':
        abort(403)  # Forbidden — you can't view someone else's profile

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('profile.html', user=user)

# ── ADMIN ─────────────────────────────────────────
@app.route('/admin')
def admin():
    # SECURE FIX 6: Broken Access Control fixed — check role before allowing access
    if 'user' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        abort(403)  # Only admins can access this

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role FROM users")  # never return passwords
    users = cursor.fetchall()
    return render_template('admin.html', users=users)

# ── SEARCH ────────────────────────────────────────
@app.route('/search')
def search():
    query = request.args.get('q', '')

    # SECURE FIX 7: Input sanitized — strip HTML tags
    query = re.sub(r'<[^>]+>', '', query)
    query = query[:100]  # limit input length

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE name LIKE %s", ('%' + query + '%',))
    results = cursor.fetchall()

    # SECURE: query passed as plain variable, Jinja2 auto-escapes it (no | safe)
    return render_template('search.html', query=query, results=results)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    message = None
    uploaded_file = None
    error = None

    if request.method == 'POST':
        if 'file' not in request.files:
            error = "No file selected!"
        else:
            file = request.files['file']

            if file.filename == '':
                error = "No file selected!"

            # SECURE FIX 1: Check file extension
            elif not allowed_file(file.filename):
                error = "File type not allowed! Only PNG, JPG, GIF, WEBP allowed."
                logging.warning(f"Blocked upload attempt: {file.filename} by {session.get('user')}")

            else:
                # SECURE FIX 2: Sanitize filename — removes ../ and special chars
                filename = secure_filename(file.filename)

                # SECURE FIX 3: Check file size
                file.seek(0, 2)
                size = file.tell()
                file.seek(0)

                if size > MAX_FILE_SIZE:
                    error = "File too large! Maximum 2MB allowed."
                else:
                    # SECURE FIX 4: Check actual file content (magic bytes)
                    header = file.read(8)
                    file.seek(0)

                    # PNG magic bytes: 89 50 4E 47
                    # JPG magic bytes: FF D8 FF
                    # GIF magic bytes: 47 49 46 38
                    # WEBP magic bytes: 52 49 46 46
                    is_image = (
                        header[:4] == b'\x89PNG' or
                        header[:3] == b'\xff\xd8\xff' or
                        header[:6] in (b'GIF87a', b'GIF89a') or
                        header[:4] == b'RIFF'
                    )

                    if not is_image:
                        error = "File content does not match image type! Upload rejected."
                        logging.warning(f"Magic byte check failed: {filename} by {session.get('user')}")
                    else:
                        upload_folder = os.path.join('static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)
                        uploaded_file = filename
                        message = f"Image uploaded successfully!"
                        logging.info(f"File uploaded: {filename} by {session.get('user')}")

    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    uploaded_files = os.listdir(upload_folder)

    return render_template('upload.html',
                           message=message,
                           error=error,
                           uploaded_file=uploaded_file,
                           uploaded_files=uploaded_files)


# ── 403 ERROR PAGE ────────────────────────────────
@app.errorhandler(403)
def forbidden(e):
    return render_template('4.3.html'), 403

print(">>> About to start Flask server on port 5001...")
if __name__ == '__main__':
    app.run(debug=True, port=5001)