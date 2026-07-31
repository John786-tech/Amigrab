import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename 
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask import send_from_directory

# --- NEW: IMPORT RAZORPAY ---
# Run: pip install razorpay
import razorpay 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = 'super_secret_key'

# --- CONFIG ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'canteen_new.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static/profile_pics')

# --- RAZORPAY CONFIGURATION (NEW) ---
# Replace these with your actual keys from https://dashboard.razorpay.com/
RAZORPAY_KEY_ID = "rzp_test_YOUR_KEY_HERE" 
RAZORPAY_KEY_SECRET = "YOUR_SECRET_HERE"

# Initialize Client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- UPDATED: AMITY DOMAINS ---
STUDENT_DOMAIN = "@s.amity.edu"
FACULTY_DOMAIN = "@amity.edu"

SENDER_EMAIL = "jahaangauri786@gmail.com" 
SENDER_PASSWORD = "ndua syjx fddp idvv" 

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Student") 
    wallet_balance = db.Column(db.Float, default=500.0)
    profile_pic = db.Column(db.String(150), default='default.png')

class Canteen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    upi_id = db.Column(db.String(100), nullable=False, default="admin@okaxis") 

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteen.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_veg = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteen.id'), nullable=False)
    
    # Relationships
    canteen = db.relationship('Canteen', backref='orders')
    user = db.relationship('User', backref='orders') 
    
    delivery_rider_id = db.Column(db.Integer, nullable=True) 
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending") 
    order_type = db.Column(db.String(20), default="Dine-in")
    customer_name = db.Column(db.String(100))
    delivery_location = db.Column(db.String(200))
    customer_phone = db.Column(db.String(20))
    pickup_time = db.Column(db.String(20))
    items_summary = db.Column(db.String(500))
    otp = db.Column(db.String(6))
    transaction_id = db.Column(db.String(50))
    rating = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20))      
    provider = db.Column(db.String(50))  
    details = db.Column(db.String(100))  
    expiry = db.Column(db.String(10))    
    color = db.Column(db.String(100))    

# --- HELPER FUNCTIONS ---
def get_user_or_logout():
    if 'user_id' not in session: return None
    user = User.query.get(session['user_id'])
    if not user: session.clear(); return None
    return user

def send_email_otp(to_email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "Campus Canteen Verification Code"
        body = f"Hello,\n\nYour OTP is: {otp}\n\nDo not share this with anyone."
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

def attach_item_ratings(items):
    for item in items:
        relevant_orders = Order.query.filter(Order.items_summary.contains(item.name), Order.rating > 0).all()
        if relevant_orders:
            avg = sum(o.rating for o in relevant_orders) / len(relevant_orders)
            item.avg_rating = round(avg, 1)
            item.rating_count = len(relevant_orders)
        else:
            item.avg_rating = 0
            item.rating_count = 0
    return items

# --- ROUTES ---

@app.route('/sw.js')
def service_worker():
    return send_from_directory(app.static_folder, 'sw.js')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("!!! WARNING: A USER IS REGISTERING VIA THE STUDENT/FACULTY ROUTE !!!")
        
        email = request.form.get('email').lower()
        
        # --- NEW: Amity-Specific Domain Checking ---
        # Note: We must check STUDENT_DOMAIN before FACULTY_DOMAIN
        if email.endswith(STUDENT_DOMAIN):
            role = "Student"
        elif email.endswith(FACULTY_DOMAIN):
            role = "Faculty"
        else:
            flash(f"Registration is restricted to official {FACULTY_DOMAIN} or {STUDENT_DOMAIN} emails only!", "error")
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for('register'))

        otp = str(random.randint(100000, 999999))
        session['temp_user'] = {
            'full_name': request.form.get('full_name'),
            'email': email,
            'phone': request.form.get('phone'),
            'password': request.form.get('password'),
            'role': role,
            'otp': otp
        }
        if send_email_otp(email, otp):
            return redirect(url_for('verify_registration_otp'))
        else:
            flash("Failed to send email. Check internet connection.", "error")
    return render_template('register.html')

@app.route('/register_rider', methods=['GET', 'POST'])
def register_rider():
    if request.method == 'POST':
        print("!!! SUCCESS: A USER IS REGISTERING VIA THE RIDER ROUTE !!!")

        email = request.form.get('email').lower()
        
        # --- NEW: STRICT ROLE SEPARATION FOR RIDERS ---
        if email.endswith(STUDENT_DOMAIN) or email.endswith(FACULTY_DOMAIN):
            flash("Official College IDs cannot be used to register as a Delivery Partner.", "error")
            return redirect(url_for('register_rider'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for('register_rider'))

        otp = str(random.randint(100000, 999999))
        session['temp_user'] = {
            'full_name': request.form.get('full_name'),
            'email': email,
            'phone': request.form.get('phone'),
            'password': request.form.get('password'),
            'role': 'Delivery', 
            'otp': otp
        }
        if send_email_otp(email, otp):
            return redirect(url_for('verify_registration_otp'))
        else:
            flash("Failed to send email.", "error")
    return render_template('register_rider.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_registration_otp():
    if 'temp_user' not in session: return redirect(url_for('register'))
    if request.method == 'POST':
        if request.form.get('otp') == session['temp_user']['otp']:
            data = session['temp_user']
            new_user = User(
                full_name=data['full_name'], 
                email=data['email'], 
                phone=data['phone'], 
                role=data['role'], 
                password_hash=generate_password_hash(data['password'])
            )
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            session['username'] = new_user.full_name
            session['role'] = new_user.role
            session.pop('temp_user', None)
            
            if new_user.role == 'Delivery':
                return redirect(url_for('delivery_hub'))
            else:
                return redirect(url_for('index'))
        else:
            flash("Invalid OTP. Try again.", "error")
    return render_template('verify_otp.html', email=session['temp_user']['email'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            session['user_id'] = user.id
            session['username'] = user.full_name
            session['role'] = user.role 
            
            if user.role == 'Delivery':
                return redirect(url_for('delivery_hub'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if user.role == 'Delivery': return redirect(url_for('delivery_hub')) 
    return redirect(url_for('select_mode'))

# --- TEMPORARY DEVELOPER TOOL ---
@app.route('/make_me_rider')
def make_me_rider():
    user = get_user_or_logout()
    if user:
        user.role = 'Delivery'
        db.session.commit()
        session['role'] = 'Delivery'  # Update session immediately
        return "<h1>✅ Success!</h1><p>You are now a Delivery Partner.</p><a href='/delivery_hub'>Go to Delivery Hub</a>"
    return "Please Login first."

# --- TEMPORARY DEVELOPER TOOL: REVERT TO STUDENT ---
@app.route('/make_me_student')
def make_me_student():
    user = get_user_or_logout()
    if user:
        user.role = 'Student'
        db.session.commit()
        session['role'] = 'Student'  # Update session immediately
        return "<h1>✅ Success!</h1><p>You are now a Student again.</p><a href='/home'>Go to Home</a>"
    return "Please Login first."

@app.route('/select_mode')
def select_mode():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if user.role == 'Delivery': return redirect(url_for('delivery_hub')) 
    return render_template('choice.html')

@app.route('/set_mode/<mode>')
def set_mode(mode):
    session['order_mode'] = mode
    return redirect(url_for('home'))

@app.route('/home')
def home():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if user.role == 'Delivery': return redirect(url_for('delivery_hub')) 
    
    canteens = Canteen.query.all()
    mode = session.get('order_mode', 'Dine-in')
    return render_template('index.html', canteens=canteens, user=user, mode=mode)

@app.route('/canteen/<int:canteen_id>')
def menu(canteen_id):
    canteen = Canteen.query.get_or_404(canteen_id)
    items = MenuItem.query.filter_by(canteen_id=canteen_id).all()
    items = attach_item_ratings(items)
    return render_template('menu.html', canteen=canteen, items=items)

@app.route('/cart', methods=['POST'])
def add_to_cart():
    item_id = int(request.form.get('item_id'))
    item = MenuItem.query.get(item_id)
    if 'cart' not in session: session['cart'] = []
    cart = session['cart']
    
    found = False
    for cart_item in cart:
        if cart_item['id'] == item_id:
            cart_item['quantity'] += 1
            found = True
            break
    
    if not found:
        cart.append({'id': item.id, 'name': item.name, 'price': item.price, 'canteen_id': item.canteen_id, 'quantity': 1})
        
    session['cart'] = cart
    return redirect(url_for('menu', canteen_id=item.canteen_id))

@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    if 'cart' in session:
        cart = session['cart']
        if 0 <= index < len(cart):
            cart.pop(index)
            session['cart'] = cart
            session.modified = True
    return redirect(url_for('checkout'))

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    item_id = int(request.form.get('item_id'))
    action = request.form.get('action') 
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == item_id:
            if action == 'add': item['quantity'] += 1
            elif action == 'sub': item['quantity'] -= 1
            break
    cart = [item for item in cart if item['quantity'] > 0]
    session['cart'] = cart
    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if user.role == 'Delivery': return redirect(url_for('delivery_hub'))

    cart = session.get('cart', [])
    if not cart: return redirect(url_for('home'))
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    mode = session.get('order_mode', 'Dine-in')
    canteen = Canteen.query.get(cart[0]['canteen_id']) 

    if mode == 'Delivery' and 'delivery_info' not in session:
        return redirect(url_for('delivery_details_form'))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        pickup_time = request.form.get('pickup_time')
        final_time = "Standard (15-20 mins)"
        if pickup_time == 'Custom': final_time = request.form.get('scheduled_time') + " (Scheduled)"

        if payment_method == 'wallet':
            if user.wallet_balance < total:
                flash("Insufficient Wallet Balance!", "error")
                return redirect(url_for('checkout'))
            user.wallet_balance -= total
            transaction_type = "WALLET"
        else:
            transaction_type = "UPI_QR"

        d_info = session.get('delivery_info', {})
        summary_text = ", ".join([f"{i['name']} x{i['quantity']}" for i in cart])

        new_order = Order(
            user_id=user.id, canteen_id=cart[0]['canteen_id'], total_price=total, status="Pending",
            pickup_time=final_time, items_summary=summary_text, order_type=mode,
            customer_name=d_info.get('name', user.full_name), customer_phone=d_info.get('phone', user.phone),
            delivery_location=d_info.get('location', 'Counter Pickup'),
            otp=str(random.randint(100000, 999999)), transaction_id=f"{transaction_type}-{random.randint(1000,9999)}"
        )
        db.session.add(new_order)
        db.session.commit()
        session.pop('cart', None)
        session.pop('delivery_info', None)
        return redirect(url_for('my_orders'))
        
    return render_template('checkout.html', cart=cart, total=total, user=user, canteen=canteen)

@app.route('/account')
def account():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    order_count = Order.query.filter_by(user_id=user.id).count()
    return render_template('account.html', user=user, order_count=order_count)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.phone = request.form.get('phone')
        user.email = request.form.get('email')
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                filename = secure_filename(f"user_{user.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_pic = filename
        db.session.commit()
        session['username'] = user.full_name
        return redirect(url_for('account'))
    return render_template('edit_profile.html', user=user)

@app.route('/payment_methods')
def payment_methods():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    saved_methods = PaymentMethod.query.filter_by(user_id=user.id).all()
    # Pass the KEY_ID to the template so JS can use it
    return render_template('payment_methods.html', user=user, saved_methods=saved_methods, razorpay_key_id=RAZORPAY_KEY_ID)

@app.route('/add_payment_method', methods=['POST'])
def add_payment_method():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    method_type = request.form.get('method_type')
    new_method = None
    if method_type == 'Card':
        card_number = request.form.get('card_number')
        expiry = request.form.get('expiry')
        if len(card_number) == 16:
            provider = "Visa" if card_number.startswith('4') else "MasterCard"
            details = card_number[-4:] 
            color = random.choice(['linear-gradient(135deg, #2962FF, #304FFE)', 'linear-gradient(135deg, #FF6F00, #FF8F00)'])
            new_method = PaymentMethod(user_id=user.id, type='Card', provider=provider, details=details, expiry=expiry, color=color)
    elif method_type == 'UPI':
        upi_id = request.form.get('upi_id')
        if upi_id:
            provider = "UPI"
            if "@ok" in upi_id: provider = "Google Pay"
            elif "@ybl" in upi_id: provider = "PhonePe"
            new_method = PaymentMethod(user_id=user.id, type='UPI', provider=provider, details=upi_id)
    if new_method:
        db.session.add(new_method)
        db.session.commit()
    return redirect(url_for('payment_methods'))

@app.route('/delete_payment_method/<int:id>')
def delete_payment_method(id):
    user = get_user_or_logout()
    method = PaymentMethod.query.get(id)
    if method and method.user_id == user.id:
        db.session.delete(method)
        db.session.commit()
    return redirect(url_for('payment_methods'))

# --- NEW REAL PAYMENT ROUTES (Backbone for Real Money) ---

@app.route('/api/create_order', methods=['POST'])
def create_order():
    user = get_user_or_logout()
    if not user: return jsonify({'error': 'Not logged in'}), 401
    
    try:
        amount = float(request.json.get('amount'))
        # Razorpay expects amount in paise (1 INR = 100 paise)
        data = {
            "amount": int(amount * 100),
            "currency": "INR",
            "receipt": f"receipt_user_{user.id}",
            "payment_capture": 1
        }
        order = razorpay_client.order.create(data=data)
        return jsonify(order)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify_payment', methods=['POST'])
def verify_payment():
    user = get_user_or_logout()
    if not user: return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    try:
        # Verify Signature
        params_dict = {
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        # This function raises an error if signature is invalid
        razorpay_client.utility.verify_payment_signature(params_dict)

        # If we reach here, payment is REAL. Add money.
        amount_in_paise = data['amount']
        amount_in_rupees = amount_in_paise / 100
        
        user.wallet_balance += amount_in_rupees
        db.session.commit()
        
        return jsonify({'status': 'success', 'new_balance': user.wallet_balance})
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'error': 'Invalid Signature'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- OLD ADD MONEY ROUTE (Manual Fallback) ---
@app.route('/add_money', methods=['POST'])
def add_money():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    try:
        amount = float(request.form.get('amount'))
        # This logic is now bypassed if you use the Real Payment flow above
        if amount > 0:
            user.wallet_balance += amount
            db.session.commit()
            return redirect(url_for('payment_methods', success=1, amount=amount))
    except ValueError: pass
    return redirect(url_for('account'))

@app.route('/delivery_details', methods=['GET', 'POST'])
def delivery_details_form():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if request.method == 'POST':
        session['delivery_info'] = {'name': request.form.get('name'), 'location': request.form.get('location'), 'phone': request.form.get('phone')}
        return redirect(url_for('checkout'))
    return render_template('delivery_form.html', user=user)

@app.route('/my_orders')
def my_orders():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).all()
    return render_template('my_orders.html', orders=orders)

@app.route('/kitchen/<int:canteen_id>')
def kitchen_dashboard(canteen_id):
    canteen = Canteen.query.get_or_404(canteen_id)
    
    # --- NEW: STRICT FIFO ORDERING ---
    # We sort by timestamp.asc() so the OLDEST orders always appear at the top.
    # The kitchen will always cook for the person who ordered first!
    orders = Order.query.filter_by(canteen_id=canteen_id)\
                        .filter(Order.status != 'Delivered')\
                        .filter(Order.status != 'Cancelled')\
                        .order_by(Order.timestamp.asc())\
                        .all()
                        
    return render_template('kitchen.html', canteen=canteen, orders=orders)

@app.route('/update_status/<int:order_id>/<status>')
def update_status(order_id, status):
    order = Order.query.get(order_id)
    order.status = status
    db.session.commit()
    return redirect(url_for('kitchen_dashboard', canteen_id=order.canteen_id))

@app.route('/verify_order_otp', methods=['POST'])
def verify_order_otp():
    source = request.form.get('source')
    otp_code = request.form.get('otp_code')
    order_id = request.form.get('order_id')
    order = Order.query.get(order_id)
    if order and order.otp == otp_code:
        if source == 'kitchen': order.status = 'Picked Up' 
        elif source == 'delivery': order.status = 'Delivered' 
        elif source == 'sim': order.status = 'Delivered' 
        db.session.commit()
        flash("Verified Successfully!", "success")
    else:
        flash("Wrong OTP!", "error")
    if source == 'kitchen': return redirect(url_for('kitchen_dashboard', canteen_id=order.canteen_id))
    elif source == 'delivery': return redirect(url_for('delivery_hub'))
    elif source == 'sim': return redirect(url_for('my_orders'))
    return redirect(url_for('home'))

@app.route('/delivery_hub')
def delivery_hub():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if user.role != 'Delivery': return redirect(url_for('home'))
    
    # 1. Available Jobs (Ready, Delivery Type, No Rider Assigned yet)
    available_orders = Order.query.filter_by(status='Ready', order_type='Delivery', delivery_rider_id=None).all()
    
    # 2. My Active Deliveries (Picked Up by ME)
    my_active_orders = Order.query.filter_by(delivery_rider_id=user.id, status='Picked Up').all()
    
    # 3. My Track Record (Completed by ME)
    my_history = Order.query.filter_by(delivery_rider_id=user.id, status='Delivered').order_by(Order.id.desc()).all()
    total_delivered = len(my_history)

    return render_template('delivery_dashboard.html', 
                           available=available_orders, 
                           active=my_active_orders, 
                           history=my_history,
                           count=total_delivered, 
                           user=user)

@app.route('/pickup_order/<int:order_id>')
def pickup_order(order_id):
    user = get_user_or_logout()
    order = Order.query.get(order_id)
    
    # Assign the order to the current rider
    order.status = 'Picked Up'
    order.delivery_rider_id = user.id 
    
    db.session.commit()
    return redirect(url_for('delivery_hub'))

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if query.lower() == 'random':
        all_items = MenuItem.query.all()
        if all_items: return render_template('surprise.html', item=random.choice(all_items))
        return redirect(url_for('home'))
    if not query: return redirect(url_for('home'))
    
    search_results = MenuItem.query.filter(MenuItem.name.ilike(f"%{query}%")).all()
    search_results = attach_item_ratings(search_results)
    
    # --- NEW: Attach Canteen Location to Search Results ---
    for item in search_results:
        c = Canteen.query.get(item.canteen_id)
        if c:
            item.canteen_name = c.name
            item.canteen_location = c.location
            
    search_context = Canteen(name=f"Results for '{query}'", location="All Canteens")
    return render_template('menu.html', canteen=search_context, items=search_results)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    user = get_user_or_logout()
    if not user: return redirect(url_for('login'))
    if request.method == 'POST':
        msg_content = request.form.get('message')
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = SENDER_EMAIL 
            msg['Subject'] = f"App Feedback from {user.full_name}"
            body = f"User: {user.full_name}\nEmail: {user.email}\n\nFeedback:\n{msg_content}"
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
            server.quit()
            flash("Feedback sent!", "success")
        except: flash("Error sending feedback.", "error")
        return redirect(url_for('account'))
    return render_template('feedback.html')

@app.route('/cancel_order')
def cancel_order():
    session.pop('cart', None)
    session.pop('delivery_info', None)
    return redirect(url_for('home'))

@app.route('/rate_order', methods=['POST'])
def rate_order():
    user = get_user_or_logout()
    order_id = request.form.get('order_id')
    rating = request.form.get('rating')
    order = Order.query.get(order_id)
    if order and order.user_id == user.id:
        order.rating = int(rating)
        db.session.commit()
    return redirect(url_for('my_orders'))

@app.route('/api/kitchen/check/<int:canteen_id>')
def check_kitchen_orders(canteen_id):
    count = Order.query.filter_by(canteen_id=canteen_id).filter(Order.status.notin_(['Delivered', 'Cancelled'])).count()
    return jsonify({'count': count})

@app.route('/api/delivery/check')
def check_delivery_orders():
    count = Order.query.filter(Order.status.in_(['Ready', 'Picked Up']), Order.order_type == 'Delivery').count()
    return jsonify({'count': count})

@app.route('/api/user/check_status')
def check_user_status():
    user = get_user_or_logout()
    if not user: return jsonify({'status': 'none'})
    latest_order = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).first()
    if latest_order:
        return jsonify({'last_order_id': latest_order.id, 'status': latest_order.status})
    return jsonify({'status': 'none'})

@app.route('/api/kitchen/check_new/<int:canteen_id>')
def check_new_orders(canteen_id):
    count = Order.query.filter_by(canteen_id=canteen_id).filter(Order.status.notin_(['Delivered', 'Cancelled'])).count()
    return jsonify({'count': count})

@app.route('/api/delivery/check_new')
def check_delivery_updates():
    count = Order.query.filter(Order.status.in_(['Ready', 'Picked Up']), Order.order_type == 'Delivery').count()
    return jsonify({'count': count})

@app.route('/sw.js')
def sw():
    # This serves the file from your static/JS folder, 
    # but the browser thinks it's at the root level!
    return app.send_static_file('JS/sw.js')

# --- DATA SEEDING ---
if __name__ == '__main__':
    with app.app_context():
        # ENSURE UPLOAD FOLDER EXISTS
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        db.create_all()
        if not Canteen.query.first():
            canteens = [
                Canteen(name="Olympia", location="I2-Block", upi_id="7836914324-3@ybl"),
                Canteen(name="Tasty Foods", location="D-Block", upi_id="tastyfoods@okicici"),
                Canteen(name="Mint", location="F-Block", upi_id="mint.food@okhdfcbank"),
                Canteen(name="Catering Care", location="H-Block", upi_id="catering.care@okaxis")
            ]
            db.session.add_all(canteens)
            db.session.commit()
            
            def get_id(name): return Canteen.query.filter_by(name=name).first().id
            items = []
            cid = get_id("Olympia")
            items.extend([
                MenuItem(canteen_id=cid, name="Cold Coffee", price=60.0),
                MenuItem(canteen_id=cid, name="Veg Grilled Sandwich", price=50.0),
                MenuItem(canteen_id=cid, name="Chicken Burger", price=90.0, is_veg=False),
                MenuItem(canteen_id=cid, name="Paneer Wrap", price=80.0),
                MenuItem(canteen_id=cid, name="Chocolate Brownie", price=70.0),
                MenuItem(canteen_id=cid, name="Masala Chai", price=20.0),
                MenuItem(canteen_id=cid, name="French Fries", price=60.0),
                MenuItem(canteen_id=cid, name="Red Sauce Pasta", price=110.0),
                MenuItem(canteen_id=cid, name="Oreo Shake", price=80.0),
                MenuItem(canteen_id=cid, name="Chicken Nuggets", price=120.0, is_veg=False)
            ])
            cid = get_id("Tasty Foods")
            items.extend([
                MenuItem(canteen_id=cid, name="Chole Bhature", price=70.0),
                MenuItem(canteen_id=cid, name="Rajma Chawal", price=60.0),
                MenuItem(canteen_id=cid, name="Aloo Paratha", price=40.0),
                MenuItem(canteen_id=cid, name="Veg Thali", price=120.0),
                MenuItem(canteen_id=cid, name="Chicken Curry", price=150.0, is_veg=False),
                MenuItem(canteen_id=cid, name="Paneer Butter Masala", price=140.0),
                MenuItem(canteen_id=cid, name="Butter Naan", price=30.0),
                MenuItem(canteen_id=cid, name="Lassi", price=40.0),
                MenuItem(canteen_id=cid, name="Gulab Jamun", price=20.0),
                MenuItem(canteen_id=cid, name="Egg Curry", price=100.0, is_veg=False)
            ])
            cid = get_id("Mint")
            items.extend([
                MenuItem(canteen_id=cid, name="Masala Dosa", price=60.0),
                MenuItem(canteen_id=cid, name="Idli Sambar", price=40.0),
                MenuItem(canteen_id=cid, name="Vada Sambar", price=45.0),
                MenuItem(canteen_id=cid, name="Uttapam", price=70.0),
                MenuItem(canteen_id=cid, name="Mysore Masala Dosa", price=80.0),
                MenuItem(canteen_id=cid, name="Upma", price=30.0),
                MenuItem(canteen_id=cid, name="Filter Coffee", price=25.0),
                MenuItem(canteen_id=cid, name="Rava Dosa", price=75.0),
                MenuItem(canteen_id=cid, name="Sambhar Rice", price=50.0),
                MenuItem(canteen_id=cid, name="Curd Rice", price=60.0)
            ])
            cid = get_id("Catering Care")
            items.extend([
                MenuItem(canteen_id=cid, name="Chicken Biryani", price=160.0, is_veg=False),
                MenuItem(canteen_id=cid, name="Veg Biryani", price=120.0),
                MenuItem(canteen_id=cid, name="Fried Rice", price=80.0),
                MenuItem(canteen_id=cid, name="Hakka Noodles", price=80.0),
                MenuItem(canteen_id=cid, name="Manchurian", price=90.0),
                MenuItem(canteen_id=cid, name="Chilli Chicken", price=140.0, is_veg=False),
                MenuItem(canteen_id=cid, name="Chilli Paneer", price=130.0),
                MenuItem(canteen_id=cid, name="Egg Roll", price=50.0, is_veg=False),
                MenuItem(canteen_id=cid, name="Schezwan Noodles", price=90.0),
                MenuItem(canteen_id=cid, name="Manchow Soup", price=60.0)
            ])
            db.session.add_all(items)
            db.session.commit()
            print("✅ 50 Food Items Added!")

    app.run(debug=True, host='0.0.0.0')