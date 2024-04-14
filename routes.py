from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import UserRequest, db, User, Section, Book, user_book
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import csv
import os
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import send_from_directory

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Please fill out all fields')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash('Username does not exist')
        return redirect(url_for('login'))
    
    if not check_password_hash(user.passhash, password):
        flash('Incorrect password')
        return redirect(url_for('login'))
    
    session['user_id'] = user.id
    flash('Login successful')
    return redirect(url_for('index'))


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')

    if not username or not password or not confirm_password:
        flash('Please fill out all fields')
        return redirect(url_for('register'))
    
    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists')
        return redirect(url_for('register'))
    
    password_hash = generate_password_hash(password)
    
    new_user = User(username=username, passhash=password_hash, name=name)
    db.session.add(new_user)
    db.session.commit()
    flash('Registered successfully')
    return redirect(url_for('login'))

# decorator for auth_required

def auth_required(func): 
    @wraps(func) 
    def inner(*args, **kwargs): 
        if 'user_id' in session: 
            return func(*args, **kwargs) 
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash('You are not authorized to access this page')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return inner


@app.route('/profile')
@auth_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/profile', methods=['POST'])
@auth_required
def profile_post():
    username = request.form.get('username')
    cpassword = request.form.get('cpassword')
    password = request.form.get('password')
    name = request.form.get('name')

    if not username or not cpassword or not password:
        flash('Please fill out all the required fields')
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    if not check_password_hash(user.passhash, cpassword):
        flash('Incorrect password')
        return redirect(url_for('profile'))
    
    if username != user.username:
        new_username = User.query.filter_by(username=username).first()
        if new_username:
            flash('Username already exists')
            return redirect(url_for('profile'))
    
    new_password_hash = generate_password_hash(password)
    user.username = username
    user.passhash = new_password_hash
    user.name = name
    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for('profile'))

    
@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

# --- admin pages

@app.route('/admin')
@admin_required
def admin():
    sections = Section.query.all()
    section_names = [section.name for section in sections]
    section_sizes = [len(section.books) for section in sections]

    query = request.args.get('query')
    if query:
        filtered_sections = []
        for section in sections:
            if (query.lower() in section.name.lower()) or any(query.lower() in book.title.lower() or query.lower() in book.author.lower() for book in section.books):
                filtered_sections.append(section)
        return render_template('admin.html', sections=filtered_sections, query=query)
    
    return render_template('admin.html', sections=sections, section_names=section_names, section_sizes=section_sizes)
@app.route('/section/add')
@admin_required
def add_section():
    return render_template('section/add.html')

@app.route('/section/add', methods=['POST'])
@admin_required
def add_section_post():
    name = request.form.get('name')
    image = request.files.get('image')
    description = request.form.get('description')

    if not name or not description:
        flash('Please fill out all required fields')
        return redirect(url_for('add_section'))
    
    date_created = datetime.utcnow()

    section = Section(name=name, date_created=date_created, description=description)

    if image:
        filename = secure_filename(image.filename) # secure the filename
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Make sure the static/images directory exists
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # Save the image to the static/images directory
        image.save(image_path)  # Set the image path for the section
        section.image = image_path

    db.session.add(section)
    db.session.commit()

    flash('Section added successfully')
    return redirect(url_for('admin'))    

    
@app.route('/section/<int:id>/')
@admin_required
def show_section(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('admin'))
    
    # Base query for books in this section
    books_query = Book.query.filter_by(section_id=id)

    # Get title and author from request args
    title = request.args.get('title', '')
    author = request.args.get('author', '')

    print("Title:", title)
    print("Author:", author)

    # Apply filters if title or author are provided
    if title:
        print("Filtering by title:", title)
        books_query = books_query.filter(Book.title.contains(title))
    if author:
        print("Filtering by author:", author)
        books_query = books_query.filter(Book.author.contains(author))

    # Fetch filtered books
    books = books_query.all()

    print("Filtered Books:", books)

    return render_template('section/show.html', section=section, books=books, title=title, author=author)

# Serve section images
@app.route('/section/<int:id>/static/images/<path:filename>') # path:filename is used to match the entire path after /static/images/
def section_image(id, filename): # id is not used, but it is required to match the route
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename) # Send the file from the static/images directory


@app.route('/section/<int:id>/edit')
@admin_required
def edit_section(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('admin'))
    return render_template('section/edit.html', section=section)

@app.route('/section/<int:id>/edit', methods=['POST'])
@admin_required
def edit_section_post(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('admin'))
    name = request.form.get('name')
    image = request.files.get('image')
    description = request.form.get('description')

    if not name or not description:
        flash('Please fill out all fields')
        return redirect(url_for('edit_section', id=id))
    
    section.name = name
    section.description = description

    if image:
        filename = secure_filename(image.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        section.image = image_path

    db.session.commit()
    flash('Section edited successfully')
    return redirect(url_for('admin'))
    

@app.route('/section/<int:id>/delete')
@admin_required
def delete_section(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('admin'))
    return render_template('section/delete.html', section=section)


@app.route('/section/<int:id>/delete', methods=['POST'])
@admin_required
def delete_section_post(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('admin'))
    # Delete all books in the section before deleting the section
    books = Book.query.filter_by(section_id=id).all()
    for book in books:
        # Delete all user requests for the book
        user_requests = UserRequest.query.filter_by(book_id=book.id).all()
        for user_request in user_requests:
            db.session.delete(user_request)
        db.session.delete(book)
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully')
    return redirect(url_for('admin'))

@app.route('/book/add/<int:section_id>')
@admin_required
def add_book(section_id):
    sections = Section.query.all() 
    section = Section.query.get(section_id) # get the section with the given id
    if not section:
        flash('Section does not exist')
        return redirect(url_for('admin'))
    now = datetime.now().strftime('%Y-%m-%d')
    return render_template('book/add.html', section=section, sections=sections, date_created=now)

@app.route('/book/add/', methods=['POST'])
@admin_required
def add_book_post():
    title = request.form.get('title')
    author = request.form.get('author')
    content_type = request.form.get('content_type')
    if content_type == "pdf":
        content_file = request.files.get('content_file')
        filename = secure_filename(content_file.filename)
        os.makedirs(app.config['UPLOAD_CONTENT'], exist_ok=True)
        content_path = os.path.join(app.config['UPLOAD_CONTENT'], filename)
        content_file.save(content_path)
        content = content_path

    else:
        content = request.form.get('content_link')


    image = request.files.get('image')
    section_id = request.form.get('section_id')
    date_created = datetime.utcnow()

    section = Section.query.get(section_id)  # Get the section with the given id
    if not section:
        flash('Section does not exist')
        return redirect(url_for('admin'))

    if not title or not author or not content or not section_id:
        flash('Please fill out all fields')
        return redirect(url_for('add_book', section_id=section_id))

    book = Book(title=title, author=author, content_type=content_type, content=content, date_created=date_created, section_id=section_id)

    if image:
        filename = secure_filename(image.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        book.image = image_path

    flash('Book added successfully')
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('show_section', id=section_id))

@app.route('/book/<int:id>/view')
@admin_required
def view_book(id):
    book = Book.query.get(id)
    if not book:
        flash('book does not exist')
        return redirect(url_for('admin'))
    return render_template('book/view.html', book=book)

# # Serve PDF content
# @app.route('/book/<int:id>/static/content/<path:filename>') # path:filename is used to match the entire path after /static/content/
# def book_content(id, filename): # id is not used, but it is required to match the route
#     return send_from_directory(app.config['UPLOAD_CONTENT'], filename) # Send the file from the static/content directory

@app.route('/book/<int:id>/pdf')
def serve_pdf(id):
    book = Book.query.get(id)
    if book and book.content_type == "pdf":
        return send_from_directory(app.config['UPLOAD_CONTENT'], os.path.basename(book.content))
    else:
        # Handle case where the book or content type is not found
        os.abort(404) # Return a 404 error
  

@app.route('/book/<int:id>/edit')
@admin_required
def edit_book(id):
    sections = Section.query.all()
    book = Book.query.get(id)
    return render_template('book/edit.html', sections=sections, book=book)

@app.route('/book/<int:id>/edit', methods=['POST'])
@admin_required
def edit_book_post(id):
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('admin'))
    title = request.form.get('title')
    author = request.form.get('author')
    content = request.form.get('content')
    image = request.files.get('image')
    section_id = request.form.get('section_id')

    if not title or not author or not content or not section_id:
        flash('Please fill out all fields')
        return redirect(url_for('edit_book', id=id))

    book.title = title
    book.author = author
    book.content = content
    book.section_id = section_id

    if image:
        filename = secure_filename(image.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        book.image = image_path

    db.session.commit()
    flash('Book edited successfully')
    return redirect(url_for('show_section', id=section_id))


@app.route('/book/<int:id>/delete')
@admin_required
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        flash('book does not exist')
        return redirect(url_for('admin'))
    return render_template('book/delete.html', book=book)

@app.route('/book/<int:id>/delete', methods=['POST'])
@admin_required
def delete_book_post(id):
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('admin'))
    section_id = book.section.id
    db.session.delete(book)
    db.session.commit()

    flash('Book deleted successfully')
    return redirect(url_for('show_section', id=section_id))

@app.route('/requests')
@admin_required
def requests():
    user_requests = UserRequest.query.filter_by(is_active=True).all()
    return render_template('requests.html', user_requests=user_requests)

@app.route('/requests/<int:id>/view')
@admin_required
def view_request(id):
    user_request = UserRequest.query.get(id)
    if not user_request:
        flash('Request does not exist')
        return redirect(url_for('requests'))
    return render_template('requests/view.html', user_request=user_request)

@app.route('/requests/<int:id>/grant')
@admin_required
def grant_request(id):
    user_request = UserRequest.query.get(id)
    if not user_request:
        flash('Request does not exist')
        return redirect(url_for('requests'))
    user_request.is_active = False
    book = Book.query.get(user_request.book_id)
    book.users.append(User.query.get(user_request.user_id))
    book.date_issued = user_request.request_date
    book.return_date = user_request.return_date
    db.session.commit()
    flash('Request granted successfully')
    return redirect(url_for('requests'))


@app.route('/requests/<int:id>/reject')
@admin_required
def reject_request(id):
    user_request = UserRequest.query.get(id)
    if not user_request:
        flash('Request does not exist')
        return redirect(url_for('requests'))
    user_request.is_active = False
    db.session.commit()
    flash('Request rejected successfully')
    return redirect(url_for('requests'))

# Define a route to render the page
@app.route('/granted_books')
def granted_books():
    # Fetch all users with granted books
    users_with_books = User.query.filter(User.books.any()).all()
    return render_template('granted_books.html', users_with_books=users_with_books)

# Define a route to revoke book access
@app.route('/revoke_access/<int:user_id>/<int:book_id>', methods=['POST'])
def revoke_access(user_id, book_id):
    # Find the user and book
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    if user and book:
        # Remove the book from the user's list of granted books
        user.books.remove(book)
        db.session.commit()
        flash('Access revoked successfully')
    return redirect(url_for('granted_books')) 





# ---- user routes  

@app.route('/')
@auth_required
def index():
    user = User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))

    sections = Section.query.all()

    section_id = request.args.get('sid') 
    book_name = request.args.get('bname')
    author_name = request.args.get('aname')

    # Filtering based on search parameters
    filtered_sections = []
    for section in sections:
        filtered_books = []
        for book in section.books:
            if (not section_id or section_id == str(section.id)) and \
               (not book_name or book_name.lower() in book.title.lower()) and \
               (not author_name or author_name.lower() in book.author.lower()):
                filtered_books.append(book)
        if filtered_books:
            filtered_section = section
            filtered_section.books = filtered_books
            filtered_sections.append(filtered_section)

    return render_template('index.html', sections=filtered_sections, sid=section_id, bname=book_name, aname=author_name)


@app.route('/request_ebook/<int:book_id>', methods=['POST'])
def request_ebook(book_id):
    user_id = session['user_id']
    book = Book.query.get(book_id)
    if not book:
        flash('book does not exist')
        return redirect(url_for('index'))
    
    request_date = datetime.now().date()
    return_date = request_date + timedelta(days=7) # 7 days from request date
    user_request = UserRequest.query.filter_by(user_id=user_id, book_id=book_id, is_active=True).first()

    if user_request:
        flash('You have already requested this book')
        return redirect(url_for('index'))
    else:
        user_request = UserRequest(user_id=user_id, book_id=book_id, request_date=request_date, return_date=return_date, is_active=True)
        db.session.add(user_request)
    db.session.commit()
    
    flash('Book requested successfully')
    return redirect(url_for('index'))


@app.route('/return_book/<int:book_id>', methods=['POST'])
def return_book(book_id):
    user_id = session['user_id']
    user_request = UserRequest.query.filter_by(user_id=user_id, book_id=book_id, is_active=True).first()
    if user_request:
        user_request.is_active = False
        db.session.commit()

        # Update the requested flag in the Book model
        book = Book.query.get(book_id)
        book.requested = False
        db.session.commit()

        flash('Book returned successfully')
    return redirect(url_for('index'))

@app.route('/my_requests')
@auth_required
def my_requests():
    user_id = session['user_id']
    user_requests = UserRequest.query.filter_by(user_id=user_id, is_active=True).all()
    return render_template('my_requests.html', user_requests=user_requests)

@app.route('/my_requests/<int:id>/cancel')
@auth_required
def cancel_request(id):
    user_request = UserRequest.query.get(id)
    if not user_request:
        flash('Request does not exist')
        return redirect(url_for('my_requests'))
    if user_request.user_id != session['user_id']:
        flash('You are not authorized to access this page')
        return redirect(url_for('my_requests'))
    if not user_request.is_active:
        flash('Request already cancelled')
        return redirect(url_for('my_requests'))
    db.session.delete(user_request)
    db.session.commit()
    flash('Request cancelled successfully')
    return redirect(url_for('my_requests'))

@app.route('/my_books')
@auth_required
def my_books():
    user_id = session['user_id']
    user = User.query.get(user_id)
    books = user.books
    return render_template('my_books.html', books=books)

@app.route('/my_books/<int:id>/read')
@auth_required
def read_my_book(id):
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('my_books'))
    return render_template('my_books/read.html', book=book)

@app.route('/my_books/<int:id>/return')
@auth_required
def return_my_book(id):
    user_id = session['user_id']
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('my_books'))
    if not book.users or user_id not in [user.id for user in book.users]:
        flash('You are not authorized to access this page')
        return redirect(url_for('my_books'))
    user = User.query.get(user_id)
    user.books.remove(book)
    db.session.commit()
    flash('Book returned successfully')
    return redirect(url_for('my_books'))





# @app.route('/checkout', methods=['POST'])
# @auth_required
# def checkout():
#     carts = Cart.query.filter_by(user_id=session['user_id']).all()
#     if not carts:
#         flash('Cart is empty')
#         return redirect(url_for('cart'))

#     transaction = Transaction(user_id=session['user_id'], datetime=datetime.now())
#     for cart in carts:
#         order = Order(transaction=transaction, book=cart.book, quantity=cart.quantity, price=cart.book.price)
#         if cart.book.quantity < cart.quantity:
#             flash(f'book {cart.book.name} is out of stock')
#             return redirect(url_for('delete_cart', id=cart.id))
#         cart.book.quantity -= cart.quantity
#         db.session.add(order)
#         db.session.delete(cart)
#     db.session.add(transaction)
#     db.session.commit()

#     flash('Order placed successfully')
#     return redirect(url_for('orders'))

# @app.route('/orders')
# @auth_required
# def orders():
#     transactions = Transaction.query.filter_by(user_id=session['user_id']).order_by(Transaction.datetime.desc()).all()
#     return render_template('orders.html', transactions=transactions)

# @app.route('/export_csv')
# @auth_required
# def export_csv():
#     transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
#     filename = uuid4().hex + '.csv'
#     url = 'static/csv/' + filename
#     with open(url, 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(['transaction_id', 'datetime', 'book_name', 'quantity', 'price'])
#         for transaction in transactions:
#             for order in transaction.orders:
#                 writer.writerow([transaction.id, transaction.datetime, order.book.name, order.quantity, order.price])
#     return redirect(url_for('static', filename='csv/'+filename))