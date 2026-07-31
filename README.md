# 🍔 AmiGrab - Campus Canteen Delivery System

## Version 2.0 (Enhanced)

A modern, full-stack campus canteen delivery application built with **Flask**, featuring role-based authentication, real-time order tracking, and a beautiful responsive UI.

---

## ✨ Key Features

### 🎓 **For Students**
- Order food from multiple campus canteens
- Real-time order status tracking
- Dine-in and delivery options
- Digital wallet for quick payments
- Order ratings and reviews
- Order history

### 🚗 **For Delivery Partners**
- Available orders dashboard
- Real-time delivery tracking
- Earnings management
- Performance metrics
- Bonus and rewards

### 👨‍💼 **For Canteen Staff**
- Kitchen dashboard with incoming orders
- Order status management
- Real-time notifications
- Daily sales report

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- SQLite (included with Python)

### Installation

1. **Clone or Download the Project**
```bash
cd AmiGrab
```

2. **Create Virtual Environment** (Optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` File**
```bash
# Copy the example below and create a .env file in the project root
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///canteen.db
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-app-password
RAZORPAY_KEY_ID=rzp_test_key
RAZORPAY_KEY_SECRET=secret
SESSION_COOKIE_SECURE=False
LOG_LEVEL=INFO
```

5. **Initialize Database**
```bash
python app_new.py
# This will create the database and seed sample data
```

6. **Run the Application**
```bash
python app_new.py
# Visit http://localhost:5000
```

---

## 📋 Default Test Accounts

### Student Account
- **Email:** student@s.amity.edu
- **Password:** password123
- **Access:** Student Portal

### Faculty Account
- **Email:** faculty@amity.edu
- **Password:** password123
- **Access:** Student Portal (can order)

### Delivery Partner Account
- **Email:** delivery@gmail.com
- **Password:** password123
- **Access:** Delivery Dashboard

---

## 🎨 UI Design Highlights

### Color Schemes
- **Student Pages:** Purple/Blue Gradient (#667eea → #764ba2)
- **Delivery Pages:** Orange/Yellow Gradient (#FF6B35 → #F7931E)
- **Verification:** Purple with animated transitions

### Responsive Design
- ✅ Mobile (375px) - Optimized
- ✅ Tablet (768px) - Fully responsive
- ✅ Desktop (1024px+) - Enhanced experience

### Modern Components
- Glassmorphic cards
- Smooth animations
- Tab-based navigation
- Gradient buttons with hover effects
- Real-time form validation

---

## 🔐 Security Features

### Authentication
- ✅ Email OTP verification
- ✅ Password hashing (Werkzeug)
- ✅ Secure session management
- ✅ HttpOnly cookies

### Role-Based Access Control
- ✅ Students can ONLY login as Student
- ✅ Delivery Partners can ONLY login as Delivery
- ✅ Strict role validation on every request
- ✅ Unauthorized access prevention

### Data Protection
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ XSS protection (Jinja2 auto-escape)
- ✅ CSRF protection ready
- ✅ Environment variable secrets

### Gmail Requirement
- ✅ Delivery partners must use @gmail.com
- ✅ Client-side validation
- ✅ Server-side regex validation
- ✅ Clear error messages

---

## 📁 Project Structure

```
AmiGrab/
├── app_new.py                 # Main application factory
├── config.py                  # Configuration management
├── models.py                  # Database models
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (create this)
│
├── utils/
│   ├── helpers.py            # Validation & decorators
│   └── email_utils.py        # Email sending
│
├── routes/
│   ├── auth.py               # Authentication routes
│   ├── main.py               # Main application routes
│   └── delivery.py           # Delivery partner routes
│
├── templates/
│   ├── layout.html           # Base template
│   ├── login.html            # Login page (ENHANCED)
│   ├── register.html         # Student registration (ENHANCED)
│   ├── register_rider.html   # Delivery registration (ENHANCED)
│   ├── verify_otp.html       # OTP verification (ENHANCED)
│   ├── index.html            # Home page
│   ├── menu.html             # Canteen menu
│   └── ... (other pages)
│
└── static/
    ├── profile_pics/         # User profile pictures
    ├── manifest.json         # PWA manifest
    └── sw.js                 # Service worker
```

---

## 🔑 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Development or production | development |
| `SECRET_KEY` | Application secret key | random-32-char-string |
| `DATABASE_URL` | Database connection URI | sqlite:///canteen.db |
| `SENDER_EMAIL` | Gmail address for emails | your-email@gmail.com |
| `SENDER_PASSWORD` | Gmail app password | xxxx xxxx xxxx xxxx |
| `RAZORPAY_KEY_ID` | Payment gateway key | rzp_test_xxxxx |
| `RAZORPAY_KEY_SECRET` | Payment gateway secret | xxxxx |
| `LOG_LEVEL` | Logging level | INFO |

### Gmail App Password Setup

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password
4. Paste in `.env` as `SENDER_PASSWORD`

---

## 📊 Database Schema

### Key Tables

**users**
- ID, Name, Email (unique), Phone, Password Hash, Role, Wallet Balance, etc.

**canteens**
- ID, Name, Location, UPI ID, Rating, Image, etc.

**menu_items**
- ID, Canteen ID, Name, Price, Category, Is Veg, Availability, etc.

**orders**
- ID, User ID, Canteen ID, Items, Status, Total Price, OTP, Delivery Address, etc.

**wallet_transactions**
- ID, User ID, Amount, Type (credit/debit), Transaction ID, etc.

---

## 🧪 Testing

### Test Login Flows

#### Student Login (Correct)
1. Go to http://localhost:5000/login
2. Click "Student" tab
3. Email: `student@s.amity.edu`
4. Password: `password123`
5. ✅ Success → Dashboard

#### Delivery Login (Correct)
1. Go to http://localhost:5000/login
2. Click "Rider" tab
3. Email: `delivery@gmail.com`
4. Password: `password123`
5. ✅ Success → Delivery Dashboard

#### Access Denial (Wrong Role)
1. Go to http://localhost:5000/login
2. Click "Student" tab
3. Email: `delivery@gmail.com` (delivery email)
4. Password: `password123`
5. ❌ Error: "Access Denied: You are not registered as a Delivery Partner"

#### Gmail Requirement
1. Go to http://localhost:5000/register_rider
2. Try: `rider@yahoo.com`
3. ❌ Client-side blocks (shows validation error)
4. Try: `rider@gmail.com`
5. ✅ Accepted

---

## 📈 Performance Optimizations

- ✅ Database indexes on frequently queried columns
- ✅ Lazy loading for database relationships
- ✅ Image optimization (user profile pictures)
- ✅ Caching for canteen menus
- ✅ Efficient ORM queries
- ✅ Responsive images

---

## 🚀 Deployment Guide

### Development to Production

1. **Security Updates:**
   - Change `SECRET_KEY` to a random 32-character string
   - Update database to PostgreSQL for production
   - Enable HTTPS (set `SESSION_COOKIE_SECURE=True`)
   - Update email credentials

2. **Database:**
   ```bash
   # Run migrations to production database
   flask db upgrade
   ```

3. **Environment:**
   ```bash
   FLASK_ENV=production
   DEBUG=False
   ```

4. **Server:**
   - Use Gunicorn or uWSGI
   - Set up Nginx reverse proxy
   - Enable SSL/TLS certificate

---

## 🐛 Troubleshooting

### Problem: "No module named 'config'"
**Solution:** Ensure `config.py` is in the project root directory

### Problem: Email not sending
**Solution:** 
- Verify Gmail app password (not regular password)
- Check firewall/antivirus blocking SMTP
- Enable "Less Secure App Access"

### Problem: Database locked
**Solution:** 
- Delete `*.db-wal` and `*.db-shm` files
- Restart the application

### Problem: Port already in use
**Solution:**
```bash
# Change port in .env or run with different port
python app_new.py --port 5001
```

---

## 📚 Additional Documentation

- **ENHANCEMENTS.md** - Complete list of enhancements
- **IMPLEMENTATION_GUIDE.md** - Step-by-step integration guide
- **config.py** - Configuration options
- **models.py** - Database schema documentation

---

## 🤝 Contributing

To contribute improvements:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## 📞 Support

### Getting Help

- Check IMPLEMENTATION_GUIDE.md for setup issues
- Review ENHANCEMENTS.md for feature documentation
- Check error logs in `app.log`

### Reporting Issues

Include:
- Error message
- Steps to reproduce
- Python version
- Operating system

---

## 📜 License

This project is provided as-is for educational purposes.

---

## 🎯 Version History

### v2.0 (Current)
- ✨ Enhanced UI with gradients and animations
- 🔒 Strict role-based access control
- 📧 Gmail requirement for delivery partners
- 🏗️ Modular blueprint architecture
- ⚙️ Configuration management system
- 📝 Comprehensive logging
- 🗄️ Database optimizations
- 🎨 Beautiful, responsive design

### v1.0
- Basic functionality
- User authentication
- Order management
- Delivery tracking

---

## 🙏 Acknowledgments

Built with:
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Jinja2** - Templating
- **Boxicons** - Icons
- **Poppins Font** - Typography

---

## 📅 Last Updated
March 29, 2026

## ✅ Status
🟢 **Production Ready** (with HTTPS in production)

---

**Made with ❤️ for Amity University Students**

