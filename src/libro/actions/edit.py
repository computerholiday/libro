import sqlite3
from libro.utils import get_valid_input, validate_and_convert_date


def edit_book(db, args):
    """Edit a book's review information."""
    try:
        book_id = args.get("id")
        if not book_id:
            print("Error: Book ID is required")
            return

        # First, check if the book exists and get current data
        cursor = db.cursor()
        cursor.execute(
            """SELECT b.id, b.title, b.author, r.date_read, r.rating, r.review
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            WHERE b.id = ?""",
            (book_id,),
        )
        book = cursor.fetchone()

        if not book:
            print(f"No book found with ID {book_id}")
            return

        print(f"\nEditing review for '{book['title']}' by {book['author']}")
        print("\nCurrent values (press Enter to keep current value):")
        
        # Get new values, allowing empty input to keep current values
        date_read = get_valid_input(
            f"Date read [{book['date_read'] or 'Not set'}] (YYYY-MM-DD): ",
            lambda x: validate_and_convert_date(x, "date_read"),
            allow_empty=True,
        )
        if not date_read:
            date_read = book['date_read']

        rating = get_valid_input(
            f"Rating [{book['rating'] or 'Not set'}] (1-5): ",
            allow_empty=True
        )
        if not rating:
            rating = book['rating']

        print(f"Current review:\n{book['review'] or 'No review set'}\n")
        review = get_valid_input(
            "New review (Enter two blank lines to finish, or press Enter to keep current review):",
            allow_empty=True,
            multiline=True
        )
        if not review:
            review = book['review']

        # Update the review in the database
        cursor.execute(
            """UPDATE reviews 
            SET date_read = ?, rating = ?, review = ?
            WHERE book_id = ?""",
            (date_read, rating, review, book_id),
        )

        # If no review exists yet, create one
        if cursor.rowcount == 0:
            cursor.execute(
                """INSERT INTO reviews (book_id, date_read, rating, review)
                VALUES (?, ?, ?, ?)""",
                (book_id, date_read, rating, review),
            )

        db.commit()
        print(f"\nSuccessfully updated review for '{book['title']}'!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}") 