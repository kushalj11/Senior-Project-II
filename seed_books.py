"""
Seed Database with Sample Books
Run this script once to populate the database with 25 popular books.
Usage: python seed_books.py
"""

from app import app, db
from models import User, Book

def seed_books():
    """Add 25 sample books to the database"""
    
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if a demo user exists, create one if not
        demo_user = User.query.filter_by(username='system').first()
        if not demo_user:
            demo_user = User(username='system', email='system@bookshelf.com')
            demo_user.set_password('system123456')
            db.session.add(demo_user)
            db.session.commit()
            print("Created system user for adding books.")
        
        # Check if books already exist
        existing_books = Book.query.count()
        if existing_books > 0:
            print(f"Database already has {existing_books} books.")
            response = input("Do you want to add more books anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled. No books added.")
                return
        
        # List of 25 popular books with complete details
        # Cover images are automatically loaded from Open Library (free, no API key needed)
        books_data = [
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780061120084',
                'publisher': 'Harper Perennial Modern Classics',
                'publication_year': 1960,
                'genre': 'Fiction',
                'description': 'A gripping tale of racial injustice and childhood innocence in the Depression-era South.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780061120084-L.jpg'
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'publisher': 'Signet Classic',
                'publication_year': 1949,
                'genre': 'Science Fiction',
                'description': 'A dystopian social science fiction novel and cautionary tale about the dangers of totalitarianism.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg'
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'publisher': 'Penguin Classics',
                'publication_year': 1813,
                'genre': 'Romance',
                'description': 'A romantic novel of manners exploring themes of marriage, morality, and misconceptions.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg'
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'publisher': 'Scribner',
                'publication_year': 1925,
                'genre': 'Fiction',
                'description': 'A tragic love story set in the Jazz Age, exploring themes of decadence and idealism.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780743273565-L.jpg'
            },
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'author': 'J.K. Rowling',
                'isbn': '9780747532699',
                'publisher': 'Bloomsbury',
                'publication_year': 1997,
                'genre': 'Fantasy',
                'description': 'A young wizard begins his magical education and discovers his destiny.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780747532699-L.jpg'
            },
            {
                'title': 'Matilda',
                'author': 'Roald Dahl',
                'isbn': '9780142410370',
                'publisher': 'Puffin Books',
                'publication_year': 1988,
                'genre': 'Children\'s Fiction',
                'description': 'An extraordinary girl with a vivid imagination takes a stand to change her story with miraculous results.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780142410370-L.jpg'
            },
            {
                'title': 'The Lord of the Rings',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780544003415',
                'publisher': 'Houghton Mifflin Harcourt',
                'publication_year': 1954,
                'genre': 'Fantasy',
                'description': 'An epic high-fantasy adventure following the quest to destroy the One Ring.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780544003415-L.jpg'
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780547928227',
                'publisher': 'Houghton Mifflin Harcourt',
                'publication_year': 1937,
                'genre': 'Fantasy',
                'description': 'Bilbo Baggins embarks on an unexpected journey with a group of dwarves and a wizard.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780547928227-L.jpg'
            },
            {
                'title': 'Brave New World',
                'author': 'Aldous Huxley',
                'isbn': '9780060850524',
                'publisher': 'Harper Perennial Modern Classics',
                'publication_year': 1932,
                'genre': 'Science Fiction',
                'description': 'A dystopian novel set in a futuristic World State inhabited by genetically modified citizens.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780060850524-L.jpg'
            },
            {
                'title': 'The Chronicles of Narnia',
                'author': 'C.S. Lewis',
                'isbn': '9780066238500',
                'publisher': 'HarperCollins',
                'publication_year': 1950,
                'genre': 'Fantasy',
                'description': 'A series of seven fantasy novels featuring children who find a magical wardrobe.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780066238500-L.jpg'
            },
            {
                'title': 'Jane Eyre',
                'author': 'Charlotte Brontë',
                'isbn': '9780141441146',
                'publisher': 'Penguin Classics',
                'publication_year': 1847,
                'genre': 'Romance',
                'description': 'The story of an orphaned girl who becomes a governess and falls in love with her employer.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141441146-L.jpg'
            },
            {
                'title': 'Animal Farm',
                'author': 'George Orwell',
                'isbn': '9780451526342',
                'publisher': 'Signet Classic',
                'publication_year': 1945,
                'genre': 'Fiction',
                'description': 'An allegorical novella about farm animals who rebel against their human farmer.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780451526342-L.jpg'
            },
            {
                'title': 'The Book Thief',
                'author': 'Markus Zusak',
                'isbn': '9780375842207',
                'publisher': 'Alfred A. Knopf',
                'publication_year': 2005,
                'genre': 'Historical Fiction',
                'description': 'Set in Nazi Germany, narrated by Death, about a young girl who steals books.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780375842207-L.jpg'
            },
            {
                'title': 'Fahrenheit 451',
                'author': 'Ray Bradbury',
                'isbn': '9781451673319',
                'publisher': 'Simon & Schuster',
                'publication_year': 1953,
                'genre': 'Science Fiction',
                'description': 'A dystopian novel about a future American society where books are outlawed.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9781451673319-L.jpg'
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'isbn': '9780061122415',
                'publisher': 'HarperOne',
                'publication_year': 1988,
                'genre': 'Fiction',
                'description': 'A philosophical novel about a young shepherd seeking treasure and finding wisdom.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780061122415-L.jpg'
            },
            {
                'title': 'Anne of Green Gables',
                'author': 'L.M. Montgomery',
                'isbn': '9780553213133',
                'publisher': 'Bantam Classics',
                'publication_year': 1908,
                'genre': 'Classic',
                'description': 'An orphan girl with red hair and a vivid imagination finds a home with an elderly brother and sister.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780553213133-L.jpg'
            },
            {
                'title': 'A Christmas Carol',
                'author': 'Charles Dickens',
                'isbn': '9780486268651',
                'publisher': 'Dover Publications',
                'publication_year': 1843,
                'genre': 'Classic',
                'description': 'The timeless tale of Ebenezer Scrooge and his transformation through visits by three ghosts.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780486268651-L.jpg'
            },
            {
                'title': 'The Secret Garden',
                'author': 'Frances Hodgson Burnett',
                'isbn': '9780141321066',
                'publisher': 'Penguin Classics',
                'publication_year': 1911,
                'genre': 'Classic',
                'description': 'A young orphan discovers a hidden garden and brings it back to life, transforming herself and others.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141321066-L.jpg'
            },
            {
                'title': 'Oliver Twist',
                'author': 'Charles Dickens',
                'isbn': '9780141439747',
                'publisher': 'Penguin Classics',
                'publication_year': 1838,
                'genre': 'Classic',
                'description': 'The story of an orphan boy who escapes the workhouse and falls in with a gang of pickpockets in London.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141439747-L.jpg'
            },
            {
                'title': 'Wuthering Heights',
                'author': 'Emily Brontë',
                'isbn': '9780141439556',
                'publisher': 'Penguin Classics',
                'publication_year': 1847,
                'genre': 'Romance',
                'description': 'A passionate tale of love and revenge on the Yorkshire moors.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141439556-L.jpg'
            },
            {
                'title': 'The Picture of Dorian Gray',
                'author': 'Oscar Wilde',
                'isbn': '9780141439570',
                'publisher': 'Penguin Classics',
                'publication_year': 1890,
                'genre': 'Fiction',
                'description': 'A philosophical novel about a man whose portrait ages while he remains young.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141439570-L.jpg'
            },
            {
                'title': 'Moby-Dick',
                'author': 'Herman Melville',
                'isbn': '9780142437247',
                'publisher': 'Penguin Classics',
                'publication_year': 1851,
                'genre': 'Adventure',
                'description': 'The epic tale of Captain Ahab\'s obsessive quest to hunt the white whale.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780142437247-L.jpg'
            },
            {
                'title': 'Robinson Crusoe',
                'author': 'Daniel Defoe',
                'isbn': '9780141439822',
                'publisher': 'Penguin Classics',
                'publication_year': 1719,
                'genre': 'Adventure',
                'description': 'The classic tale of a shipwrecked sailor who spends 28 years on a remote tropical island.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141439822-L.jpg'
            },
            {
                'title': 'Little Women',
                'author': 'Louisa May Alcott',
                'isbn': '9780147514011',
                'publisher': 'Penguin Classics',
                'publication_year': 1868,
                'genre': 'Fiction',
                'description': 'The story of the four March sisters growing up during the American Civil War.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780147514011-L.jpg'
            },
            {
                'title': 'The Count of Monte Cristo',
                'author': 'Alexandre Dumas',
                'isbn': '9780140449266',
                'publisher': 'Penguin Classics',
                'publication_year': 1844,
                'genre': 'Adventure',
                'description': 'A tale of betrayal, imprisonment, escape, and revenge set in early 19th century France.',
                'cover_image': 'https://covers.openlibrary.org/b/isbn/9780140449266-L.jpg'
            }
        ]
        
        # Add each book to the database
        added_count = 0
        for book_data in books_data:
            # Check if book already exists (by ISBN or title+author)
            existing = Book.query.filter_by(isbn=book_data['isbn']).first()
            if not existing:
                existing = Book.query.filter_by(
                    title=book_data['title'], 
                    author=book_data['author']
                ).first()
            
            if existing:
                print(f"Skipping '{book_data['title']}' - already exists")
                continue
            
            # Create new book
            book = Book(
                title=book_data['title'],
                author=book_data['author'],
                isbn=book_data['isbn'],
                publisher=book_data['publisher'],
                publication_year=book_data['publication_year'],
                genre=book_data['genre'],
                description=book_data['description'],
                cover_image=book_data.get('cover_image'),  # Use .get() to handle books without covers
                added_by=demo_user.id
            )
            db.session.add(book)
            added_count += 1
            print(f"Added: {book_data['title']} by {book_data['author']}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Successfully added {added_count} books to the database!")
        print(f"📚 Total books in database: {Book.query.count()}")
        print("\nYou can now run the application and browse these books.")

if __name__ == '__main__':
    print("=" * 60)
    print("BookShelf - Database Seeding Script")
    print("=" * 60)
    print("\nThis will add 25 classic books to your database.\n")
    
    seed_books()
    
    print("\n" + "=" * 60)
    print("Done! Your BookShelf database is ready to use.")
    print("=" * 60)
