from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Student")
    wallet_balance = db.Column(db.Float, default=500.0)
    profile_pic = db.Column(db.String(150), default='default.png')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    payment_methods = db.relationship('PaymentMethod', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'wallet_balance': self.wallet_balance,
            'profile_pic': self.profile_pic
        }


class Canteen(db.Model):
    __tablename__ = 'canteens'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    upi_id = db.Column(db.String(100), nullable=False, default="admin@okaxis")
    description = db.Column(db.String(500))
    image = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    
    menu_items = db.relationship('MenuItem', backref='canteen', lazy='dynamic')
    orders = db.relationship('Order', backref='canteen', lazy='dynamic')
    
    def __repr__(self):
        return f'<Canteen {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'upi_id': self.upi_id,
            'description': self.description,
            'image': self.image,
            'rating': self.rating
        }


class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteens.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    is_veg = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50), default='General')
    image = db.Column(db.String(150))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'canteen_id': self.canteen_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'is_veg': self.is_veg,
            'category': self.category,
            'image': self.image,
            'is_available': self.is_available
        }


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteens.id'), nullable=False, index=True)
    delivery_rider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending", index=True)
    order_type = db.Column(db.String(20), default="Dine-in")
    
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    delivery_location = db.Column(db.String(200))
    pickup_time = db.Column(db.String(50))
    
    items_summary = db.Column(db.String(500))
    otp = db.Column(db.String(6))
    transaction_id = db.Column(db.String(50), unique=True)
    rating = db.Column(db.Integer, default=0)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rider = db.relationship('User', foreign_keys=[delivery_rider_id], backref='deliveries')
    
    def __repr__(self):
        return f'<Order {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'canteen_id': self.canteen_id,
            'total_price': self.total_price,
            'status': self.status,
            'order_type': self.order_type,
            'items_summary': self.items_summary,
            'otp': self.otp,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(20))
    provider = db.Column(db.String(50))
    details = db.Column(db.String(100))
    expiry = db.Column(db.String(10))
    color = db.Column(db.String(100))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentMethod {self.type} - {self.provider}>'


class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='wallet_transactions')
    
    def __repr__(self):
        return f'<WalletTransaction {self.transaction_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(20), default='general')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id}>'


def seed_data():
    from .app import db
    
    if Canteen.query.first():
        return
    
    canteens = [
        Canteen(name="Olympia", location="I2-Block", upi_id="7836914324-3@ybl", 
                description="Popular spot for snacks and beverages", rating=4.2),
        Canteen(name="Tasty Foods", location="D-Block", upi_id="tastyfoods@okicici",
                description="North Indian & South Indian cuisines", rating=4.0),
        Canteen(name="Megabite", location="E1-Block", upi_id="megabite@oklink",
                description="Fast food and continental", rating=3.8),
        Canteen(name="Mint", location="F-Block", upi_id="mint.food@okhdfcbank",
                description="South Indian specialties", rating=4.1),
        Canteen(name="Catering Care", location="H-Block", upi_id="catering.care@okaxis",
                description="Biryani and Chinese", rating=3.9)
    ]
    db.session.add_all(canteens)
    db.session.commit()
    
    menu_items_data = {
        "Olympia": [
            ("Cold Coffee", 60.0, True, "Beverages"),
            ("Veg Grilled Sandwich", 50.0, True, "Snacks"),
            ("Chicken Burger", 90.0, False, "Burgers"),
            ("Paneer Wrap", 80.0, True, "Wraps"),
            ("Chocolate Brownie", 70.0, True, "Desserts"),
            ("Masala Chai", 20.0, True, "Beverages"),
            ("French Fries", 60.0, True, "Snacks"),
            ("Red Sauce Pasta", 110.0, True, "Pasta"),
            ("Oreo Shake", 80.0, True, "Beverages"),
            ("Chicken Nuggets", 120.0, False, "Snacks")
        ],
        "Tasty Foods": [
            ("Chole Bhature", 70.0, True, "North Indian"),
            ("Rajma Chawal", 60.0, True, "North Indian"),
            ("Aloo Paratha", 40.0, True, "North Indian"),
            ("Veg Thali", 120.0, True, "Thali"),
            ("Chicken Curry", 150.0, False, "Curries"),
            ("Paneer Butter Masala", 140.0, True, "Curries"),
            ("Butter Naan", 30.0, True, "Breads"),
            ("Lassi", 40.0, True, "Beverages"),
            ("Gulab Jamun", 20.0, True, "Desserts"),
            ("Egg Curry", 100.0, False, "Curries")
        ],
        "Megabite": [
            ("Cheese Pizza", 150.0, True, "Pizza"),
            ("Chicken Pepperoni", 200.0, False, "Pizza"),
            ("Garlic Bread", 80.0, True, "Starters"),
            ("White Sauce Pasta", 130.0, True, "Pasta"),
            ("Coke (500ml)", 40.0, True, "Beverages"),
            ("Veg Burger", 50.0, True, "Burgers"),
            ("Chicken Roll", 90.0, False, "Rolls"),
            ("Momos (Steam)", 60.0, True, "Momos"),
            ("Momos (Fried)", 70.0, True, "Momos"),
            ("Spring Roll", 60.0, True, "Starters")
        ],
        "Mint": [
            ("Masala Dosa", 60.0, True, "South Indian"),
            ("Idli Sambar", 40.0, True, "South Indian"),
            ("Vada Sambar", 45.0, True, "South Indian"),
            ("Uttapam", 70.0, True, "South Indian"),
            ("Mysore Masala Dosa", 80.0, True, "South Indian"),
            ("Upma", 30.0, True, "South Indian"),
            ("Filter Coffee", 25.0, True, "Beverages"),
            ("Rava Dosa", 75.0, True, "South Indian"),
            ("Sambhar Rice", 50.0, True, "Rice"),
            ("Curd Rice", 60.0, True, "Rice")
        ],
        "Catering Care": [
            ("Chicken Biryani", 160.0, False, "Biryani"),
            ("Veg Biryani", 120.0, True, "Biryani"),
            ("Fried Rice", 80.0, True, "Rice"),
            ("Hakka Noodles", 80.0, True, "Noodles"),
            ("Manchurian", 90.0, True, "Chinese"),
            ("Chilli Chicken", 140.0, False, "Chinese"),
            ("Chilli Paneer", 130.0, True, "Chinese"),
            ("Egg Roll", 50.0, False, "Rolls"),
            ("Schezwan Noodles", 90.0, True, "Noodles"),
            ("Manchow Soup", 60.0, True, "Soups")
        ]
    }
    
    all_items = []
    for canteen in canteens:
        items_data = menu_items_data.get(canteen.name, [])
        for name, price, is_veg, category in items_data:
            all_items.append(MenuItem(
                canteen_id=canteen.id,
                name=name,
                price=price,
                is_veg=is_veg,
                category=category
            ))
    
    db.session.add_all(all_items)
    db.session.commit()
    print(f"✓ Seeded {len(canteens)} canteens and {len(all_items)} menu items")
