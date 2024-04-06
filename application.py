from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'

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
    date_created = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    books = db.relationship('Book', backref='section', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date_issued = db.Column(db.String(100), nullable=False)
    return_date = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

# Routes
@app.route('/')
def index():
    sections = Section.query.all()
    return render_template('index.html', sections=sections)

@app.route('/section/<int:section_id>')
def section_detail(section_id):
    section = Section.query.get(section_id)
    books = Book.query.filter_by(section_id=section_id).all()
    return render_template('section_detail.html', section=section, books=books)

# Add more routes for other functionalities

if __name__ == '__main__':
    app.run(debug=True)
