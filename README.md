# BookNook
# Library Management System

**Author**: Jyotiraditya Saha

## Description
The Library Management System allows users to request, read, download, and review books, while providing admins or librarians with tools to manage sections, books, and user requests.

---

## Technologies Used
- **Flask**: Lightweight Python web framework for handling HTTP requests and rendering templates.
- **Flask-SQLAlchemy**: Enables interaction with the database using SQLAlchemy.
- **Flask-Migrate**: Manages database migrations.
- **Flask-Login**: Handles user sessions and secure authentication.
- **Flask-WTF**: Integrates WTForms for form validation and rendering.
- **Flask-Session**: Supports server-side session data management.
- **Flask-Flash**: Displays user messages for improved UX.
- **Flask-Uploads**: Manages file uploads for book images and content.
- **Flask-Admin**: Provides CRUD interfaces for easy database management.
- **Flask-RESTful**: Simplifies creation of RESTful APIs.
- **Werkzeug**: Utility library for password hashing and file uploads.
- **Jinja2**: Templating engine for dynamic HTML generation.
- **HTML, CSS, Bootstrap**: Frontend development for a user-friendly interface.
- **JavaScript**: Enhances interactivity and dynamic elements like charts.

---

## Database Schema Design
The database schema includes several tables representing different entities:

1. **User**
   - `id`: Primary key.
   - `username`: Unique username (not nullable).
   - `passhash`: Hashed password (not nullable).
   - `name`: Optional name of the user.
   - `is_admin`: Boolean flag (default: False).
   - **Relationships**:
     - Many-to-many with Book (via `user_book` association table).
     - One-to-many with `UserRequest` and `Rating`.

2. **Section**
   - `id`: Primary key.
   - `name`: Section name (not nullable).
   - `date_created`: Date of creation.
   - `description`: Section description.
   - `image`: Optional image URL.
   - **Relationships**:
     - One-to-many with `Book`.

3. **Book**
   - `id`: Primary key.
   - `title`: Book title (not nullable).
   - `content_type`: Type of content (Link or PDF).
   - `content`: URL/path to content file.
   - `author`: Author (not nullable).
   - `image`: Optional image URL.
   - `date_created`: Date of creation.
   - `download_price`: Price for downloading.
   - **Relationships**:
     - One-to-many with `Rating` and `UserRequest`.
     - Many-to-one with `Section`.

4. **Rating**
   - `id`: Primary key.
   - `book_id`: Foreign key for Book.
   - `user_id`: Foreign key for User.
   - `rating`: Numeric rating (not nullable).
   - `feedback`: Optional feedback text.
   - **Relationship**:
     - One-to-many with User.

5. **UserRequest**
   - `id`: Primary key.
   - `user_id`: Foreign key for User.
   - `book_id`: Foreign key for Book.
   - `request_date`: Date of request.
   - `return_date`: Expected return date.
   - `is_active`: Boolean flag for active requests.
   - **Relationship**:
     - One-to-many with User.

---

## API Design
The `/api/section` endpoint provides access to section data. The `SectionResource` class handles GET requests, returning JSON with properties: `id`, `name`, `date_created`, `description`, and `image`.

---

## Architecture
The project follows the Model-View-Controller (MVC) architecture:

- **Controllers (`routes.py`)**: Define routes, handle request/response cycle, perform validation.
- **Models (`models.py`)**: Define database schema and business logic.
- **Configurations (`config.py`)**: Centralize settings like database connections and security.
- **Application (`app.py`)**: Initializes Flask, registers components, and configures settings.
- **APIs (`api.py`)**: Define RESTful endpoints and request handling.
- **Templates (`templates/`)**: HTML templates for presentation.

---

## Features
- **User Registration and Login**: Secure login with hashed passwords.
- **User Profile**: View and update profile details.
- **Authentication and Authorization**: Restricted access based on roles.
- **Book and Section Management**: Admin can add, edit, and delete books and sections.
- **RESTful API for Sections**: Provides API endpoint for section retrieval.
- **Book Search and Filtering**: Search for books by section, title, or author.
- **Book Requests**: Request to borrow books, with admin approval.
- **Book Checkout and Return**: Track user borrowing history.
- **Book Reviews and Ratings**: Submit and display reviews for books.
- **User Book History**: View past requests and borrowing history.
- **Access Revocation**: Admins can revoke user access to specific books.
- **PDF Download**: Download books with PDF content.

---

## Demonstration Video
[Watch the demo](https://drive.google.com/file/d/1IpSocRw65N-zt54_SEbjOW_mI99lbda3/view)
