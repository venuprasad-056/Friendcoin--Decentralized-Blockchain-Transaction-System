from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3, hashlib, time
from blockchain import Blockchain

app = Flask(__name__)
app.secret_key = "friendcoin_demo_secret_change_this"

DB = "users.db"
blockchain = Blockchain()

# ---------- DB setup ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    wallet TEXT UNIQUE,
                    balance REAL DEFAULT 0.0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT,
                    receiver TEXT,
                    amount REAL,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------- helpers ----------
def get_user_by_username(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, password, wallet, balance FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_by_wallet(wallet):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, password, wallet, balance FROM users WHERE wallet=?", (wallet,))
    row = c.fetchone()
    conn.close()
    return row

def save_transaction(sender, receiver, amount):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (sender, receiver, amount, timestamp) VALUES (?, ?, ?, ?)",
              (sender, receiver, amount, ts))
    conn.commit()
    conn.close()

def get_transactions_for_wallet(wallet):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT sender, receiver, amount, timestamp FROM transactions WHERE sender=? OR receiver=? ORDER BY id DESC",
              (wallet, wallet))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- routes ----------
@app.route("/")
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        if not username or not password:
            return render_template("register.html", error="Please enter username and password.")
        if get_user_by_username(username):
            return render_template("register.html", error="Username already exists.")
        
        wallet = hashlib.blake2b((username + str(time.time())).encode(), digest_size=8).hexdigest()
        private_key = hashlib.blake2b((wallet + str(time.time())).encode(), digest_size=16).hexdigest()
        starting_balance = 100.0
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, wallet, balance) VALUES (?, ?, ?, ?)",
                  (username, password, wallet, starting_balance))
        conn.commit()
        conn.close()
        
        return render_template("register_success.html", username=username, wallet=wallet, private_key=private_key)
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = get_user_by_username(username)
        if user and user[2] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = get_user_by_username(session['username'])
    print("DEBUG: session username =", session.get('username'))
    print("DEBUG: user =", user)

    if not user:
        # User not found — clear session and force re-login
        session.pop('username', None)
        return redirect(url_for('login'))

    wallet = user[3]
    balance = user[4] if user[4] is not None else 0.0
    txs = get_transactions_for_wallet(wallet)
    return render_template("dashboard.html", username=user[1], wallet=wallet, balance=balance, tx_history=txs)

@app.route("/profile")
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = get_user_by_username(session['username'])
    if not user:
        session.pop('username', None)
        return redirect(url_for('login'))
    return render_template("profile.html", username=user[1], wallet=user[3], balance=user[4])

@app.route("/send", methods=["POST"])
def send():
    if 'username' not in session:
        return redirect(url_for('login'))
    sender_user = get_user_by_username(session['username'])
    if not sender_user:
        session.pop('username', None)
        return redirect(url_for('login'))

    sender_wallet = sender_user[3]
    try:
        amount = float(request.form.get("amount"))
    except:
        return render_template("dashboard.html", username=sender_user[1], wallet=sender_wallet,
                               balance=sender_user[4], tx_history=get_transactions_for_wallet(sender_wallet),
                               error="Invalid amount.")
    receiver_wallet = request.form.get("receiver_wallet").strip()
    receiver = get_user_by_wallet(receiver_wallet)
    if not receiver:
        return render_template("dashboard.html", username=sender_user[1], wallet=sender_wallet,
                               balance=sender_user[4], tx_history=get_transactions_for_wallet(sender_wallet),
                               error="Receiver not found.")
    sender_balance = sender_user[4] if sender_user[4] is not None else 0.0
    if sender_balance < amount:
        return render_template("dashboard.html", username=sender_user[1], wallet=sender_wallet,
                               balance=sender_balance, tx_history=get_transactions_for_wallet(sender_wallet),
                               error="Insufficient balance.")
    
    # Update balances
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET balance=? WHERE wallet=?", (sender_balance - amount, sender_wallet))
    recv_balance = receiver[4] if receiver[4] is not None else 0.0
    c.execute("UPDATE users SET balance=? WHERE wallet=?", (recv_balance + amount, receiver_wallet))
    conn.commit()
    conn.close()
    
    # Save transaction
    save_transaction(sender_wallet, receiver_wallet, amount)
    blockchain.add_transaction(sender_wallet, receiver_wallet, amount)
    last_hash = blockchain.last_block["hash"]
    blockchain.create_block(previous_hash=last_hash)
    
    return redirect(url_for('dashboard'))

@app.route("/explorer")
def explorer():
    chain = blockchain.chain
    return render_template("explorer.html", chain=chain)

@app.route("/get_private_key", methods=["POST"])
def get_private_key():
    if 'username' not in session:
        return jsonify(success=False)
    user = get_user_by_username(session['username'])
    data = request.get_json()
    if user and data.get("password") == user[2]:
        private_key = hashlib.blake2b((user[3] + str(time.time())).encode(), digest_size=32).hexdigest()
        return jsonify(success=True, private_key=private_key)
    return jsonify(success=False)

if __name__ == "__main__":
    app.run(debug=True)
