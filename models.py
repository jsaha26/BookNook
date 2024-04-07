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

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True, default = 'https://images.unsplash.com/photo-1603058817990-2b9a9abbce86?crop=entropy&cs=tinysrgb&fit=crop&fm=jpg&h=900&ixid=MnwxfDB8MXxyYW5kb218MHx8Ym9va3N8fHx8fHwxNzEyMzc5MTU0&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1600')
    books = db.relationship('Book', backref='section', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True, default = 'https://images.unsplash.com/photo-1622006816342-36fe7754b0c9?q=80&w=1887&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')
    date_created = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # user who has been issued the book
    date_issued = db.Column(db.String(100), nullable=True)
    return_date = db.Column(db.String(100), nullable=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

with app.app_context():
    db.create_all()
    # if admin exists, else create admin
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        password_hash = generate_password_hash('admin')
        admin = User(username='admin', passhash=password_hash, name='Admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()