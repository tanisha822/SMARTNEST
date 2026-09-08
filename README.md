# CyberNest — OWASP Top 10 Vulnerability Demo Platform
### A Professional Cybersecurity Education Project

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Complete Setup Guide](#3-complete-setup-guide)
4. [Database Setup](#4-database-setup)
5. [Project File Structure](#5-project-file-structure)
6. [All Vulnerabilities — Code Difference & Explanation](#6-all-vulnerabilities)
7. [Complete Attack Guide — All Payloads](#7-complete-attack-guide)
8. [Security Fixes Summary](#8-security-fixes-summary)
9. [Testing Checklist](#9-testing-checklist)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Project Overview

**CyberNest** is a dual-website cybersecurity education platform built to demonstrate the OWASP Top 10 web vulnerabilities. The project consists of two websites with identical UI but completely different backends:

| Feature | Vulnerable Site | Secure Site |
|---|---|---|
| Port | 5000 | 5001 |
| Database | smartnest | smartnest_secure |
| Passwords | Plain text | bcrypt hashed |
| SQL Queries | String formatted | Parameterized |
| Debug Mode | ON | OFF |
| Session Cookie | SameSite=None | SameSite=Strict |
| CSRF Protection | None | Token validated |
| Access Control | None | Role checked |
| Input Validation | None | Sanitized |
| Logging | None | Full audit log |

### Tech Stack

- **Backend:** Python 3.x + Flask
- **Database:** MySQL
- **Frontend:** HTML5 + CSS3 + JavaScript + Bootstrap 5
- **Password Hashing:** bcrypt
- **Fonts:** Rajdhani, DM Sans, JetBrains Mono

---

## 2. Architecture

```
SMARTNEST/
│
├── vulnerable_site/              ← Port 5000 — intentionally weak
│   ├── app.py                    ← All 10 vulnerabilities here
│   ├── static/
│   │   └── uploads/              ← Uploaded files (no restriction)
│   └── templates/
│       ├── base.html             ← Shared UI layout
│       ├── home.html             ← Product listing
│       ├── login.html            ← SQL injectable login
│       ├── register.html         ← No validation
│       ├── profile.html          ← IDOR vulnerable
│       ├── admin.html            ← No access control
│       ├── search.html           ← XSS vulnerable
│       ├── change_password.html  ← CSRF vulnerable
│       ├── upload.html           ← Unrestricted upload
│       └── file_viewer.html      ← Path traversal
│
├── secure_site/                  ← Port 5001 — fully secured
│   ├── secure_app.py             ← All 10 fixes here
│   ├── security.log              ← Audit log (auto-created)
│   ├── static/
│   │   └── uploads/              ← Only verified images
│   └── templates/
│       ├── (same HTML files)     ← Identical UI
│       └── 4.3.html              ← 403 error page
│ 
├── csrf_attack.html              ← CSRF demo attack page
├── hash_passwords.py             ← Password hashing utility
├── requirements.txt              ← All dependencies
└── README.md                     ← This file
```

---

## 3. Complete Setup Guide

### Prerequisites

Install these before starting:

| Tool | Download |
|---|---|
| Python 3.10+ | https://python.org/downloads |
| MySQL Server | https://dev.mysql.com/downloads/mysql |
| MySQL Workbench | https://dev.mysql.com/downloads/workbench |
| VS Code | https://code.visualstudio.com |
| Git (optional) | https://git-scm.com |

---

### Step 1 — Clone or Download Project

```bash
# Option A: If using Git
git clone https://github.com/yourusername/cybernest.git
cd cybernest

# Option B: Download ZIP and extract to a folder
cd "C:\path\to\SMARTNEST"
```

---

### Step 2 — Install All Dependencies

```bash
# Install everything from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list
```

Expected output includes: flask, mysql-connector-python, bcrypt, werkzeug

---

### Step 3 — Start MySQL Server

Open **MySQL Workbench** and connect to `localhost:3306` with your root credentials.

If MySQL is not running, start it via Windows Services or run:
```bash
net start MySQL80
```

---

### Step 4 — Create Databases and Tables

Open MySQL Workbench → New Query tab → paste and run:

```sql
-- ═══════════════════════════════════════
-- VULNERABLE SITE DATABASE
-- ═══════════════════════════════════════
CREATE DATABASE IF NOT EXISTS smartnest;
USE smartnest;

CREATE TABLE IF NOT EXISTS users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email    VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    role     VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    price       DECIMAL(10,2),
    image       VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS orders (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT,
    product_id INT,
    quantity   INT,
    total      DECIMAL(10,2)
);

-- Insert plain text users (vulnerable site)
INSERT INTO users (username, email, password, role) VALUES
('admin', 'admin@smartnest.com', 'admin123', 'admin'),
('john',  'john@gmail.com',      'john123',  'user'),
('user',  'user@gmail.com',      'user123',  'user'),
('sahoo', 'sahoo@gmail.com',     'sahoo123', 'user');

-- Insert sample products
INSERT INTO products (name, description, price, image) VALUES
('Smart Thermostat',    'Control your home temperature remotely', 2999.00, 'thermostat.jpg'),
('Security Camera',     'HD indoor/outdoor camera',               1999.00, 'camera.jpg'),
('Smart Lock',          'Keyless entry for your home',            3499.00, 'lock.jpg'),
('USB Rubber Ducky',    'Keystroke injection device',             6499.00, 'usb.jpg'),
('WiFi Pineapple',      'Wireless network auditing tool',        14999.00, 'wifi.jpg'),
('YubiKey 5 NFC',       'Hardware security key',                  4299.00, 'yubikey.jpg'),
('HackRF One',          'Software defined radio',                18999.00, 'hackrf.jpg'),
('Flipper Zero',        'Multi-tool hacker device',              22999.00, 'flipper.jpg'),
('IronKey USB 128GB',   'Encrypted USB drive',                    8499.00, 'ironkey.jpg'),
('Reolink 4K Camera',   'PoE IP security camera',                 5999.00, 'reolink.jpg');

-- ═══════════════════════════════════════
-- SECURE SITE DATABASE
-- ═══════════════════════════════════════
CREATE DATABASE IF NOT EXISTS smartnest_secure;
USE smartnest_secure;

CREATE TABLE IF NOT EXISTS users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email    VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    role     VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    price       DECIMAL(10,2),
    image       VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS orders (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT,
    product_id INT,
    quantity   INT,
    total      DECIMAL(10,2)
);

-- Copy products to secure DB
INSERT INTO smartnest_secure.products SELECT * FROM smartnest.products;
```

---

### Step 5 — Generate Hashed Passwords for Secure Site

Open terminal in project folder and run:

```bash
python -c "
import bcrypt
users = [
    ('admin', 'admin123', 'admin'),
    ('john',  'john123',  'user'),
    ('user',  'user123',  'user'),
    ('sahoo', 'sahoo123', 'user')
]
for u, p, r in users:
    h = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
    print(f'INSERT INTO smartnest_secure.users (username,email,password,role) VALUES (\"{u}\",\"{u}@gmail.com\",\"{h}\",\"{r}\");')
"
```

Copy the output and run it in MySQL Workbench.

---

### Step 6 — Configure Database Connection

In `vulnerable_site/app.py` find and update:

```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD_HERE",  # ← change this
        database="smartnest"
    )
```

In `secure_site/secure_app.py` find and update:

```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD_HERE",  # ← change this
        database="smartnest_secure"
    )
```

---

### Step 7 — Run Both Sites

Open **two separate terminals** in VS Code (`Ctrl + Shift + \``):

```bash
# Terminal 1 — Vulnerable Site
cd vulnerable_site
python app.py
# Opens at http://localhost:5000
```

```bash
# Terminal 2 — Secure Site
cd secure_site
python secure_app.py
# Opens at http://localhost:5001
```

---

### Step 8 — Verify Everything Works

| URL | Expected Result |
|---|---|
| http://localhost:5000 | CyberNest home with products |
| http://localhost:5000/login | Login page with demo credentials |
| http://localhost:5000/admin | Admin panel (no login needed — vulnerability!) |
| http://localhost:5001 | Same UI — secure version |
| http://localhost:5001/admin | Redirects to login — secured! |

---

### Step 9 — Setup CSRF Attack Server

```bash
# Terminal 3 — serves the CSRF attack page
cd "C:\path\to\SMARTNEST"
python -m http.server 9999
# CSRF attack page at http://localhost:9999/csrf_attack.html
```

---

## 4. Database Setup

### Vulnerable Site — `smartnest`

Stores **plain text passwords** intentionally:

```sql
SELECT * FROM smartnest.users;
-- Shows: admin | admin123 | admin  ← plain text visible!
```

### Secure Site — `smartnest_secure`

Stores **bcrypt hashed passwords**:

```sql
SELECT * FROM smartnest_secure.users;
-- Shows: admin | $2b$12$xxxxx... | admin  ← hash only!
```

### Reset Passwords After Testing

```sql
-- Reset vulnerable site passwords
SET SQL_SAFE_UPDATES = 0;
USE smartnest;
UPDATE users SET password='admin123' WHERE username='admin';
UPDATE users SET password='john123'  WHERE username='john';
UPDATE users SET password='user123'  WHERE username='user';
UPDATE users SET password='sahoo123' WHERE username='sahoo';
SET SQL_SAFE_UPDATES = 1;
```

---

## 5. Project File Structure

```
SMARTNEST/
├── vulnerable_site/
│   ├── app.py
│   ├── static/uploads/
│   └── templates/
│       ├── base.html
│       ├── home.html
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       ├── admin.html
│       ├── search.html
│       ├── change_password.html
│       ├── upload.html
│       └── file_viewer.html
│
├── secure_site/
│   ├── secure_app.py
│   ├── security.log
│   ├── static/uploads/
│   └── templates/
│       ├── (all same html files)
│       └── 4.3.html
│
├── csrf_attack.html
├── hash_passwords.py
├── requirements.txt
└── README.md
```

---

## 6. All Vulnerabilities

### VULN-01 — SQL Injection (OWASP A03)

**What:** Attacker injects SQL code into login form to bypass authentication.

**Vulnerable Code (`app.py` line ~38):**
```python
# DANGEROUS: User input directly in SQL string
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
cursor.execute(query)
```

**Why it happens:** Python f-string puts user input directly into SQL query. When user types `admin' --` the query becomes:
```sql
SELECT * FROM users WHERE username='admin' --' AND password='anything'
-- Everything after -- is a comment — password check is skipped!
```

**Secure Code (`secure_app.py`):**
```python
# SAFE: Parameterized query — input never becomes SQL code
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

**Why fix works:** The `%s` placeholder tells MySQL driver to treat the value as data, never as SQL code. Injection characters are escaped automatically.

---

### VULN-02 — Cryptographic Failure / Plain Text Passwords (OWASP A02)

**What:** Passwords stored as plain text in database — one breach exposes everyone.

**Vulnerable Code:**
```python
# DANGEROUS: Stores password exactly as typed
cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')",
               (username, email, password))  # password = "john123"
```

**Secure Code:**
```python
# SAFE: Hash password before storing
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
cursor.execute("INSERT INTO users ...", (username, email, hashed.decode('utf-8')))
# Stored: "$2b$12$xxxxxxxxxxxxx..." — irreversible hash
```

**Why fix works:** bcrypt is a one-way hash. Even if database is stolen, attacker cannot reverse `$2b$12$...` back to `john123`. Verification uses `bcrypt.checkpw()` which compares hash without reversing.

---

### VULN-03 — Broken Access Control — Admin Panel (OWASP A01)

**What:** Anyone can access admin panel without logging in.

**Vulnerable Code:**
```python
@app.route('/admin')
def admin():
    # NO CHECKS AT ALL — anyone can access!
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return render_template('admin.html', users=users)
```

**Secure Code:**
```python
@app.route('/admin')
def admin():
    # CHECK 1: Must be logged in
    if 'user' not in session:
        return redirect('/login')
    # CHECK 2: Must be admin role
    if session.get('role') != 'admin':
        abort(403)
    # CHECK 3: Never return password field
    cursor.execute("SELECT id, username, email, role FROM users")
```

---

### VULN-04 — IDOR (Insecure Direct Object Reference) (OWASP A01)

**What:** Changing user ID in URL lets attacker view any user's profile.

**Vulnerable Code:**
```python
@app.route('/profile/<int:user_id>')
def profile(user_id):
    # NO OWNERSHIP CHECK — fetches any user ID requested!
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('profile.html', user=user)
    # Template shows: username, email, PASSWORD, role
```

**Secure Code:**
```python
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        return redirect('/login')
    # Only allow own profile OR admin viewing any profile
    if session['user_id'] != user_id and session.get('role') != 'admin':
        abort(403)
    # Never return password field
    cursor.execute("SELECT id, username, email, role FROM users WHERE id = %s", (user_id,))
```

---

### VULN-05 — XSS Cross Site Scripting (OWASP A03)

**What:** Attacker injects JavaScript into search — runs in victim's browser.

**Vulnerable Code (`search.html`):**
```html
<!-- DANGEROUS: | safe tells Jinja2 to render raw HTML -->
<p>Results for: <span>{{ query | safe }}</span></p>
```

**Secure Code:**
```html
<!-- SAFE: No | safe filter — Jinja2 auto-escapes HTML characters -->
<p>Results for: <span>{{ query }}</span></p>
```

**Also in secure backend (`secure_app.py`):**
```python
# Strip HTML tags from input before processing
query = re.sub(r'<[^>]+>', '', query)
query = query[:100]  # Limit input length
```

**Why fix works:** Without `| safe`, Jinja2 converts `<script>` to `&lt;script&gt;` which browser displays as text, never executes.

---

### VULN-06 — CSRF Cross Site Request Forgery (OWASP A08)

**What:** Attacker's page silently sends request to change victim's password while they are logged in.

**Vulnerable Code:**
```python
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    # NO TOKEN CHECK — accepts any request from anywhere!
    if request.method == 'POST':
        new_password = request.form['new_password']
        cursor.execute("UPDATE users SET password=%s WHERE username=%s",
                       (new_password, session['user']))

    # ALSO ACCEPTS GET — trivially exploitable!
    elif request.args.get('new_password'):
        new_password = request.args.get('new_password')
        cursor.execute("UPDATE users SET password=%s ...", (new_password, ...))
```

**Secure Code:**
```python
# Generate unique token per session
session['csrf_token'] = secrets.token_hex(32)

# Validate token on every POST
token_form    = request.form.get('csrf_token', '')
token_session = session.get('csrf_token', '')
if not secrets.compare_digest(token_form, token_session):
    error = "CSRF Attack Detected! Invalid token."
    return ...

# Also: SameSite=Strict cookie prevents cross-site requests
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

---

### VULN-07 — Brute Force / Auth Failure (OWASP A07)

**What:** No limit on login attempts — attacker scripts thousands of password guesses.

**Vulnerable Code:**
```python
# Login just checks credentials with no attempt tracking
if user and user['password'] == password:
    session['user'] = user['username']
    return redirect('/')
else:
    error = "Invalid credentials"  # No counter, no lockout
```

**Secure Code:**
```python
# Track failed attempts in session
if 'failed_attempts' not in session:
    session['failed_attempts'] = 0

if session['failed_attempts'] >= 5:
    error = "Too many failed attempts. Try again later."
    logging.warning(f"Brute force detected for: {username}")
    return render_template('login.html', error=error)

# On success: reset counter
if user and bcrypt.checkpw(...):
    session['failed_attempts'] = 0
    ...
else:
    session['failed_attempts'] += 1
    remaining = 5 - session['failed_attempts']
    error = f"Invalid credentials. {remaining} attempts remaining."
```

---

### VULN-08 — Security Misconfiguration — Debug Mode (OWASP A05)

**What:** Debug mode ON exposes full stack traces, file paths, and DB queries to attackers.

**Vulnerable Code:**
```python
app.secret_key = "123456"  # Weak secret key
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_HTTPONLY'] = False

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Debug ON = full errors shown
```

**Secure Code:**
```python
app.secret_key = "a3f8#kL9!mZ2@qR7$nX4&wV6"  # Strong random key
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # True in production with HTTPS

if __name__ == '__main__':
    app.run(debug=False, port=5001)  # Debug OFF = generic errors only
```

---

### VULN-09 — Path Traversal (OWASP A01)

**What:** Attacker uses `../` in filename to read files outside the web folder.

**Vulnerable Code:**
```python
@app.route('/product-image')
def product_image():
    filename = request.args.get('file', '')
    # DANGEROUS: No path validation — reads any file!
    filepath = os.path.join('static', filename)
    with open(filepath, 'r') as f:
        content = f.read()
    return render_template('file_viewer.html', content=content)
```

**Secure Code:**
```python
@app.route('/product-image')
def product_image():
    filename = request.args.get('file', '')
    # CHECK 1: Block ../ sequences
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return "Access Denied! Path traversal detected."
    # CHECK 2: Only allow image extensions
    allowed = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(filename.endswith(ext) for ext in allowed):
        return "Access Denied! Only image files allowed."
    # CHECK 3: Verify final path is inside static/
    base_dir = os.path.abspath('static')
    filepath  = os.path.abspath(os.path.join(base_dir, filename))
    if not filepath.startswith(base_dir):
        return "Access Denied! Outside allowed directory."
```

---

### VULN-10 — Unrestricted File Upload (OWASP A04)

**What:** Upload page accepts any file type — attacker uploads malicious Python script and executes it.

**Vulnerable Code:**
```python
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file = request.files['file']
    # DANGEROUS: No type check, no size check, no filename sanitization!
    filepath = os.path.join('static/uploads', file.filename)
    file.save(filepath)
    # EXTREMELY DANGEROUS: Execute button runs uploaded code!
    exec(open(filepath).read(), {})
```

**Secure Code:**
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Check 1: Extension whitelist
if not allowed_file(file.filename):
    error = "File type not allowed!"

# Check 2: Sanitize filename
filename = secure_filename(file.filename)

# Check 3: File size limit
if size > MAX_FILE_SIZE:
    error = "File too large!"

# Check 4: Magic bytes — verify actual content
header = file.read(8)
is_image = header[:4] == b'\x89PNG' or header[:3] == b'\xff\xd8\xff' ...
if not is_image:
    error = "File content does not match type!"

# No execute route exists on secure site
```

---

## 7. Complete Attack Guide

### Attack 1 — SQL Injection

**Target:** `http://localhost:5000/login`

| Payload | Effect |
|---|---|
| `admin'#` | Login as admin without password |
| `admin' --` | Same (MySQL comment) |
| `' OR '1'='1` | Login as first user in DB |
| `john'#` | Login as john without password |
| `' OR 1=1 LIMIT 1 --` | Login as first user |

**Steps:**
1. Go to `http://localhost:5000/login`
2. Enter payload in Username field
3. Enter anything in Password field
4. Click Sign In → logged in without valid credentials!

**Expected on secure:** "Invalid credentials" — blocked ✅

---

### Attack 2 — XSS

**Target:** `http://localhost:5000/search`

| Payload | Effect |
|---|---|
| `<script>alert('XSS!')</script>` | Alert popup |
| `<script>alert(document.cookie)</script>` | Shows session cookie |
| `<img src=x onerror=alert('XSS')>` | Image error XSS |
| `<script>document.body.style.background='red'</script>` | Page defacement |
| `<h1 style="color:red;position:fixed;top:0;width:100%;background:black;z-index:9999">HACKED</h1>` | Visual defacement |
| `<script>window.location='http://evil.com'</script>` | Redirect to attacker site |

**Steps:**
1. Go to `http://localhost:5000/search`
2. Paste payload into search box
3. Click Search → payload executes!

**Via URL:**
```
http://localhost:5000/search?q=<script>alert('XSS')</script>
```

**Expected on secure:** Shows as plain text — no execution ✅

---

### Attack 3 — Broken Access Control

**Target:** `http://localhost:5000/admin`

**Steps:**
1. Logout: `http://localhost:5000/logout`
2. Visit directly: `http://localhost:5000/admin`
3. Full admin panel opens — shows all users + passwords!

**As normal user:**
1. Login as john: john / john123
2. Visit: `http://localhost:5000/admin`
3. Still opens — no role check!

**Expected on secure:** Redirects to login or shows 403 ✅

---

### Attack 4 — IDOR

**Target:** `http://localhost:5000/profile/<id>`

| URL | Effect |
|---|---|
| `/profile/1` | Admin's profile + password |
| `/profile/2` | John's profile + password |
| `/profile/3` | User's profile + password |
| `/profile/4` | Sahoo's profile + password |

**Steps:**
1. Login as john
2. Visit `http://localhost:5000/profile/1`
3. Sees admin's password in plain text!

**Expected on secure:** 403 Access Denied ✅

---

### Attack 5 — CSRF

**Setup:**
```bash
python -m http.server 9999
```

**Steps:**
1. Login as admin: `http://localhost:5000/login` → admin / admin123
2. Open new tab: `http://localhost:9999/csrf_attack.html`
3. Click "Claim My Prize!"
4. Logout
5. Try admin123 → FAILS (password changed to HACKED99)
6. Try HACKED99 → WORKS!

**Direct GET attack (easier to demo):**
```
http://localhost:5000/change-password?new_password=HACKED99
```
Visit this while logged in → password changed instantly!

**Expected on secure:**
```
http://localhost:5001/change-password?new_password=HACKED99
```
Shows "Invalid request! GET method not allowed." ✅

**Reset after demo:**
```sql
USE smartnest;
SET SQL_SAFE_UPDATES = 0;
UPDATE users SET password='admin123' WHERE username='admin';
SET SQL_SAFE_UPDATES = 1;
```

---

### Attack 6 — Brute Force

**Target:** `http://localhost:5000/login`

**Steps:**
1. Enter wrong password 6+ times
2. No lockout, no warning, no counter
3. Attacker scripts 1000 guesses per minute

**Expected on secure:**
- After 5 attempts: "Too many failed attempts. Try again later."
- Account locked ✅

---

### Attack 7 — Plain Text Passwords

**In MySQL Workbench:**
```sql
SELECT username, password FROM smartnest.users;
-- Shows: admin | admin123 | admin
```

**In browser (while logged in as any user):**
```
http://localhost:5000/profile/1
-- Shows password field in plain text!
http://localhost:5000/admin
-- Shows all passwords in table!
```

**Expected on secure:**
```sql
SELECT username, password FROM smartnest_secure.users;
-- Shows: admin | $2b$12$FRpGCk... (hash — useless to attacker)
```

---

### Attack 8 — Path Traversal

**Target:** `http://localhost:5000/product-image`

| Payload | Effect |
|---|---|
| `?file=../app.py` | Read entire source code + DB password |
| `?file=../../hash_passwords.py` | Read password utility script |
| `?file=../../secure_site/secure_app.py` | Read secure site's code |
| `?file=../../../Windows/System32/drivers/etc/hosts` | Read Windows system file |
| `?file=../../../../Users/sahoo/Desktop/passwords.txt` | Read desktop files |

**Steps:**
1. Visit: `http://localhost:5000/product-image?file=../app.py`
2. Full source code with DB password shown! 😱

**Expected on secure:**
```
http://localhost:5001/product-image?file=../secure_app.py
```
Shows "Access Denied! Path traversal detected." ✅

---

### Attack 9 — File Upload

**Target:** `http://localhost:5000/upload`

**Create malicious.py on Desktop:**
```python
import os, platform
output = f"OS: {platform.system()} | User: {os.getlogin()} | Dir: {os.getcwd()} | Files: {os.listdir('.')}"
```

**Steps:**
1. Visit: `http://localhost:5000/upload`
2. Upload `malicious.py`
3. Click "Execute" button
4. Server OS, username, file listing displayed! 😱

**Expected on secure:**
- Upload `malicious.py` → "File type not allowed!" ✅
- Upload real jpg renamed to `.py` → Magic byte check fails! ✅

---

### Attack 10 — Security Misconfiguration (Debug Mode)

**Target:** Vulnerable site with any error

**Trigger error (while logged in):**
```
http://localhost:5000/profile/99999
```

**Expected:**
- Vulnerable: Full Werkzeug debug page with stack trace, file paths, code lines
- Secure: Generic "403 Access Denied" page — no info leaked ✅

---

## 8. Security Fixes Summary

| OWASP | Vulnerability | Fix Applied |
|---|---|---|
| A01 | Broken Access Control | Session + role checks on every protected route |
| A01 | IDOR | Ownership validation before data access |
| A01 | Path Traversal | Path validation + directory boundary check |
| A02 | Plain Text Passwords | bcrypt hashing with salt |
| A03 | SQL Injection | Parameterized queries throughout |
| A03 | XSS | Jinja2 auto-escaping + input sanitization |
| A04 | File Upload | Extension whitelist + magic byte check + size limit |
| A05 | Debug Mode | debug=False + generic error pages |
| A07 | Brute Force | 5 attempt limit with session counter |
| A08 | CSRF | Token generation + SameSite=Strict cookie |
| A09 | No Logging | Full audit log in security.log |

---

## 9. Testing Checklist

### Vulnerable Site (`http://localhost:5000`)

- [ ] Homepage loads with products
- [ ] Login works: admin / admin123
- [ ] SQL injection: `admin'#` → logs in
- [ ] XSS: `<script>alert(1)</script>` in search → popup
- [ ] Admin panel opens without login: `/admin`
- [ ] IDOR: `/profile/1` as john → sees admin's password
- [ ] CSRF: visit `/change-password?new_password=HACKED99` → works
- [ ] Brute force: 10 wrong attempts → no lockout
- [ ] Path traversal: `?file=../app.py` → shows source code
- [ ] File upload: upload `.py` file → succeeds
- [ ] Debug mode: trigger error → full trace shown

### Secure Site (`http://localhost:5001`)

- [ ] Homepage loads
- [ ] Login works: admin / admin123
- [ ] SQL injection: `admin'#` → "Invalid credentials"
- [ ] XSS: script tag → shows as plain text
- [ ] Admin panel: `/admin` without login → redirects
- [ ] IDOR: `/profile/1` as john → 403
- [ ] CSRF: GET attack → "Invalid request!"
- [ ] Brute force: 5 attempts → "Too many failed attempts"
- [ ] Path traversal: `?file=../secure_app.py` → "Access Denied"
- [ ] File upload: `.py` file → "File type not allowed"
- [ ] Debug mode: trigger error → generic 403 page

---

## 10. Troubleshooting

### Error: `mysql.connector.errors.InterfaceError: 2003`
**Cause:** MySQL server not running
**Fix:** Start MySQL via services or `net start MySQL80`

### Error: `ValueError: Invalid salt`
**Cause:** Plain text password in DB but bcrypt.checkpw used
**Fix:** Run hash_passwords.py or manually update passwords

### Error: `decimal.Decimal` multiplication error
**Cause:** MySQL returns DECIMAL type
**Fix:** Use `product.price|float` in Jinja2 template

### Error: `TemplateNotFound`
**Cause:** HTML file missing or wrong folder
**Fix:** Check file is in `templates/` folder

### Error: Port already in use
**Cause:** Previous Flask instance still running
**Fix:**
```bash
netstat -ano | findstr :5000
taskkill /PID <NUMBER> /F
```

### Site runs but URL not shown in terminal
**Cause:** Normal Flask behavior with some configurations
**Fix:** Always visit `http://localhost:5000` or `http://localhost:5001` manually

### CSRF attack not working
**Cause:** Session expired or SameSite cookie blocking
**Fix:** Must be logged in BEFORE opening attack page. Use GET method attack for reliable demo.

---

## Login Credentials Quick Reference

### Vulnerable Site (`smartnest` DB)

| Username | Password | Role |
|---|---|---|
| admin | admin123 | admin |
| john | john123 | user |
| user | user123 | user |
| sahoo | sahoo123 | user |

### Secure Site (`smartnest_secure` DB)

| Username | Password | Role |
|---|---|---|
| admin | admin123 | admin |
| john | john123 | user |
| user | user123 | user |
| sahoo | sahoo123 | user |

---

## Important Notes

1. **Educational Purpose Only** — This project is for learning cybersecurity. Never deploy the vulnerable site on a public server.
2. **Local Only** — Keep both sites on localhost only.
3. **Reset After Demo** — Always reset passwords after CSRF demo.
4. **Port 9999** — Must run `python -m http.server 9999` for CSRF demo.
5. **security.log** — Auto-created in `secure_site/` folder — shows all attack attempts.

---

*CyberNest — OWASP Top 10 Demo Project*
*Built with Flask + MySQL + Bootstrap*
*For Educational Purposes Only*
