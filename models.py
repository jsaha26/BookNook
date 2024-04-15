from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)


# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    books = db.relationship('Book', secondary='user_book', backref='users', lazy=True)  # Updated relationship
    orders = db.relationship('Order', backref='user', lazy=True)


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True,
                      default='https://images.unsplash.com/photo-1603058817990-2b9a9abbce86?crop=entropy&cs=tinysrgb&fit=crop&fm=jpg&h=900&ixid=MnwxfDB8MXxyYW5kb218MHx8Ym9va3N8fHx8fHwxNzEyMzc5MTU0&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1600')
    books = db.relationship('Book', backref='section', lazy=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True,
                      default='https://images.unsplash.com/photo-1622006816342-36fe7754b0c9?q=80&w=1887&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')
    date_created = db.Column(db.Date, nullable=False)
    download_price = db.Column(db.Float, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

    # Relationships
    requests = db.relationship('UserRequest', backref='book', lazy=True)
    ratings = db.relationship('Rating', backref='book', lazy=True)
    orders = db.relationship('Order', backref='book', lazy=True)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref='ratings', lazy=True)


user_book = db.Table('user_book',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
                     )


class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship('User', backref='requests', lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    is_delivered = db.Column(db.Boolean, nullable=False, default=False)


with app.app_context():
    db.create_all()  # create tables if they do not exist
    admin = User.query.filter_by(is_admin=True).first()  # check if admin exists

    if not admin:  # if admin does not exist
        password_hash = generate_password_hash('admin')  # hash the password
        admin = User(username='admin', passhash=password_hash, name='Admin', is_admin=True)  # create admin
        db.session.add(admin)  # add admin to the session
        db.session.commit()
