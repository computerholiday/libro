import sqlite3
from libro.utils import get_valid_input


def add_note(db, args):
    """Add a note to a currently reading book."""
    try:
        book_id = args.get("id")
        if not book_id:
            print("Error: Book ID is required")
            return

        # First, check if the book exists and is currently being read
        cursor = db.cursor()
        cursor.execute(
            """SELECT b.id, b.title, b.author, r.status
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            WHERE b.id = ?""",
            (book_id,),
        )
        book = cursor.fetchone()

        if not book:
            print(f"No book found with ID {book_id}")
            return

        if book['status'] != 'currently_reading':
            print(f"'{book['title']}' is not in your currently reading list.")
            print("You can only add notes to books you are currently reading.")
            return

        # Get note details
        print(f"\nAdding note for '{book['title']}' by {book['author']}")
        
        page_number = get_valid_input(
            "Page number (optional): ",
            allow_empty=True
        )
        
        note = get_valid_input(
            "Your note (Enter two blank lines to finish):",
            multiline=True
        )

        # Insert the note
        cursor.execute(
            """INSERT INTO reading_notes (book_id, note, page_number)
            VALUES (?, ?, ?)""",
            (book_id, note, page_number),
        )

        db.commit()
        print(f"\nSuccessfully added note for '{book['title']}'!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def show_notes(db, args):
    """Show notes for a book."""
    try:
        book_id = args.get("id")
        if not book_id:
            print("Error: Book ID is required")
            return

        cursor = db.cursor()
        cursor.execute(
            """SELECT b.title, b.author, n.note, n.date_added, n.page_number
            FROM books b
            JOIN reading_notes n ON b.id = n.book_id
            WHERE b.id = ?
            ORDER BY n.date_added DESC""",
            (book_id,),
        )
        notes = cursor.fetchall()

        if not notes:
            print("No notes found for this book.")
            return

        print(f"\nNotes for '{notes[0]['title']}' by {notes[0]['author']}:")
        print("─" * 60)
        
        for note in notes:
            print(f"Date: {note['date_added']}")
            if note['page_number']:
                print(f"Page: {note['page_number']}")
            print(f"\n{note['note']}\n")
            print("─" * 60)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}") 