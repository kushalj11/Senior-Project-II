# BookShelf

A web-based reading management platform where users can discover books, track reading progress, write reviews, and connect with other readers.

## Features

- **User Authentication**: Secure registration and login with password hashing
- **Book Database**: Community-built database with search functionality
- **Reading Shelves**: Organize books into Want to Read, Currently Reading, Finished, and custom shelves
- **Progress Tracking**: Track reading progress by pages or percentage
- **Reviews & Ratings**: 1-5 star ratings with optional text reviews
- **Social Features**: Follow other users and view activity feeds
- **Public Profiles**: View other readers' shelves and reviews
- **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the Project**
   ```bash
   git clone https://github.com/kushalj11/Senior-Project-II.git
   cd Senior-Project-II
   ```

2. **Create a Virtual Environment** (Recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Open in Browser**
   - Navigate to: `http://localhost:5000`
   - The application will automatically create the database on first run

6. **[Optional] Add Sample Books**
   ```bash
   # Stop the app (Ctrl+C) and run:
   python seed_books.py
   
   # This will add 25 classic books to browse
   # Then restart: python app.py
   ```

## Project Structure

```
Bookshelf/
├── app.py                  # Main Flask application with all routes
├── models.py               # Database models (User, Book, Shelf, Review)
├── seed_books.py           # Script to add 25 sample books to database
├── requirements.txt        # Python dependencies
├── bookshelf.db           # SQLite database (created on first run)
├── static/
│   ├── css/
│   │   └── style.css      # All styling
│   ├── js/
│   │   └── main.js        # Client-side JavaScript
│   └── uploads/
│       └── covers/        # Book cover images (created on first run)
└── templates/
    ├── base.html           # Base template with sidebar
    ├── index.html          # Landing page
    ├── register.html       # Registration page
    ├── login.html          # Login page
    ├── dashboard.html      # User dashboard
    ├── search.html         # Book search page
    ├── book_detail.html    # Individual book details
    ├── add_book.html       # Add new book form
    ├── shelves.html        # All user shelves
    ├── shelf_detail.html   # Individual shelf with books
    ├── users_list.html     # List of all users
    ├── user_profile.html   # User profile page
    └── activity_feed.html  # Activity feed from followed users
```

## Usage Guide

### Getting Started

1. **Create an Account**
   - Click "Sign Up" on the homepage
   - Provide username, email, and password (min 8 characters)
   - Three default shelves are automatically created for you

2. **Add Books**
   - Use the "Add Book" page to add new books to the database
   - Fill in title and author (required)
   - Optionally add ISBN, publisher, year, genre, description, and cover image
   - Supported image formats: JPG, PNG, GIF (max 5MB)

3. **Search for Books**
   - Use the search page to find books by title, author, or ISBN
   - Click on any book to view details

4. **Organize Your Reading**
   - Add books to shelves from the book detail page
   - Track progress on "Currently Reading" books
   - Create custom shelves for different genres or projects

5. **Write Reviews**
   - Rate books from 1-5 stars
   - Add optional text reviews
   - Edit your review anytime

6. **Social Features**
   - Follow other users from the "Find Users" page
   - View activity feed to see what people you follow are reading
   - Visit user profiles to see their shelves and reviews

## Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug's secure password hashing (bcrypt)
- **Session Management**: Secure session handling with Flask sessions
- **Input Validation**: Server-side validation for all user inputs
- **File Upload Security**: File type and size validation for book covers
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Jinja2 template auto-escaping prevents cross-site scripting

## Technical Details

### Backend
- **Framework**: Flask 3.0.0
- **Database**: SQLite (via SQLAlchemy)
- **Authentication**: Werkzeug password hashing + Flask sessions
- **ORM**: Flask-SQLAlchemy

### Frontend
- **Templates**: Jinja2
- **Styling**: Custom CSS (no frameworks)
- **JavaScript**: Vanilla JavaScript (no frameworks)
- **Icons**: Unicode emoji characters (no icon fonts needed)

### Database Schema

**Users Table**
- id, username, email, password_hash, created_at
- Relationships: shelves, reviews, books_added, following/followers

**Books Table**
- id, title, author, isbn, publisher, publication_year, genre, description, cover_image, added_by, created_at
- Relationships: reviews, shelf_entries

**Shelves Table**
- id, name, user_id, is_default, created_at
- Relationships: entries (shelf entries)

**ShelfEntry Table**
- id, shelf_id, book_id, added_at, progress_pages, progress_percent

**Reviews Table**
- id, user_id, book_id, rating, text, created_at
- Constraint: One review per user per book

**Followers Table** (Association)
- follower_id, followed_id

## Configuration

The application uses secure defaults. The secret key is auto-generated, and the database is automatically created on first run.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Kushal Jayaswal  
CMSI 4072 Senior Project II  
Spring 2026
