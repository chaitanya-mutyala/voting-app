import sqlite3, os
from copy import deepcopy
from functools import wraps
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

# ----- App setup -----
app = Flask(__name__)
app.secret_key = 'your_strong_secret_key_here_replace_me_with_a_real_one'

ELECTION_END = datetime.utcnow() + timedelta(days=2)
DB_FILE = "ballots.db"
DB_RESET_FLAG = False  # To prevent multiple resets on every request

USERS = {}
CANDIDATES = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Miller", "Eve Davis"]

# ----- DB Helpers -----
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ballots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ranking TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def reset_election():
    """Delete ballots if election ended."""
    global DB_RESET_FLAG
    if not DB_RESET_FLAG and os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        DB_RESET_FLAG = True
        for user in USERS.values():
            user['voted'] = False
        print("Election ended — ballots deleted.")

def add_ballot(ranking):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO ballots (ranking) VALUES (?)", (",".join(ranking),))
    conn.commit()
    conn.close()

def fetch_ballots():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ranking FROM ballots")
    rows = c.fetchall()
    conn.close()
    return [row[0].split(",") for row in rows]

# ----- RCV -----
def calculate_rcv_winner(ballots):
    n = len(ballots)
    while True:
        d = {}
        for ballot in ballots:
            if ballot:
                d[ballot[0]] = d.get(ballot[0], 0) + 1
        if not d:
            return None
        for candidate, cnt in d.items():
            if cnt * 2 > n:
                return candidate
        if len(d) == 1:
            return next(iter(d))
        if len(set(d.values())) == 1:
            return None
        min_votes = min(d.values())
        to_eliminate = [c for c, cnt in d.items() if cnt == min_votes]
        for ballot in ballots:
            ballot[:] = [name for name in ballot if name not in to_eliminate]

# ----- Auth Decorator -----
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = session.get('username')
        if not user or user not in USERS:
            session.pop('username', None)
            flash("Please log in to access that page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

# ----- Routes -----
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('vote'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('register.html')

        if username in USERS:
            flash("That username is already taken.", "error")
            return render_template('register.html')

        USERS[username] = {
            'password_hash': generate_password_hash(password),
            'voted': False
        }
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session and session['username'] not in USERS:
        session.pop('username')

    if datetime.utcnow() > ELECTION_END:
        
        return redirect(url_for('results'))

    if 'username' in session:
        user = session['username']
        if 'just_voted' in session:
            voted_data = session.pop('just_voted')
            return render_template('voted_confirmation.html', user_vote=voted_data, end_time=ELECTION_END.isoformat())
        if USERS[user]['voted']:
            flash("Welcome back!", "info")
            return render_template('voted_confirmation.html',
                           user_vote=[],  # <-- optionally fetch their actual vote
                           end_time=ELECTION_END.isoformat())
        return redirect(url_for('vote'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = USERS.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            if user['voted']:
                return render_template(
        'voted_confirmation.html',
        user_vote=[],  # Optional: replace with actual prefs if stored
        end_time=ELECTION_END.isoformat()
    )

            return redirect(url_for('vote'))
        flash("Invalid username or password.", "error")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    flash("You’ve been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if datetime.utcnow() > ELECTION_END:
        
        return redirect(url_for('results'))

    user = session['username']
    if USERS[user]['voted']:
        flash("Welcome back!", "info")
        return render_template('voted_confirmation.html',
                           user_vote=[],  # <-- optionally fetch their actual vote
                           end_time=ELECTION_END.isoformat())

    error = None
    if request.method == 'POST':
        prefs = []
        seen = set()
        for i in range(1, len(CANDIDATES) + 1):
            choice = request.form.get(f"pref{i}")
            if i == 1 and not choice:
                error = "First preference is required."
                break
            if choice:
                if choice not in CANDIDATES:
                    error = f"Invalid candidate: {choice}"
                    break
                if choice in seen:
                    error = f"Duplicate selection: {choice}"
                    break
                seen.add(choice)
                prefs.append(choice)

        if error:
            flash(error, "error")
            return render_template('vote.html', candidates=CANDIDATES, error=error, end_time=ELECTION_END.isoformat())

        add_ballot(prefs)
        USERS[user]['voted'] = True
        session['just_voted'] = prefs
        return render_template('voted_confirmation.html', user_vote=prefs, end_time=ELECTION_END.isoformat())

    return render_template('vote.html', candidates=CANDIDATES, error=None, end_time=ELECTION_END.isoformat())

@app.route('/results')
@login_required
def results():
    ballots = fetch_ballots()
    winner = calculate_rcv_winner(deepcopy(ballots))
    return render_template('results.html', winner=winner, ballots=ballots)

# ----- Entrypoint -----
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
