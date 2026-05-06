"""
Database models for BookShelf application
Contains User, Book, Shelf, ShelfEntry, Review, and Follow models
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Association table for user followers (many-to-many)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shelves = db.relationship('Shelf', backref='owner', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    books_added = db.relationship('Book', backref='contributor', lazy=True)
    
    # Following relationship (self-referential many-to-many)
    following = db.relationship(
        'User', 
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        """Follow another user"""
        if not self.is_following(user):
            self.following.append(user)
    
    def unfollow(self, user):
        """Unfollow a user"""
        if self.is_following(user):
            self.following.remove(user)
    
    def is_following(self, user):
        """Check if following a user"""
        return self.following.filter(followers.c.followed_id == user.id).count() > 0
    
    def __repr__(self):
        return f'<User {self.username}>'


class Book(db.Model):
    """Book entry in the database"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    publisher = db.Column(db.String(200), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    pages = db.Column(db.Integer, nullable=True)  # Total page count for progress tracking
    genre = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(300), nullable=True)  # Filename or URL
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='book', lazy=True, cascade='all, delete-orphan')
    shelf_entries = db.relationship('ShelfEntry', backref='book', lazy=True, cascade='all, delete-orphan')
    
    @property
    def average_rating(self):
        """Calculate average rating from all reviews"""
        if not self.reviews:
            return 0
        return sum(r.rating for r in self.reviews) / len(self.reviews)
    
    @property
    def review_count(self):
        """Count total reviews"""
        return len(self.reviews)
    
    def __repr__(self):
        return f'<Book {self.title}>'


class Shelf(db.Model):
    """Reading shelf (Want to Read, Currently Reading, Finished, or custom)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    entries = db.relationship('ShelfEntry', backref='shelf', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Shelf {self.name}>'


class ShelfEntry(db.Model):
    """Individual book entry on a shelf with progress tracking"""
    id = db.Column(db.Integer, primary_key=True)
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelf.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress_pages = db.Column(db.Integer, nullable=True)  # Current page number
    progress_percent = db.Column(db.Integer, nullable=True)  # Or percentage (0-100)
    
    def __repr__(self):
        return f'<ShelfEntry shelf={self.shelf_id} book={self.book_id}>'


class Review(db.Model):
    """Book review with rating and optional text"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one review per user per book
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_review'),)
    
    def __repr__(self):
        return f'<Review user={self.user_id} book={self.book_id} rating={self.rating}>'
