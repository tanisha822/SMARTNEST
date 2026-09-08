import bcrypt
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="babamama",        # your MySQL password
    database="smartnest"
)

cursor = db.cursor(dictionary=True)
cursor.execute("SELECT id, username, password FROM users")
users = cursor.fetchall()


for user in users:
    pwd = user['password']

    # Only hash if it's NOT already a bcrypt hash
    if not pwd.startswith('$2b$'):
        print(f"Hashing password for: {user['username']}")
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

        update = db.cursor()
        update.execute(
            "UPDATE users SET password=%s WHERE id=%s",
            (hashed.decode('utf-8'), user['id'])
        )
        db.commit()
        print(f"  Done → {hashed.decode('utf-8')[:30]}...")
    else:
        print(f"Already hashed: {user['username']} — skipping")

print("\nAll done! All passwords are now bcrypt hashed.")