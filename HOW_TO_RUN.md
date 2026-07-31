# 🚀 How to Open & Run AmiGrab v2.0

## Step-by-Step Instructions

### STEP 1: Open Command Prompt / Terminal

**On Windows:**
1. Press `Win + R` on your keyboard
2. Type `cmd` and press Enter
3. A black terminal window will open

**Alternative (File Explorer Method):**
1. Open File Explorer
2. Navigate to: `C:\Users\Jahaa\OneDrive\Desktop\AmiGrab`
3. Right-click in empty space
4. Select "Open in Terminal" or "Open Command Prompt here"

---

### STEP 2: Navigate to Project Folder

```bash
cd C:\Users\Jahaa\OneDrive\Desktop\AmiGrab
```

**Your terminal should show:**
```
C:\Users\Jahaa\OneDrive\Desktop\AmiGrab>
```

---

### STEP 3: Create Virtual Environment (Recommended)

This creates an isolated Python environment:

```bash
python -m venv venv
```

**Then activate it:**

```bash
venv\Scripts\activate
```

**Your terminal should now show:**
```
(venv) C:\Users\Jahaa\OneDrive\Desktop\AmiGrab>
```

---

### STEP 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-SQLAlchemy (database)
- Flask-Migrate (migrations)
- python-dotenv (environment variables)
- Werkzeug (utilities)

**Wait for it to complete. You'll see:**
```
Successfully installed Flask-2.3.2 Flask-SQLAlchemy-3.0.5 ...
```

---

### STEP 5: Create .env Configuration File

**Option A: Using Command Line**

```bash
# Create .env file
echo FLASK_ENV=development > .env
echo SECRET_KEY=amigrab-secret-key-2024 >> .env
echo DATABASE_URL=sqlite:///canteen.db >> .env
echo SENDER_EMAIL=your-gmail@gmail.com >> .env
echo SENDER_PASSWORD=your-app-password >> .env
echo LOG_LEVEL=INFO >> .env
```

**Option B: Using Notepad (Easier)**

1. Open Notepad
2. Copy and paste this:
```
FLASK_ENV=development
SECRET_KEY=amigrab-secret-key-2024
DATABASE_URL=sqlite:///canteen.db
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-app-password
LOG_LEVEL=INFO
```

3. Save as `.env` in `C:\Users\Jahaa\OneDrive\Desktop\AmiGrab\`
   - File name: `.env`
   - Save as type: `All Files (*.*)`

---

### STEP 6: Run the Application

```bash
python app_new.py
```

**You should see:**
```
╔══════════════════════════════════════════╗
║    🍔 AmiGrab - Campus Canteen App      ║
║           Enhanced Version 2.0          ║
╚══════════════════════════════════════════╝

Environment: DEVELOPMENT
Debug Mode: True
Server: http://0.0.0.0:5000

✓ Authentication with role-based access
✓ Gmail required for delivery partners
✓ Modern responsive UI
✓ Modular architecture
✓ Database optimization

Press CTRL+C to stop the server.
```

---

### STEP 7: Open in Browser

**Click this link or copy-paste in your browser:**

```
http://localhost:5000
```

**Or use these addresses:**
- `http://127.0.0.1:5000`
- `http://0.0.0.0:5000`

---

## 🧪 Test Accounts

Once the app opens, use these to login:

### Student Account
- **Email:** `student@s.amity.edu`
- **Password:** `password123`
- Click the **"Student"** tab on login page

### Delivery Partner Account
- **Email:** `delivery@gmail.com`
- **Password:** `password123`
- Click the **"Rider"** tab on login page

---

## 📱 What You'll See

### Login Page
```
┌─────────────────────────────┐
│  🍔 AmiGrab                 │
│  Fast & Fresh Food Delivery │
│                             │
│  ┌─ Student ── Rider ─┐    │
│  │                    │    │
│  │ Email: @amity.edu  │    │
│  │ Password: ••••••   │    │
│  │ [Login →]          │    │
│  └────────────────────┘    │
└─────────────────────────────┘
```

### Two Tabs:
1. **Student Tab** - Purple gradient, college email required
2. **Rider Tab** - Orange gradient, Gmail required

---

## ❌ If You Get Errors

### Error: "No module named config"
**Solution:** Make sure all files are in `C:\Users\Jahaa\OneDrive\Desktop\AmiGrab\`

### Error: "Port 5000 already in use"
**Solution:** Use a different port:
```bash
python app_new.py --port 5001
```
Then visit: `http://localhost:5001`

### Error: "ModuleNotFoundError: No module named 'flask'"
**Solution:** Make sure to install dependencies:
```bash
pip install -r requirements.txt
```

### Error: ".env file not found"
**Solution:** Create `.env` file with the content from Step 5

### Emails not sending
**Solution:** Update `.env` with real Gmail credentials:
```
SENDER_EMAIL=your-actual-email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
```

---

## 🛑 Stop the Application

**Press in the terminal:**
```
CTRL + C
```

You'll see:
```
Keyboard interrupt received, shutting down.
```

---

## 📂 File Structure You Should See

```
AmiGrab/
├── app_new.py                 ✓ Main app
├── config.py                  ✓ Configuration
├── models.py                  ✓ Database
├── requirements.txt           ✓ Dependencies
├── .env                       ✓ Create this
├── venv/                      ✓ Virtual environment (created)
├── utils/
│   ├── helpers.py
│   └── email_utils.py
├── routes/
│   ├── auth.py
│   ├── main.py
│   └── delivery.py
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── register_rider.html
│   └── verify_otp.html
└── README.md                  ✓ Documentation
```

---

## 🎯 Quick Summary

| Step | Command | What It Does |
|------|---------|-------------|
| 1 | `cd C:\Users\Jahaa\OneDrive\Desktop\AmiGrab` | Go to folder |
| 2 | `python -m venv venv` | Create virtual environment |
| 3 | `venv\Scripts\activate` | Activate environment |
| 4 | `pip install -r requirements.txt` | Install dependencies |
| 5 | Create `.env` file | Setup configuration |
| 6 | `python app_new.py` | **START THE APP** |
| 7 | Open `http://localhost:5000` | **VIEW IN BROWSER** |

---

## 🎉 Once Running

You can:
✅ Login as Student or Delivery Partner
✅ See dual login tabs
✅ Test role-based access
✅ Try wrong email combos (will be blocked)
✅ View modern UI with gradients
✅ Test on mobile too!

---

## 💡 Tips

- **Keep terminal open** while using the app
- **Use Ctrl+C** in terminal to stop the app
- **Refresh browser** (F5) if something looks wrong
- **Check terminal** for error messages
- **Mobile view:** Press F12 in browser, then mobile icon

---

## 📞 Need Help?

If something doesn't work:
1. Check terminal for error messages
2. Make sure `.env` file exists
3. Make sure all files are in the right folder
4. Try stopping (Ctrl+C) and restarting
5. Check `app.log` file for detailed errors

---

**You're all set! Follow the steps above and your AmiGrab app will be running in seconds!** 🚀

