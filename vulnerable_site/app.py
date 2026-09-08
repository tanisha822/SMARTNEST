from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os;

app = Flask(__name__)
app.secret_key = "123456"

# VULNERABILITY: Makes cookies vulnerable to CSRF
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="babamama",  # your MySQL password
        database="smartnest"
    )

# ---------- HOME ----------
@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('home.html', products=products)

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # VULNERABILITY 1: SQL Injection
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['user'] = user['username']
            session['role'] = user['role']
            return redirect('/')
        else:
            error = "Invalid credentials"
    return render_template('login.html', error=error)

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()

        # VULNERABILITY 2: Password stored as plain text
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')",
                       (username, email, password))
        db.commit()
        return redirect('/login')
    return render_template('register.html', error=error)

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



# VULNERABLE: No CSRF token check — accepts both GET and POST
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect('/login')

    message = None

    if request.method == 'POST':
        new_password = request.form['new_password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET password=%s WHERE username=%s",
                       (new_password, session['user']))
        db.commit()
        message = "Password changed successfully!"

    # VULNERABILITY: Accepts password change via GET request too!
    elif request.method == 'GET' and request.args.get('new_password'):
        new_password = request.args.get('new_password')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET password=%s WHERE username=%s",
                       (new_password, session['user']))
        db.commit()
        message = "Password changed!"

    return render_template('change_password.html', message=message)


# VULNERABLE: Path Traversal
@app.route('/product-image')
def product_image():
    filename = request.args.get('file', '')

    # VULNERABILITY: No path validation — user controls file path!
    filepath = os.path.join('static', filename)

    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return render_template('file_viewer.html',
                               filename=filename,
                               content=content)
    except FileNotFoundError:
        return render_template('file_viewer.html',
                               filename=filename,
                               content='File not found!')
    except Exception as e:
        return render_template('file_viewer.html',
                               filename=filename,
                               content=str(e))

# ---------- PROFILE (IDOR vulnerability) ----------
@app.route('/profile/<int:user_id>')
def profile(user_id):
    # VULNERABILITY 3: IDOR — no check if this is YOUR profile
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('profile.html', user=user)

# ---------- ADMIN PANEL ----------
@app.route('/admin')
def admin():
    # VULNERABILITY 4: Broken Access Control — no role check
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return render_template('admin.html', users=users)

# ---------- SEARCH (XSS vulnerability) ----------
@app.route('/search')
def search():
    query = request.args.get('q', '')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE name LIKE %s", ('%' + query + '%',))
    results = cursor.fetchall()
    # VULNERABILITY 5: XSS — query reflected without escaping
    return render_template('search.html', query=query, results=results)



# VULNERABLE: File Upload — no restriction on file type
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    message = None
    uploaded_file = None

    if request.method == 'POST':
        if 'file' not in request.files:
            message = "No file selected!"
        else:
            file = request.files['file']

            if file.filename == '':
                message = "No file selected!"
            else:
                # VULNERABILITY: No file type check — accepts ANY file!
                # VULNERABILITY: Uses original filename — path traversal possible!
                # VULNERABILITY: No file size limit!
                upload_folder = os.path.join('static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)

                filepath = os.path.join(upload_folder, file.filename)
                file.save(filepath)

                uploaded_file = file.filename
                message = f"File uploaded successfully: {file.filename}"

    # Show all uploaded files
    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    uploaded_files = os.listdir(upload_folder)

    return render_template('upload.html',
                           message=message,
                           uploaded_file=uploaded_file,
                           uploaded_files=uploaded_files)


# VULNERABILITY: Execute uploaded Python files!
@app.route('/execute/<filename>')
def execute_file(filename):
    if 'user' not in session:
        return redirect('/login')

    filepath = os.path.join('static', 'uploads', filename)
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        # EXTREME VULNERABILITY: Executes uploaded code on server!
        exec_globals = {}
        exec(code, exec_globals)
        output = exec_globals.get('output', 'Code executed! No output variable set.')
        return render_template('upload.html',
                               message=f"Executed {filename}",
                               exec_output=str(output),
                               uploaded_files=os.listdir('static/uploads'))
    except Exception as e:
        return render_template('upload.html',
                               message=f"Error: {str(e)}",
                               uploaded_files=os.listdir('static/uploads'))

if __name__ == '__main__':
    # VULNERABILITY 6: Debug mode ON
    app.run(debug=True, port=5000)