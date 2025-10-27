# FriendCoin Wallet – A Decentralized Blockchain-based Transaction System

Lightweight Flask app that simulates a decentralized transaction system using a simple in-memory blockchain and user wallets. Suitable for demos and learning purposes.

## Preview
Add a screenshot named `dashboard_preview.png` in the repo root to show a preview image here.
![FriendCoin Dashboard Preview](dashboard_preview.png)

## Features
- User registration and login
- Wallet generation (BLAKE2b) and encrypted private key storage
- Send/receive FriendCoin between users
- In-memory blockchain explorer (blocks created per transaction)
- Private key protection: encrypted with user's password; reveal by password
- Ready for deployment to Render.com

## Tech Stack
- Python 3, Flask
- SQLite (ephemeral `/tmp/users.db` on Render free tier)
- BLAKE2b hashing, SHA256-based key derivation
- Tailwind CSS for UI (via CDN) + custom CSS

## Quick Local Setup
```bash
# 1. Unzip repo and enter folder
unzip friendcoin_wallet_github_ready.zip -d friendcoin
cd friendcoin

# 2. Create virtual env (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run locally
python app.py
# or using gunicorn (production-like)
gunicorn app:app --bind 0.0.0.0:5000

# 5. Open http://127.0.0.1:5000
```

## Deploy to Render (step-by-step)
1. Push this repo to GitHub (see below).  
2. Sign in to https://render.com and click **New** → **Web Service**.  
3. Connect your GitHub account and select this repository.  
4. Fill the service form:
   - **Name:** friendcoin-wallet (or any name)
   - **Branch:** main
   - **Environment:** Python 3
   - **Build command:** `pip install -r requirements.txt` (Render usually auto-detects)
   - **Start command:** `gunicorn app:app`
5. Create the service and wait for the build to finish. A public URL will be provided.
6. (Optional but recommended) In the Render service dashboard → **Environment** → **Environment Variables**, set:
   - `SECRET_KEY` to a secure random string (used by Flask session)
7. Test the site: register, login, send coins, and view the blockchain explorer.

**Notes:** On Render free tier the database file is stored at `/tmp/users.db` and is ephemeral — it will be reset on deploys/restarts. For persistence, attach a disk on Render or use a managed database like PostgreSQL.

## How to push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - FriendCoin Wallet"
git branch -M main
git remote add origin https://github.com/venuprasad-056/friendcoin-Decentralized-Blockchain-Transaction-System.git
git push -u origin main
```

## License
This project is released under the MIT License. See the `LICENSE` file.

---
**Developed by Venu Prasad**  
Department of Artificial Intelligence & Data Science, BGSCET
