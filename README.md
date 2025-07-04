
# 🗳️ Ranked Choice Voting (RCV) Web App

A web-based voting platform built with **Flask** that supports **Ranked Choice Voting (RCV)**. Voters can rank candidates by preference. The app ensures secure, fair voting and automatically calculates the winner once the election ends.

---

## 🚀 Live Demo

🟢 **Live App**: [https://your-render-link.onrender.com](https://your-render-link.onrender.com)  
_(Replace with your actual deployed URL once deployed)_

---

## 🎯 Features

- 🔒 **User Authentication** (Register/Login/Logout)
- 🗳️ **Ranked Voting** (1st to 5th preference)
- 🕑 **Election Countdown Timer**
- 📄 **Vote Confirmation Page** (with ranking and timer)
- 🏆 **Results Page** using RCV elimination logic
- 🧹 **Automatic Ballot Reset** after election ends
- 🛠️ **In-memory user handling**, and persistent vote storage using **SQLite**

---

## 📸 Screenshots

### 🔐 Register Page
![Register Page](screenshots/Screenshot%202025-07-04%20111550.png)

### 🔑 Login Page
![Login Page](screenshots/Screenshot%202025-07-04%20111524.png)

### 🗳️ Vote Page (with timer)
![Vote Page](screenshots/Screenshot%202025-07-04%20111632.png)

### ✅ Confirmation Page (with ranking)
![Confirmation Page](screenshots/Screenshot%202025-07-04%20111649.png)

### 🏁 Results Page (after countdown ends)
![Results Page](screenshots/Screenshot%202025-07-04%20111713.png)


## 📋 How It Works

1. **Election Setup**: The election ends 2 days from the server start time (you can change this duration in `main.py` via `ELECTION_END`).

2. **User Registration**: Voters register with a username and password.

3. **Voting Process**:
   - Users must select at least their 1st preference.
   - Ranked preferences are stored securely in a SQLite database.
   - Confirmation page is shown with ranking and a live countdown.

4. **After Voting**:
   - Re-login shows the same confirmation page until the timer expires.

5. **After Countdown Ends**:
   - Election restarts automatically for new users.

---

## ⚙️ Installation & Local Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/rcv-voting-app.git
cd rcv-voting-app
```

### 2️⃣ Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Requirements
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the App
```bash
python main.py
```

- Visit `http://127.0.0.1:5000` in your browser.

---

## 🧪 Dependencies

- Python 3.7+
- Flask
- Werkzeug (for password hashing)
- SQLite (builtin)

---

## 🔧 Configuration

You can customize these in `main.py`:

```python
# ⏳ Election Duration (default: 2 days)
ELECTION_END = datetime.utcnow() + timedelta(days=2)

# 👥 Candidates List
CANDIDATES = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Miller", "Eve Davis"]
```

---

## 📈 Future Upgrades (Ideas)

- 📱 Add **mobile number** and **OTP-based verification** during registration.
- 📩 Send email confirmation to voters.
- 📊 Admin dashboard to monitor voting activity.
- 🧾 Export results as CSV.
- 💬 Voter comments/feedback section.

---

## 📦 Deployment (Render)

1. Push your code to GitHub.
2. Go to [https://render.com](https://render.com), create a new **Web Service**.
3. Connect your GitHub repo.
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. Make sure the following file is in your root directory:
   - `requirements.txt`
   - `main.py`
   - `templates/` folder with HTML files

> Note: SQLite DB (`ballots.db`) will persist between restarts unless manually deleted.

---

## 📄 License

MIT License

---

## 🙋‍♂️ Author

Made with ❤️ by Chaitu 
