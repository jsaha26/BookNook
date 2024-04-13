
from dotenv import load_dotenv
import os
from app import app
load_dotenv() # Load environment variables from .env file

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['UPLOAD_CONTENT'] = 'static/content'