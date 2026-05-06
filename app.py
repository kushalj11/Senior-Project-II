"""
BookShelf - Main Flask Application
A web-based reading management platform
"""

import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from models import db, User, Book, Shelf, ShelfEntry, Review
from datetime import datetime
from sqlalchemy import or_, func

# Initialize Flask app
app = Flask(__name__)
# Auto-generate secret key if not provided via environment variable
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookshelf.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/covers'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Initialize database
db.init_app(app)

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions for book covers
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validate_email(email):
    """Validate email format"""
    return EMAIL_REGEX.match(email) is not None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_user():
    """Get currently logged in user or None"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== Home and Landing ====================

@app.route('/')
def index():
    """Landing page"""
    user = get_current_user()
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(6).all()
    return render_template('index.html', user=user, recent_books=recent_books)


# ==================== Authentication ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        # Username validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html')
        
        if len(username) > 50:
            flash('Username must be less than 50 characters.', 'error')
            return render_template('register.html')
        
        if not username.replace('_', '').isalnum():
            flash('Username can only contain letters, numbers, and underscores.', 'error')
            return render_template('register.html')
        
        # Email validation
        if not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')
        
        # Password validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create default shelves
            default_shelves = ['Want to Read', 'Currently Reading', 'Finished']
            for shelf_name in default_shelves:
                shelf = Shelf(name=shelf_name, user_id=user.id, is_default=True)
                db.session.add(shelf)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ==================== Dashboard ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing shelves and stats"""
    user = get_current_user()
    shelves = Shelf.query.filter_by(user_id=user.id).all()
    
    # Get comprehensive stats
    total_books_read = ShelfEntry.query.join(Shelf).filter(
        Shelf.user_id == user.id,
        Shelf.name == 'Finished'
    ).count()
    
    total_reviews = Review.query.filter_by(user_id=user.id).count()
    
    currently_reading_count = ShelfEntry.query.join(Shelf).filter(
        Shelf.user_id == user.id,
        Shelf.name == 'Currently Reading'
    ).count()
    
    want_to_read_count = ShelfEntry.query.join(Shelf).filter(
        Shelf.user_id == user.id,
        Shelf.name == 'Want to Read'
    ).count()
    
    # Calculate average rating given by user
    user_reviews = Review.query.filter_by(user_id=user.id).all()
    avg_rating = sum(r.rating for r in user_reviews) / len(user_reviews) if user_reviews else 0
    
    # Find favorite genre (most books read in that genre)
    favorite_genre = db.session.query(Book.genre, func.count(Book.id).label('count')).join(
        ShelfEntry, Book.id == ShelfEntry.book_id
    ).join(
        Shelf, ShelfEntry.shelf_id == Shelf.id
    ).filter(
        Shelf.user_id == user.id,
        Shelf.name == 'Finished',
        Book.genre.isnot(None)
    ).group_by(Book.genre).order_by(func.count(Book.id).desc()).first()
    
    favorite_genre_name = favorite_genre[0] if favorite_genre else 'None yet'
    
    # Get recent activity from followed users
    following_ids = [u.id for u in user.following.all()]
    recent_reviews = Review.query.filter(Review.user_id.in_(following_ids)).order_by(
        Review.created_at.desc()
    ).limit(5).all() if following_ids else []
    
    return render_template('dashboard.html', 
                         user=user, 
                         shelves=shelves,
                         total_books_read=total_books_read,
                         total_reviews=total_reviews,
                         currently_reading_count=currently_reading_count,
                         want_to_read_count=want_to_read_count,
                         avg_rating=avg_rating,
                         favorite_genre=favorite_genre_name,
                         recent_reviews=recent_reviews)


# ==================== Book Management ====================

@app.route('/search')
def search():
    """Search for books"""
    user = get_current_user()
    query = request.args.get('q', '').strip()
    
    if query:
        # Case-insensitive search in title, author, and ISBN
        results = Book.query.filter(
            or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%')
            )
        ).all()
    else:
        # Show all books when no search query
        results = Book.query.order_by(Book.title).all()
    
    return render_template('search.html', user=user, query=query, results=results)


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """View book details"""
    user = get_current_user()
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
    
    # Check if current user has reviewed this book
    user_review = None
    user_shelf = None
    if user:
        user_review = Review.query.filter_by(user_id=user.id, book_id=book_id).first()
        # Find which shelf (if any) this book is on
        shelf_entry = ShelfEntry.query.join(Shelf).filter(
            Shelf.user_id == user.id,
            ShelfEntry.book_id == book_id
        ).first()
        if shelf_entry:
            user_shelf = shelf_entry.shelf
    
    return render_template('book_detail.html', 
                         user=user, 
                         book=book, 
                         reviews=reviews,
                         user_review=user_review,
                         user_shelf=user_shelf)


@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def add_book():
    """Add a new book to the database"""
    user = get_current_user()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publication_year = request.form.get('publication_year', '').strip()
        pages = request.form.get('pages', '').strip()
        genre = request.form.get('genre', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validation
        if not title or not author:
            flash('Title and author are required.', 'error')
            return render_template('add_book.html', user=user)
        
        # Check for duplicate books (same title and author, or same ISBN)
        if isbn:
            existing_book = Book.query.filter_by(isbn=isbn).first()
            if existing_book:
                flash(f'A book with ISBN {isbn} already exists: "{existing_book.title}".', 'warning')
                return redirect(url_for('book_detail', book_id=existing_book.id))
        
        # Check by title and author
        existing_book = Book.query.filter(
            func.lower(Book.title) == func.lower(title),
            func.lower(Book.author) == func.lower(author)
        ).first()
        
        if existing_book:
            flash(f'"{title}" by {author} already exists in the database.', 'warning')
            return redirect(url_for('book_detail', book_id=existing_book.id))
        
        # Handle file upload
        cover_filename = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                filename = f"{datetime.now().timestamp()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cover_filename = filename
        
        # Create book
        book = Book(
            title=title,
            author=author,
            isbn=isbn if isbn else None,
            publisher=publisher if publisher else None,
            publication_year=int(publication_year) if publication_year else None,
            pages=int(pages) if pages else None,
            genre=genre if genre else None,
            description=description if description else None,
            cover_image=cover_filename,
            added_by=user.id
        )
        
        db.session.add(book)
        db.session.commit()
        
        flash(f'Book "{title}" added successfully!', 'success')
        return redirect(url_for('book_detail', book_id=book.id))
    
    return render_template('add_book.html', user=user)


# ==================== Shelf Management ====================

@app.route('/shelves')
@login_required
def shelves():
    """View all shelves"""
    user = get_current_user()
    user_shelves = Shelf.query.filter_by(user_id=user.id).all()
    return render_template('shelves.html', user=user, shelves=user_shelves)


@app.route('/shelf/<int:shelf_id>')
@login_required
def shelf_detail(shelf_id):
    """View books on a specific shelf"""
    user = get_current_user()
    shelf = Shelf.query.get_or_404(shelf_id)
    
    # Allow viewing own shelves or other users' shelves (read-only)
    # Only the owner can edit/remove books
    is_owner = (shelf.user_id == user.id)
    
    return render_template('shelf_detail.html', user=user, shelf=shelf, is_owner=is_owner)


@app.route('/shelf/create', methods=['POST'])
@login_required
def create_shelf():
    """Create a new custom shelf"""
    user = get_current_user()
    shelf_name = request.form.get('shelf_name', '').strip()
    
    if not shelf_name:
        flash('Shelf name is required.', 'error')
        return redirect(url_for('shelves'))
    
    # Check if shelf with this name already exists for user
    existing = Shelf.query.filter_by(user_id=user.id, name=shelf_name).first()
    if existing:
        flash('You already have a shelf with that name.', 'error')
        return redirect(url_for('shelves'))
    
    shelf = Shelf(name=shelf_name, user_id=user.id, is_default=False)
    db.session.add(shelf)
    db.session.commit()
    
    flash(f'Shelf "{shelf_name}" created!', 'success')
    return redirect(url_for('shelves'))


@app.route('/shelf/<int:shelf_id>/add_book/<int:book_id>', methods=['POST'])
@login_required
def add_book_to_shelf(shelf_id, book_id):
    """Add a book to a shelf"""
    user = get_current_user()
    shelf = Shelf.query.get_or_404(shelf_id)
    book = Book.query.get_or_404(book_id)
    
    # Ensure user owns this shelf
    if shelf.user_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Check if book already on this shelf
    existing = ShelfEntry.query.filter_by(shelf_id=shelf_id, book_id=book_id).first()
    if existing:
        flash('Book is already on this shelf.', 'info')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Add to shelf
    entry = ShelfEntry(shelf_id=shelf_id, book_id=book_id)
    db.session.add(entry)
    db.session.commit()
    
    flash(f'Added "{book.title}" to {shelf.name}!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))


@app.route('/shelf/entry/<int:entry_id>/remove', methods=['POST'])
@login_required
def remove_from_shelf(entry_id):
    """Remove a book from a shelf"""
    user = get_current_user()
    entry = ShelfEntry.query.get_or_404(entry_id)
    shelf = entry.shelf
    
    # Ensure user owns this shelf
    if shelf.user_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('shelves'))
    
    book_title = entry.book.title
    shelf_name = shelf.name
    
    db.session.delete(entry)
    db.session.commit()
    
    flash(f'Removed "{book_title}" from {shelf_name}.', 'success')
    return redirect(url_for('shelf_detail', shelf_id=shelf.id))


@app.route('/shelf/entry/<int:entry_id>/update_progress', methods=['POST'])
@login_required
def update_progress(entry_id):
    """Update reading progress on a book"""
    user = get_current_user()
    entry = ShelfEntry.query.get_or_404(entry_id)
    shelf = entry.shelf
    
    # Ensure user owns this shelf
    if shelf.user_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('shelves'))
    
    progress_type = request.form.get('progress_type')
    progress_value = request.form.get('progress_value', '').strip()
    
    if progress_value:
        if progress_type == 'pages':
            entry.progress_pages = int(progress_value)
            entry.progress_percent = None
        elif progress_type == 'percent':
            entry.progress_percent = int(progress_value)
            entry.progress_pages = None
        
        db.session.commit()
        flash('Progress updated!', 'success')
    
    return redirect(url_for('shelf_detail', shelf_id=shelf.id))


# ==================== Reviews and Ratings ====================

@app.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    """Add or update a review for a book"""
    user = get_current_user()
    book = Book.query.get_or_404(book_id)
    
    rating = request.form.get('rating')
    text = request.form.get('review_text', '').strip()
    
    if not rating:
        flash('Rating is required.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    rating = int(rating)
    if rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Check if user already reviewed this book
    existing_review = Review.query.filter_by(user_id=user.id, book_id=book_id).first()
    
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.text = text if text else None
        flash('Review updated!', 'success')
    else:
        # Create new review
        review = Review(user_id=user.id, book_id=book_id, rating=rating, text=text if text else None)
        db.session.add(review)
        flash('Review added!', 'success')
    
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book_id))


# ==================== Social Features ====================

@app.route('/users')
@login_required
def users_list():
    """List all users to find and follow"""
    user = get_current_user()
    all_users = User.query.filter(User.id != user.id).all()
    return render_template('users_list.html', user=user, all_users=all_users)


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """View a user's public profile"""
    current_user = get_current_user()
    profile_user = User.query.get_or_404(user_id)
    
    # Get public shelves
    shelves = Shelf.query.filter_by(user_id=profile_user.id).all()
    
    # Get reviews
    reviews = Review.query.filter_by(user_id=profile_user.id).order_by(Review.created_at.desc()).limit(10).all()
    
    # Stats
    total_books_read = ShelfEntry.query.join(Shelf).filter(
        Shelf.user_id == profile_user.id,
        Shelf.name == 'Finished'
    ).count()
    
    follower_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    
    return render_template('user_profile.html', 
                         user=current_user, 
                         profile_user=profile_user,
                         shelves=shelves,
                         reviews=reviews,
                         total_books_read=total_books_read,
                         follower_count=follower_count,
                         following_count=following_count)


@app.route('/user/<int:user_id>/follow', methods=['POST'])
@login_required
def follow_user(user_id):
    """Follow a user"""
    current_user = get_current_user()
    user_to_follow = User.query.get_or_404(user_id)
    
    if current_user.id == user_id:
        flash('You cannot follow yourself.', 'error')
        return redirect(url_for('user_profile', user_id=user_id))
    
    current_user.follow(user_to_follow)
    db.session.commit()
    
    flash(f'You are now following {user_to_follow.username}!', 'success')
    return redirect(url_for('user_profile', user_id=user_id))


@app.route('/user/<int:user_id>/unfollow', methods=['POST'])
@login_required
def unfollow_user(user_id):
    """Unfollow a user"""
    current_user = get_current_user()
    user_to_unfollow = User.query.get_or_404(user_id)
    
    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    
    flash(f'You have unfollowed {user_to_unfollow.username}.', 'info')
    return redirect(url_for('user_profile', user_id=user_id))


@app.route('/activity')
@login_required
def activity_feed():
    """View activity feed from followed users"""
    user = get_current_user()
    
    # Get IDs of users being followed
    following_ids = [u.id for u in user.following.all()]
    
    # Get recent reviews from followed users
    recent_reviews = Review.query.filter(Review.user_id.in_(following_ids)).order_by(
        Review.created_at.desc()
    ).limit(20).all() if following_ids else []
    
    # Get recent shelf additions from followed users
    recent_shelf_entries = ShelfEntry.query.join(Shelf).filter(
        Shelf.user_id.in_(following_ids)
    ).order_by(ShelfEntry.added_at.desc()).limit(20).all() if following_ids else []
    
    # Combine and sort by timestamp
    activities = []
    
    for review in recent_reviews:
        activities.append({
            'type': 'review',
            'user': review.author,
            'book': review.book,
            'rating': review.rating,
            'text': review.text,
            'timestamp': review.created_at
        })
    
    for entry in recent_shelf_entries:
        activities.append({
            'type': 'shelf_add',
            'user': entry.shelf.owner,
            'book': entry.book,
            'shelf': entry.shelf,
            'timestamp': entry.added_at
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:30]  # Limit to 30 most recent
    
    return render_template('activity_feed.html', user=user, activities=activities)


@app.route('/all-activity')
@login_required
def all_activity():
    """View activity feed from ALL users (not just followed)"""
    user = get_current_user()
    
    # Get recent users who joined (new accounts)
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Get recent books added to the database
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(15).all()
    
    # Get recent reviews from ALL users
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(20).all()
    
    # Get recent shelf additions from ALL users
    recent_shelf_entries = ShelfEntry.query.join(Shelf).order_by(
        ShelfEntry.added_at.desc()
    ).limit(20).all()
    
    # Combine and sort by timestamp
    activities = []
    
    # Add new user activities
    for new_user in recent_users:
        activities.append({
            'type': 'new_user',
            'user': new_user,
            'timestamp': new_user.created_at
        })
    
    # Add new book activities
    for book in recent_books:
        activities.append({
            'type': 'new_book',
            'user': book.contributor,
            'book': book,
            'timestamp': book.created_at
        })
    
    # Add review activities
    for review in recent_reviews:
        activities.append({
            'type': 'review',
            'user': review.author,
            'book': review.book,
            'rating': review.rating,
            'text': review.text,
            'timestamp': review.created_at
        })
    
    # Add shelf addition activities
    for entry in recent_shelf_entries:
        activities.append({
            'type': 'shelf_add',
            'user': entry.shelf.owner,
            'book': entry.book,
            'shelf': entry.shelf,
            'timestamp': entry.added_at
        })
    
    # Sort by timestamp (most recent first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:50]  # Limit to 50 most recent activities
    
    return render_template('all_activity.html', user=user, activities=activities)


# ==================== Initialize Database ====================

@app.cli.command()
def initdb():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


# Create tables on first run
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    # Use environment variable to control debug mode (safer for production)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
