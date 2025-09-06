import mysql.connector
from mysql.connector import Error
from flask import flash
from config import DB_CONFIG
import os


def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def init_database():
    """Initialize database and create tables"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234'
        )
        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS ntvhs_portal")
        cursor.execute("USE ntvhs_portal")

        # Create tables for quizzes, activities, and worksheets (same structure)
        tables = ['quizzes', 'activities', 'worksheets']
        for table in tables:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                grade VARCHAR(50) NOT NULL,
                end_date DATETIME NULL,
                upload_link TEXT NOT NULL,
                professor VARCHAR(255) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)

        # Create videos table
        create_videos_table = """
        CREATE TABLE IF NOT EXISTS videos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NULL,
            grade VARCHAR(50) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_size BIGINT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_videos_table)

        # Create library table
        create_library_table = """
        CREATE TABLE IF NOT EXISTS library (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NULL,
            grade VARCHAR(50) NOT NULL,
            pdf_filename VARCHAR(255) NOT NULL,
            picture_filename VARCHAR(255) NULL,
            file_size BIGINT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_library_table)

        connection.commit()
        print("Database and tables created successfully!")

    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# ==================== GENERIC DATABASE FUNCTIONS ====================
def get_all_items(table_name):
    """Generic function to get all items from any table"""
    items = []
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at DESC")
            items = cursor.fetchall()

            # Format datetime fields for display
            for item in items:
                if item['created_at']:
                    item['created_at'] = item['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                if item.get('updated_at'):
                    item['updated_at'] = item['updated_at'].strftime("%Y-%m-%d %H:%M:%S")
                if item.get('end_date'):
                    item['end_date'] = item['end_date'].strftime("%Y-%m-%dT%H:%M")

    except Error as e:
        print(f"Error fetching {table_name}: {e}")
        flash(f'Error loading {table_name} from database', 'error')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return items


def add_item_to_db(table_name, item_data):
    """Generic function to add item to any table"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            insert_query = f"""
            INSERT INTO {table_name} (name, grade, end_date, upload_link, professor)
            VALUES (%s, %s, %s, %s, %s)
            """

            # Handle optional fields
            end_date = item_data['end_date'] if item_data['end_date'] else None
            professor = item_data['professor'] if item_data['professor'] else None

            cursor.execute(insert_query, (
                item_data['name'],
                item_data['grade'],
                end_date,
                item_data['upload_link'],
                professor
            ))

            connection.commit()
            return True

    except Error as e:
        print(f"Error adding to {table_name}: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def get_item_by_id(table_name, item_id):
    """Generic function to get single item by ID from any table"""
    item = None
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (item_id,))
            item = cursor.fetchone()

            if item and item.get('end_date'):
                item['end_date'] = item['end_date'].strftime("%Y-%m-%dT%H:%M")

    except Error as e:
        print(f"Error fetching from {table_name}: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return item


def update_item_in_db(table_name, item_id, item_data):
    """Generic function to update item in any table"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            update_query = f"""
            UPDATE {table_name} 
            SET name = %s, grade = %s, end_date = %s, upload_link = %s, professor = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            # Handle optional fields
            end_date = item_data['end_date'] if item_data['end_date'] else None
            professor = item_data['professor'] if item_data['professor'] else None

            cursor.execute(update_query, (
                item_data['name'],
                item_data['grade'],
                end_date,
                item_data['upload_link'],
                professor,
                item_id
            ))

            connection.commit()
            return True

    except Error as e:
        print(f"Error updating {table_name}: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def delete_item_from_db(table_name, item_id):
    """Generic function to delete item from any table"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (item_id,))
            connection.commit()
            return True

    except Error as e:
        print(f"Error deleting from {table_name}: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def get_items_by_grade(table_name, grade):
    """Generic function to get items filtered by grade (for student access)"""
    items = []
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name} WHERE grade = %s ORDER BY created_at DESC", (grade,))
            items = cursor.fetchall()

            # Format datetime fields for display
            for item in items:
                if item['created_at']:
                    item['created_at'] = item['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                if item.get('end_date'):
                    item['end_date'] = item['end_date'].strftime("%Y-%m-%dT%H:%M")

    except Error as e:
        print(f"Error fetching {table_name} by grade: {e}")
        flash(f'Error loading {table_name} from database', 'error')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return items


# ==================== VIDEO-SPECIFIC FUNCTIONS ====================
def add_video_to_db(video_data):
    """Add new video to database"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO videos (title, description, grade, filename, file_size)
            VALUES (%s, %s, %s, %s, %s)
            """

            description = video_data['description'] if video_data['description'] else None

            cursor.execute(insert_query, (
                video_data['title'],
                description,
                video_data['grade'],
                video_data['filename'],
                video_data['file_size']
            ))

            connection.commit()
            return True

    except Error as e:
        print(f"Error adding video: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def update_video_in_db(video_id, video_data):
    """Update video info in database (not file)"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            update_query = """
            UPDATE videos
            SET title = %s, description = %s, grade = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            description = video_data['description'] if video_data['description'] else None

            cursor.execute(update_query, (
                video_data['title'],
                description,
                video_data['grade'],
                video_id
            ))

            connection.commit()
            return True

    except Error as e:
        print(f"Error updating video: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def delete_video_from_db(video_id):
    """Delete video from database and file system"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)

            # Get video info first
            cursor.execute("SELECT filename FROM videos WHERE id = %s", (video_id,))
            video = cursor.fetchone()

            if video:
                # Delete from database
                cursor.execute("DELETE FROM videos WHERE id = %s", (video_id,))
                connection.commit()

                # Delete file from file system
                try:
                    file_path = os.path.join('static/videos', video['filename'])
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting video file: {e}")

                return True

    except Error as e:
        print(f"Error deleting video: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def get_videos_by_grade(grade):
    """Get videos filtered by grade"""
    return get_items_by_grade('videos', grade)


def search_videos_by_title(title_query):
    """Search videos by title"""
    videos = []
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM videos WHERE title LIKE %s ORDER BY created_at DESC", (f'%{title_query}%',))
            videos = cursor.fetchall()

            # Format datetime fields for display
            for video in videos:
                if video['created_at']:
                    video['created_at'] = video['created_at'].strftime("%Y-%m-%d %H:%M:%S")

    except Error as e:
        print(f"Error searching videos: {e}")
        flash('Error searching videos', 'error')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return videos


# ==================== LIBRARY-SPECIFIC FUNCTIONS ====================
def add_library_book_to_db(book_data):
    """Add new book to library database"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO library (title, description, grade, pdf_filename, picture_filename, file_size)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            description = book_data['description'] if book_data['description'] else None
            picture_filename = book_data.get('picture_filename', None)

            cursor.execute(insert_query, (
                book_data['title'],
                description,
                book_data['grade'],
                book_data['pdf_filename'],
                picture_filename,
                book_data['file_size']
            ))

            connection.commit()
            return True

    except Error as e:
        print(f"Error adding book: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def update_library_book_in_db(book_id, book_data):
    """Update book info in database (not files)"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            update_query = """
            UPDATE library
            SET title = %s, description = %s, grade = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            description = book_data['description'] if book_data['description'] else None

            cursor.execute(update_query, (
                book_data['title'],
                description,
                book_data['grade'],
                book_id
            ))

            connection.commit()
            return True

    except Error as e:
        print(f"Error updating book: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def delete_library_book_from_db(book_id):
    """Delete book from database and file system"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)

            # Get book info first
            cursor.execute("SELECT pdf_filename, picture_filename FROM library WHERE id = %s", (book_id,))
            book = cursor.fetchone()

            if book:
                # Delete from database
                cursor.execute("DELETE FROM library WHERE id = %s", (book_id,))
                connection.commit()

                # Delete files from file system
                try:
                    pdf_path = os.path.join('static/library/pdfs', book['pdf_filename'])
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

                    if book['picture_filename']:
                        picture_path = os.path.join('static/library/pictures', book['picture_filename'])
                        if os.path.exists(picture_path):
                            os.remove(picture_path)
                except Exception as e:
                    print(f"Error deleting book files: {e}")

                return True

    except Error as e:
        print(f"Error deleting book: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def get_library_books_by_grade(grade):
    """Get library books filtered by grade"""
    return get_items_by_grade('library', grade)


def search_library_books_by_title(title_query):
    """Search library books by title"""
    books = []
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM library WHERE title LIKE %s ORDER BY created_at DESC", (f'%{title_query}%',))
            books = cursor.fetchall()

            # Format datetime fields for display
            for book in books:
                if book['created_at']:
                    book['created_at'] = book['created_at'].strftime("%Y-%m-%d %H:%M:%S")

    except Error as e:
        print(f"Error searching books: {e}")
        flash('Error searching books', 'error')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return books