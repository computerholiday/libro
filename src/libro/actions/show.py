import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table


def show_books(db, args={}):
    # If id is specified, show book detail
    if args.get("id") is not None:
        show_book_detail(db, args.get("id"))
        return

    # Get the list to show
    list_type = args.get("list", "all")
    year = args.get("year", datetime.now().year)

    if list_type == "current":
        books = get_books_by_status(db, "currently_reading")
        title = "Currently Reading"
    elif list_type == "want":
        books = get_books_by_status(db, "want_to_read")
        title = "Want to Read"
    elif list_type == "finished":
        books = get_books_by_year(db, year)
        title = f"Books Read in {year}"
    else:
        books = get_all_books(db)
        title = "All Books"

    if not books:
        print("No books found.")
        return

    console = Console()
    table = Table(show_header=True, title=title)
    table.add_column("id")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Rating")
    table.add_column("Date Read" if list_type == "finished" else "Status")

    # Sort books by genre (fiction first) and then by date
    sorted_books = sorted(
        books, key=lambda x: (x["genre"] != "fiction", x["date_read"] or "")
    )

    current_genre = None
    for book in sorted_books:
        # Add genre separator if genre changes
        if book["genre"] != current_genre:
            if current_genre is not None:  # Don't add separator before first genre
                table.add_row("", "", "", "", "", style="dim")
            current_genre = book["genre"]
            table.add_row(
                f"[bold]{current_genre.title()}[/bold]",
                "",
                "",
                "",
                "",
                style="bold cyan",
            )

        # Format the date/status column
        if list_type == "finished":
            date_str = book["date_read"]
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    last_column = date_obj.strftime("%b %d, %Y")
                except ValueError:
                    last_column = date_str
            else:
                last_column = ""
        else:
            last_column = book["status"].replace("_", " ").title() if book["status"] else ""

        table.add_row(
            str(book["id"]),
            book["title"],
            book["author"],
            str(book["rating"] or ""),
            last_column,
        )

    console.print(table)


def show_book_detail(db, id):
    cursor = db.cursor()
    cursor.execute(
        """SELECT b.id, b.title, b.author, b.pub_year, b.pages, b.genre,
                  r.rating, r.date_read, r.review, r.status,
                  COUNT(n.id) as note_count
        FROM books b
        LEFT JOIN reviews r ON b.id = r.book_id
        LEFT JOIN reading_notes n ON b.id = n.book_id
        WHERE b.id = ?
        GROUP BY b.id""",
        (id,),
    )
    book = cursor.fetchone()

    if not book:
        print(f"No book found with ID {id}")
        return

    console = Console()
    table = Table(show_header=True, title="Book Details")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    # Map of column names to display names
    fields = [
        ("ID", book["id"]),
        ("Title", book["title"]),
        ("Author", book["author"]),
        ("Publication Year", book["pub_year"]),
        ("Pages", book["pages"]),
        ("Genre", book["genre"]),
        ("Status", book["status"].replace("_", " ").title() if book["status"] else "Not Set"),
        ("Rating", book["rating"]),
        ("Date Read", book["date_read"]),
        ("Reading Notes", f"{book['note_count']} notes" if book['note_count'] > 0 else "No notes"),
        ("My Review", book["review"] or "No review"),
    ]

    for label, value in fields:
        table.add_row(label, str(value) if value is not None else "")

    console.print(table)


def get_books_by_year(db, year):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT b.id, b.title, b.author, b.genre, r.rating, r.date_read, r.status
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            WHERE strftime('%Y', r.date_read) = ? AND r.status = 'finished'
            ORDER BY r.date_read ASC
        """,
            (str(year),),
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_books_by_status(db, status):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT b.id, b.title, b.author, b.genre, r.rating, r.date_read, r.status
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            WHERE r.status = ?
            ORDER BY r.date_read ASC
        """,
            (status,),
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_all_books(db):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT b.id, b.title, b.author, b.genre, r.rating, r.date_read, r.status
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            ORDER BY r.status, r.date_read ASC
        """
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
